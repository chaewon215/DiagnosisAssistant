import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import itertools



def gen_transaction(df):
    for i in range(len(df)):
        df.at[i, '증상 키워드'] = df['증상 키워드'][i].replace("[", "").replace("]", "")\
                                                    .replace(" ", "").replace("'", "").split(',')
    symptoms = list(df["증상 키워드"])
    trns_en = TransactionEncoder()
    symptoms_te = trns_en.fit(symptoms).transform(symptoms)
    trns_df = pd.DataFrame(symptoms_te, columns=trns_en.columns_)

    return trns_df


def aprior_func(df, min_sup=0.1):
    trns_df = gen_transaction(df)
    symptoms_sets = apriori(trns_df, min_support=min_sup, use_colnames=True, max_len=15)
    symptoms_sets.sort_values(['support'], ascending=False)
    return symptoms_sets
    

def arm(df, min_sup, save=False):
    symptoms_sets = aprior_func(df, min_sup=min_sup)
    rules = association_rules(symptoms_sets, metric="confidence", min_threshold=0.5)
    if save:
        rules.to_csv('./crowling/rules.csv', index=False)
    rules.sort_values(['confidence'], ascending=False)

    return rules, symptoms_sets


def user_symptoms_subsets(user_symptoms):
    all_subsets = []
    for i in range(len(user_symptoms)):
        all_subsets.extend(list(list(itertools.combinations(user_symptoms, i+1))))
    
    return all_subsets


def extract_keyword_combi(df, user_symptoms):
    all_subsets = user_symptoms_subsets(user_symptoms)
    keyword_combi = pd.DataFrame(columns=["keyword", "support"])
    rules, symptoms_sets = arm(df, min_sup=0.1)
    for i in range(len(symptoms_sets)):
        for subset in all_subsets:
            if set(subset) == (set(symptoms_sets['itemsets'][i])):
                keyword_combi.loc[len(keyword_combi)] = \
                    [list(symptoms_sets['itemsets'][i]), symptoms_sets['support'][i]]
    keyword_combi.sort_values(['support'], ascending=False)

    return rules, keyword_combi


def filtered_rules(rules, keyword_combi):
    
    user_syt_df = pd.DataFrame(columns=rules.columns)
    for i in range(len(keyword_combi)):        
        filtered = rules[rules["antecedents"] == frozenset(keyword_combi["keyword"][i])]
        filtered.sort_values(['support'], ascending=False)
        user_syt_df = pd.concat([user_syt_df, filtered])
    user_syt_df.sort_values(['confidence'], ascending=False)

    return user_syt_df


def left_right_combi(rules, keyword_combi):
    user_syt_df = filtered_rules(rules, keyword_combi)
    item_sets = []
    for i in range(len(user_syt_df)):
        item_sets.append(list(user_syt_df['antecedents'].values[i]) + list(user_syt_df['consequents'].values[i]))
    return item_sets


def match_score(disease, df, user_symptoms):
    import numpy as np
    score = 0
    for i in range(len(df)):
        if df["질환명"][i] == disease:
            length = len(df["증상 키워드"][i])
            
            if set(user_symptoms).issubset(set(df["증상 키워드"][i])):
                score += (len(user_symptoms))
                
            for symptom in user_symptoms:
                
                if symptom in df["증상 키워드"][i]:
                    score += 1
                else:
                    length += 1

    score = (score / length) * 100
    return score


def find_matches(df , user_symptoms, item_sets):
    best_matches = {}
    able_diseases = {}
    able_df_disases = {}

    for i in range(len(df["증상 키워드"])):
        if set(user_symptoms) == set(df["증상 키워드"][i]):
            best_matches[df["질환명"][i]] = match_score(df["질환명"][i], df, user_symptoms)
        else:
            if len(item_sets) != 0:        
                for item_set in item_sets:
                    if set(item_set).issubset(set(df["증상 키워드"][i])):
                        able_diseases[df["질환명"][i]] = match_score(df["질환명"][i], df, user_symptoms)
            else:
                if set(user_symptoms).issubset(set(df["증상 키워드"][i])):
                    able_df_disases[df["질환명"][i]] = match_score(df["질환명"][i], df, user_symptoms)
    return best_matches, able_diseases, able_df_disases


