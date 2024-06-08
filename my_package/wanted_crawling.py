import time
import datetime

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


# -------------------- 년월일 --------------------
now = datetime.datetime.now()
ymd_name = now.strftime('%Y%m%d')


# -------------------- 크롬 준비 --------------------
options = Options()
options.add_experimental_option("detach", True) # 브라우저 꺼짐 방지

service = Service(excutable_path=ChromeDriverManager().install()) 


# -------------------- 크롤링 함수 --------------------
def wanted_crawling(search_keyword):
    driver = webdriver.Chrome(service=service, options=options)

    url = f'https://www.wanted.co.kr/search?query={search_keyword}&tab=position'
    driver.get(url=url)
    driver.implicitly_wait(2)
    scroll(driver)

    ## 데이터 수집
    config = {
        'link': list(), # 공고 링크
        'title': list(), # 공고 제목
        'company': list(), # 공고 회사
        'jobdesc': list(), # JD 상세 내용
        'skill': list(), # JD 기술 스택/툴
        'due': list(), # JD 마감일
        'workplace': list(), # JD 근무지역
    }

    print(f'\n[{search_keyword}]')

    content_num = driver.find_element(By.XPATH, '//*[@id="search_tabpanel_position"]/div/div[1]/h2').text
    content_num = int(content_num.replace('포지션', '')) # 공고 개수
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

    elem_return_0('공고 링크', config['link'])
    elem_return_0('공고 제목', config['title'])
    elem_return_0('공고 회사', config['company'])


    ## 데이터 수집
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

    elem_return_1('JD 상세 내용', config['jobdesc'])
    elem_return_1('JD 기술 스택/툴', config['skill'])
    elem_return_1('JD 마감일', config['due'])
    elem_return_1('JD 근무지역', config['workplace'])

    driver.close()

    return config