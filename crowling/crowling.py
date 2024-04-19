import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


# 서울대병원 데이터 크롤링 (http://www.snuh.org/health/nMedInfo/nList.do?searchNWord=&sortType=A)
def snu_crowling(driver, disease, idx, df):
    # 서울대학교 병원 홈페이지
    driver.get('http://www.snuh.org/health/nMedInfo/nList.do?searchNWord=&sortType=A')

    # 검색 버튼 클릭
    search_btn = driver.find_element(By.XPATH, '//*[@id="gnb"]/button[2]')
    search_btn.click()
    time.sleep(1)

    # 검색창에 질병명 입력 및 전송
    search_ipt = driver.find_element(By.XPATH, '//*[@id="totSearchInp"]')
    search_ipt.send_keys(disease)
    search_ipt.send_keys(Keys.RETURN)
    time.sleep(1)

    # 새로 열린 검색 결과 탭으로 이동
    driver.switch_to.window(driver.window_handles[-1])

    # 검색 결과 페이지의 내비게이션 바에서 "건강정보" 클릭
    navi_btn = driver.find_element(By.XPATH, '//*[@id="gnb"]/ul/li[4]/a')
    navi_btn.click()
    time.sleep(1)
    
    more_btn = driver.find_element(By.XPATH, '//*[@id="content"]/div[3]/a')
    more_btn.click()
    time.sleep(1)
    
    sort_acc = driver.find_element(By.XPATH, '//*[@id="rank"]')
    sort_acc.click()
    time.sleep(1)
    
    results_list = driver.find_element(By.CLASS_NAME, 'thumbType02').find_elements(By.CLASS_NAME, 'item')
    elem_list = []
    title_list = []
    for result in results_list:
        elem_list.append(result.find_element(By.TAG_NAME, 'strong'))
        title_list.append(result.find_element(By.TAG_NAME, 'strong').text.replace(" ", ""))
    
    best = []
    for title in title_list:
        if '[N의학정보]' + disease.replace(" ", "") in title:
            best.insert(0, title_list.index(title))
        elif '[N의학정보]' in title and disease.replace(" ", "") in title:
            best.append(title_list.index(title))
        
    elem_list[best[0]].click()
        

    # 새로 열린 질환 세부 정보 페이지로 이동
    driver.switch_to.window(driver.window_handles[-1])
    
    
    # 질환 세부 정보 페이지의 목차
    contents = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[3]/div[1]/div/ul').find_elements(By.TAG_NAME, 'li')
    contents = [content.text for content in contents]
    
    
    # 질환 세부 정보 페이지의 목차와 xpath를 매칭
    xpath_dict = dict.fromkeys(contents)
    
    for i in range(len(contents)):
        xpath_dict[contents[i]] = f'//*[@id="content"]/div[2]/div[3]/div[2]/div[{i+1}]/p'
    

    cols = list(df.columns)
    # ['질환명', '영문명', '증상 키워드', '정의', '증상', '원인', '관련신체기관',
    #                            '진단', '검사', '치료', '경과/합병증', '생활가이드', 'URL']
    
    
    # 질환명은 따로 수집하여, 파싱을 통해 국문명과 영문명을 추출
    name = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/h3').text
    kr_name = name.split('\n')[0]
    en_name = name.split('\n')[1].replace('[','').replace(']','')   
    df.loc[idx, '질환명'] = kr_name
    df.loc[idx, '영문명'] = en_name
    
    
    # 증상 키워드 수집
    df.loc[idx, '증상 키워드'] = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[2]/div[4]/p').text
    
    
    # 질환 세부 정보 수집
    err_list = []
    try:
        for info, xpath in xpath_dict.items():
            if info in cols:
                df.loc[idx, info] = driver.find_element(By.XPATH, xpath).text
            else:
                df.insert(len(df.columns), info, None)
                df.loc[idx, info] = driver.find_element(By.XPATH, xpath).text            
    except:
        err_list.append(info)
            

    # URL 수집
    df.loc[idx, 'URL'] = driver.current_url
    
    if len(err_list) != 0:
        print(f"Error: '{disease}'의 '{err_list}' 정보 수집 실패")
    else:
        print(f"'{disease}'의 정보 수집 완료")
    driver.close()


def make_snu_df(driver, diseases, save=False):
    snu_df = pd.DataFrame(columns=['질환명', '영문명', '증상 키워드', '정의', '증상', '원인', '관련신체기관',
                                '진단', '검사', '치료', '경과/합병증', '생활가이드', 'URL'])
    for idx in range(len(diseases)):
        disease = diseases[idx]
        snu_crowling(driver, disease, idx, snu_df)
    if save:
        snu_df.to_csv('snuh_crowling_ver_2.csv', index=False, encoding='utf-8-sig')
    return snu_df


