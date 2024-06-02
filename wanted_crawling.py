import os
import re
import time
import pandas as pd

from tqdm import tqdm

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By


# -------------------- 함수 모음 -------------------- 
## 스크롤 끝까지
def scroll(driver):
    scroll_location = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        time.sleep(2)
        scroll_height = driver.execute_script('return document.body.scrollHeight')
        if scroll_location == scroll_height:
            break
        else:
            scroll_location = driver.execute_script('return document.body.scrollHeight')
    driver.implicitly_wait(3)


## 스크롤 한 번만
def scroll_one(driver):
    driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
    time.sleep(1)
    driver.implicitly_wait(3)


## 수집명, 수집 개수, 첫번째 값 반환
def elem_return_0(Name, List):
    print(f'{Name} {len(List)} {List[0]}')


## 수집명, 수집 개수 반환
def elem_return_1(Name, List):
    print(f'{Name} {len(List)}')


## 조건에 맞는 텍스트 추출
def match_text(left_cond, right_cond, text):
    text = text
    search = re.search(rf'{left_cond}(.*){right_cond}', text, re.DOTALL)
    if search:
        search = search.group(1).strip()
    return search


# -------------------- 크롤링 함수 -------------------- 
chrome_options = Options()
chrome_options.add_experimental_option("detach", True) # 브라우저 꺼짐 방지

service = Service(excutable_path=ChromeDriverManager().install()) 


def wanted_crawling(search_keyword):
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f'https://www.wanted.co.kr/search?query={search_keyword}&tab=position'
    driver.get(url=url)
    driver.implicitly_wait(2)
    scroll(driver)

    # 데이터 수집 config
    config = {
        'link': list(), # 공고 링크
        'title': list(), # 공고 제목
        'company': list(), # 공고 회사
        'jobdesc': list(), # JD 상세 내용
        'skill': list(), # JD 기술 스택/툴
        'due': list(), # JD 마감일
        'workplace': list(), # JD 근무지역
    }

    # 검색 키워드 출력
    print(f'\n\n##### {search_keyword} #####')

    # 공고 개수
    content_num = driver.find_element(By.XPATH, '//*[@id="search_tabpanel_position"]/div/div[1]/h2').text
    content_num = int(content_num.replace('포지션', ''))
    for i in tqdm(range(1, content_num+1)):
        try:
            p_0 = driver.find_element(By.XPATH, f'//*[@id="search_tabpanel_position"]/div/div[3]/div[{i}]/a').get_attribute('href')
            config['link'].append(p_0)
            
            p_1 = driver.find_element(By.XPATH, f'//*[@id="search_tabpanel_position"]/div/div[3]/div[{i}]/a/div[2]/strong').text
            config['title'].append(p_1)
            
            p_2 = driver.find_element(By.XPATH, f'//*[@id="search_tabpanel_position"]/div/div[3]/div[{i}]/a/div[2]/span[1]').text
            config['company'].append(p_2)                                        
        except Exception as e:
            print(e)
            break

    # 데이터 출력
    elem_return_0('공고 링크', config['link'])
    elem_return_0('공고 제목', config['title'])
    elem_return_0('공고 회사', config['company'])


    for i in tqdm(range(content_num)):
        driver.get(config['link'][i])
        scroll_one(driver)
        time.sleep(1)
        execute = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div/section/section/article[1]/div/button')
        driver.execute_script("arguments[0].click();", execute)
        time.sleep(1)

        try:
            p_3 = driver.find_element(By.CLASS_NAME, 'JobDescription_JobDescription__VWfcb').text
            config['jobdesc'].append(p_3)
            
            skill_elems = driver.find_elements(By.CLASS_NAME, 'SkillTagItem_SkillTagItem__JC2VO')
            p_4 = [elem.text for elem in skill_elems]
            config['skill'].append(p_4)
            
            p_5 = driver.find_element(By.CLASS_NAME, 'JobDueTime_JobDueTime__iKbEO').text
            config['due'].append(p_5)
            
            p_6 = driver.find_element(By.CLASS_NAME, 'JobWorkPlace_JobWorkPlace__map__location__Jksjp').text
            config['workplace'].append(p_6)
        except Exception as e:
            print(e)
            break

    driver.close()

    # 데이터 출력
    elem_return_1('JD 상세 내용', config['jobdesc'])
    elem_return_1('JD 기술 스택/툴', config['skill'])
    elem_return_1('JD 마감일', config['due'])
    elem_return_1('JD 근무지역', config['workplace'])

    return config


# -------------------- 크롤링 실행 -------------------- 
search_keywords = ['LLM', 'NLP'] # 수집할 채용공고의 직무
for search_keyword in search_keywords:
    config = wanted_crawling(search_keyword)


    ## JD 텍스트 추출 및 마감일 텍스트 전처리
    temp = pd.DataFrame({'jobdesc': config['jobdesc'], 'due': config['due']})

    config2 = {
        'mainwork': list(), # 주요업무
        'requirement': list(), # 자격요건
        'preferential': list(), # 우대사항

        'intro': list(), # 포지션 상세,
        'benefit': list(), # 혜택 및 복지
    }

    config2['mainwork'] = temp['jobdesc'].apply(lambda x: match_text('주요업무', '자격요건', x))
    config2['requirement'] = temp['jobdesc'].apply(lambda x: match_text('자격요건', '우대사항', x))
    config2['preferential'] = temp['jobdesc'].apply(lambda x: match_text('우대사항', '혜택 및 복지', x))

    config2['intro'] = temp['jobdesc'].apply(lambda x: match_text('포지션 상세', '주요업무', x))
    config2['benefit'] = temp['jobdesc'].apply(lambda x: match_text('혜택 및 복지', '', x))

    config['due'] = temp['due'].apply(lambda x: x.split()[1])


    ## 데이터프레임 생성 및 저장
    data = {
        'link': config['link'], # 공고 링크
        'title': config['title'], # 공고 제목
        'company': config['company'], # 공고 회사
        'mainwork': config2['mainwork'], # 주요업무
        'requirement': config2['requirement'], # 자격요건
        'preferential': config2['preferential'], # 우대사항
        'skill': [', '.join(skills) for skills in config['skill']], # JD 기술 스택/툴
        'due': config['due'], # JD 마감일
        'workplace': config['workplace'], # JD 근무지역
        
        'intro': config2['intro'], # 포지션 상세,
        'benefit': config2['benefit'], # 혜택 및 복지
        # 'jobdesc': config['jobdesc'], # JD 상세 내용
        'label': f'{search_keyword}'

    }

    df = pd.DataFrame(data)
    csv_name = f'./data/{search_keyword}.csv'
    df.to_csv(csv_name, index=False, encoding='utf-8-sig')


# -------------------- 데이터프레임 병합 --------------------
directory_path = './data'
all_files = os.listdir(directory_path)
csv_files = [file for file in all_files if file.endswith('.csv')]

dataframes = []
for csv_file in csv_files:
    file_path = os.path.join(directory_path, csv_file)
    df = pd.read_csv(file_path)
    dataframes.append(df)

concat_df = pd.concat(dataframes, ignore_index=True)
save_path = os.path.join(directory_path, 'final_data.csv')
concat_df.to_csv(save_path, index=False, encoding='utf-8-sig')