def print_results(df, user_symptoms, item_sets):
    
    best_matches, able_diseases, able_df_disases = find_matches(df, user_symptoms, item_sets)
    results = {}

    if len(best_matches) != 0:
        scores = sorted(list(best_matches.values()), reverse=True)
        for score in scores:
            best = list(best_matches.keys())[list(best_matches.values()).index(score)]
            print(f"입력하신 증상에 대해 가장 적합한 질환은 {best}이며, 일치도는 {score:.2f}% 입니다.")
            results[best] = score
            
    if len(able_diseases) != 0:
        scores = sorted(list(able_diseases.values()), reverse=True)
        for score in scores:
            able = list(able_diseases.keys())[list(able_diseases.values()).index(score)]
            print(f"ARM 기반 입력하신 증상에 대해 가능성 있는 질환은 {able}이며, 일치도는 {score:.2f}% 입니다.")
            results[able] = score
            
    if len(able_df_disases) != 0:
        scores = sorted(list(able_df_disases.values()), reverse=True)
        for score in scores:
            able_df = list(able_df_disases.keys())[list(able_df_disases.values()).index(score)]
            print(f"Dataframe 내 탐색 기반 입력하신 증상에 대해 가능성 있는 질환은 {able_df}, 일치도는 {score:.2f}% 입니다.")
            results[able_df] = score
    print("")
    return results


def sort_results(results):
    sorted_results = []
    if len(results) != 0:
        scores = sorted(list(results.values()), reverse=True)
        for score in scores:
            sorted_results.append(list(results.keys())[list(results.values()).index(score)])
    return sorted_results


def predict_disease(df, user_symptoms, item_sets):
    
    results = print_results(df, user_symptoms, item_sets)
    sorted_results = sort_results(results)
    
    print(f"입력하신 증상은 {user_symptoms} 입니다.")
    print("===================================================================")
    for i in range(3):
        if i < len(sorted_results):
            print(f"{i+1}순위 질환은 {sorted_results[i]}입니다.")
            print(f"{sorted_results[i]}의 증상은 {df[df['질환명'] == sorted_results[i]]['증상 키워드'].values[0]} 입니다.")
            print(f"증상 일치도는 {results[sorted_results[i]]:.2f}% 입니다.")
            print(f"자세한 정보는 아래 링크에서 확인하실 수 있습니다.")
            print(df[df['질환명'] == sorted_results[i]]['URL1'].values[0])
            print(df[df['질환명'] == sorted_results[i]]['URL2'].values[0])
            print("===================================================================")
        else:
            break
    print("")
    return sorted_results


def disease_info(df, sorted_results):
    
    visit = False
    
    desc_input = input("이 질환 중 생활 가이드, 주의사항 등을 알고 싶은 질환명을 입력하세요: ")

    if desc_input not in sorted_results[:3]:
        print("해당 질환은 입력하신 증상과 일치할 확률이 낮습니다.")
        print("")

    cols = ['설명', '주의사항']
    for col in cols:
        
        info = df[df['질환명'] == desc_input][col].values[0]
        if not pd.isna(info) and info != "nan":
            print(f"========={col}=========")
            print(info)

            if "병원" in info or "내원" in info or "응급실" in info:
                visit = True
    
    if visit:
        print("****안내****")
        print(f"{desc_input}은 내원이 요구되는 질환입니다. 빠른 시일 내 병원을 방문해주세요.")
        
            
            
def main():
    df = pd.read_csv('./crowling/merged_crowling_ver_2.csv', encoding='utf-8')
    user_symptoms = input("증상을 입력하세요: ").replace(" ", "").split(",")
    
    
    rules, keyword_combi = extract_keyword_combi(df, user_symptoms)
    item_sets = left_right_combi(rules, keyword_combi)
    
    sorted_results = predict_disease(df, user_symptoms, item_sets)
    disease_info(df, sorted_results)
    
    
if __name__ == "__main__":
    main()