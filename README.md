# DiagnosisAssistant
- 2024학년도 1학기 전남대학교 일반대학원 빅데이터분석 수업 프로젝트 레포지토리입니다.  
- 본 서비스는 Association Rule Mining(ARM)을 기반으로 사용자가 입력한 증상과 가장 유사한 증상을 보이는 질환을 반환합니다. 이를 통해 사용자가 내원하지 않고 적은 비용으로 자신의 증상에 대한 질환을 탐색할 수 있도록 합니다.

### 1. Crowling
1. Selenium을 활용하여 [서울대학교 병원](http://www.snuh.org/health/nMedInfo/nList.do?searchNWord=&sortType=A)과 [서울아산병원](https://www.amc.seoul.kr/asan/healthinfo/disease/diseaseSubmain.do)의 데이터를 수집합니다.
2. 수집한 데이터로 데이터프레임을 생성 및 저장합니다.

### 2. Association Rule Mining(ARM) 실행 및 질환 예측
1. Apriori algorithm을 활용하여 transaction에서 minimun support를 만족하는 itemset을 추출합니다.
2. 이를 기반으로 ARM을 수행하여 규칙(rules)을 생성합니다.
3. 사용자의 증상을 입력받고, 그에 대한 모든 subset을 생성합니다.
4. 2.에서 생성된 규칙 중 left hand, 즉 antecedents와 3.의 subset이 일치하는 규칙을 출력합니다.
5. 이 규칙들의 left hand와 right hand를 병합하여 증상 리스트를 생성합니다.
6. 해당 증상들을 포함하는 질환을 dataframe에서 탐색합니다.
7. 이 질환의 증상과 사용자 입력 증상 간의 매칭 점수를 계산하고, 내림차순으로 정렬합니다.
8. Top 3의 질환에 대해 질환명, 질환의 증상, 매칭 점수, url을 출력합니다.
9. 사용자가 질환명을 입력하면, 실생활에서 실천할 수 있는 예방법 또는 주의사항 등을 출력합니다. 만약 내원이 요구되는 질환이라면 안내사항을 함께 출력합니다.


## Presentation Materials
- [**🎨Figma**](https://www.figma.com/file/paLsM5qUkr42vkKYYly9bd/Bigdata-Analysis?type=design&node-id=0%3A1&mode=design&t=aaekYWbXMly8LxES-1)