# ### 서울아산병원 데이터 크롤링 (https://www.amc.seoul.kr/asan/healthinfo/disease/diseaseSubmain.do)
def asan_crowling(driver, disease, disease_en, idx, df):
    # 서울아산병원 홈페이지
    driver.get('https://www.amc.seoul.kr/asan/healthinfo/disease/diseaseSubmain.do')

    search_ipt = driver.find_element(By.XPATH, '//*[@id="regionSrc"]')
    search_ipt.send_keys(disease)
    search_ipt.send_keys(Keys.RETURN)
    time.sleep(1)
    
    
    
    if "없습니다" in driver.find_element(By.CLASS_NAME, 'listCont').text:
        search_ipt = driver.find_element(By.XPATH, '//*[@id="regionSrc"]')
        search_ipt.clear()
        search_ipt.send_keys(disease_en)
        search_ipt.send_keys(Keys.RETURN)
        time.sleep(1)


    results_list = driver.find_element(By.CLASS_NAME, 'descBox').find_elements(By.TAG_NAME, 'li')
    elem_list = []
    title_list = []
    syn_list = []
    for result in results_list:
        title_space = result.find_element(By.CLASS_NAME, 'contTitle')
        elem_list.append(title_space.find_element(By.TAG_NAME, 'a'))
        title_list.append(title_space.find_element(By.TAG_NAME, 'a').text.replace(" ", "").split('(')[0])
        title_space = driver.find_element(By.CLASS_NAME, 'contBox').find_elements(By.TAG_NAME, 'dd')

        if len(title_space) == 4:
            syn_list.append(result.find_element(By.CSS_SELECTOR, 'dd:nth-child(8)').text.replace(" ", '').split(','))
        else:
            syn_list.append([""])

    best = []
    for i in range(len(title_list)):
        title = title_list[i]
        syn = syn_list[i]            
            
        if disease.replace(" ", "") == title:
            best.insert(0, title_list.index(title))
        elif disease.replace(" ", "") in syn:
            best.insert(0, title_list.index(title))
        elif disease.replace(" ", "") in title:
            best.append(title_list.index(title))

        
    elem_list[best[0]].click()


    description = driver.find_element(By.CLASS_NAME, 'descDl').find_elements(By.TAG_NAME, 'dt')
    desc_list = [desc.text for desc in description]

    # 질환 세부 정보 페이지의 목차와 xpath를 매칭
    xpath_dict = dict.fromkeys(desc_list)
    
    for i in range(len(desc_list)):
        xpath_dict[desc_list[i]] = f'//*[@id="content"]/div[2]/div[1]/div[2]/dl/dd[{i+1}]'
        
    cols = list(df.columns)



    # 질환명은 따로 수집하여, 파싱을 통해 국문명과 영문명을 추출
    name = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/ul/li/div[2]/strong').text
    kr_name = name.split('(')[0]
    en_name = name.split('(')[1].replace(')','')
    df.loc[idx, '질환명'] = kr_name
    df.loc[idx, '영문명'] = en_name


    # 동의어 수집
    df.loc[idx, '동의어'] = str(driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/ul/li/div[2]/dl/dd[4]').text.split(','))
    

    # 증상 키워드 수집
    df.loc[idx, '증상 키워드'] = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/div[1]/ul/li/div[2]/dl/dd[1]').text
    
    
    # 질환 세부 정보 수집
    err_list = []
    try:
        for info, xpath in xpath_dict.items():
            if info in cols:
                df.loc[idx, info] = driver.find_element(By.XPATH, xpath).text
            else:
                df.insert(len(df.columns), info, None)
                df.loc[idx, info] = driver.find_element(By.XPATH, xpath).text            
    except:
        err_list.append(info)
    
    # URL 수집
    df.loc[idx, 'URL'] = driver.current_url

    if len(err_list) != 0:
        print(f"Error: '{disease}'의 '{err_list}' 정보 수집 실패")
    else:
        print(f"'{disease}'의 정보 수집 완료")
    driver.close()


def make_asan_df(driver, save=False):
    snu_df = pd.read_csv('snuh_crowling.csv')
    disease_kr = snu_df['질환명'].tolist()
    disease_en = snu_df['영문명'].tolist()
    disease_dict = dict.fromkeys(disease_kr)
    for i in range(len(disease_kr)):
        disease_dict[disease_kr[i]] = disease_en[i]
        
    # 질환 20개 리스트
    diseases = disease_kr

    asan_df = pd.DataFrame(columns=['질환명', '영문명', '동의어', '증상 키워드', '정의', '증상', '원인', '진단', '치료', '경과', '주의사항', 'URL'])

    for idx in range(len(diseases)):
        disease = diseases[idx]
        asan_crowling(driver, disease, disease_dict[disease], idx, asan_df)

    if save:
        asan_df.to_csv('asan_crowling_ver_2.csv', index=False, encoding='utf-8-sig')
        
    return asan_df



def main():
    chrome_option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_option)
    
    # 질환 20개 리스트
    diseases = ['과민성 대장 증후군', '당뇨병', '심부전', '천식', '급성대장염',
                '감기', '급성 경막하 출혈', '인플루엔자', '긴장성 두통', '고산병',
                '아나필락시스', '루게릭병', '장폐색', '아토피 피부염', '대상포진',
                '돌발성 난청', '만성 비염', '신우신염', '뇌전증', '패혈증']
    
    make_snu_df(driver, diseases, save=True)
    make_asan_df(driver, save=True)


if __name__ == '__main__':
    main()