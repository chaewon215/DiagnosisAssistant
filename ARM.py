import pandas as pd
from utils import *

def main():
    df = pd.read_csv('./crowling/merged_crowling_ver_3.csv', encoding='utf-8')
    user_symptoms = input("증상을 입력하세요: ").replace(" ", "").split(",")
    
    
    rules, keyword_combi = extract_keyword_combi(df, user_symptoms)
    item_sets = left_right_combi(rules, keyword_combi)
    
    sorted_results = predict_disease(df, user_symptoms, item_sets)
    disease_info(df, sorted_results)
    
    
if __name__ == "__main__":
    main()