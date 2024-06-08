import os
import re
import datetime
import numpy as np
import pandas as pd


# -------------------- 함수 모음 -------------------- 
## 조건에 맞는 텍스트 추출
def search_text(left_cond, right_cond, text):
    search = re.search(rf'{left_cond}(.*){right_cond}', text, re.DOTALL)
    if search:
        return search.group(1).strip()
    return np.nan


# -------------------- 년월일 --------------------
now = datetime.datetime.now()
ymd_name = now.strftime('%Y%m%d')


# -------------------- 전처리 함수 --------------------
def wanted_preprocessing(config, search_keyword):

    ## JD 텍스트 추출 및 마감일 텍스트 전처리
    temp = pd.DataFrame({'jobdesc': config['jobdesc'], 'due': config['due']})

    config2 = {
        'intro': list(), # 포지션 상세
        'mainwork': list(), # 주요업무
        'requirement': list(), # 자격요건
        'preferential': list(), # 우대사항
        'benefit': list(), # 혜택 및 복지
    }

    config2['intro'] = temp['jobdesc'].apply(lambda x: search_text('포지션 상세', '주요업무', x))
    config2['mainwork'] = temp['jobdesc'].apply(lambda x: search_text('주요업무', '자격요건', x))
    config2['requirement'] = temp['jobdesc'].apply(lambda x: search_text('자격요건', '우대사항', x))
    config2['preferential'] = temp['jobdesc'].apply(lambda x: search_text('우대사항', '혜택 및 복지', x))
    config2['benefit'] = temp['jobdesc'].apply(lambda x: search_text('혜택 및 복지', '', x))

    config['due'] = temp['due'].apply(lambda x: x.split()[1])

    print('데이터 전처리 완료')

    ## 원시 데이터 저장
    raw_data = {
        'link': config['link'], # 공고 링크
        'title': config['title'], # 공고 제목
        'company': config['company'], # 공고 회사

        'jobdesc': config['jobdesc'], # JD 상세 내용

        'skill': [', '.join(skills) for skills in config['skill']], # JD 기술 스택/툴

        'due': config['due'], # JD 마감일
        'workplace': config['workplace'], # JD 근무지역         
    }
    raw_df = pd.DataFrame(raw_data)
    path = './data/raw'
    os.makedirs(path, exist_ok=True)
    csv_name = f'{path}/{search_keyword}_{ymd_name}.csv'
    raw_df.to_csv(csv_name, index=False, encoding='utf-8-sig')

    print('원시 데이터 저장')


    ## 원천 데이터 저장
    src_data = {
        'link': config['link'], # 공고 링크
        'title': config['title'], # 공고 제목
        'company': config['company'], # 공고 회사

        'intro': config2['intro'], # 포지션 상세,
        'mainwork': config2['mainwork'], # 주요업무
        'requirement': config2['requirement'], # 자격요건
        'preferential': config2['preferential'], # 우대사항
        'benefit': config2['benefit'], # 혜택 및 복지

        'skill': [', '.join(skills) for skills in config['skill']], # JD 기술 스택/툴

        'due': config['due'], # JD 마감일
        'workplace': config['workplace'], # JD 근무지역
    }
    src_df = pd.DataFrame(src_data)
    path = './data/src'
    os.makedirs(path, exist_ok=True)
    csv_name = f'{path}/{search_keyword}_{ymd_name}.csv'
    src_df.to_csv(csv_name, index=False, encoding='utf-8-sig')

    print('원천 데이터 저장')


    ## 라벨링 데이터 저장
    lbl_data = {
        'link': config['link'], # 공고 링크
        'title': config['title'], # 공고 제목
        'company': config['company'], # 공고 회사

        'intro': config2['intro'], # 포지션 상세,
        'mainwork': config2['mainwork'], # 주요업무
        'requirement': config2['requirement'], # 자격요건
        'preferential': config2['preferential'], # 우대사항
        'benefit': config2['benefit'], # 혜택 및 복지

        'skill': [', '.join(skills) for skills in config['skill']], # JD 기술 스택/툴

        'due': config['due'], # JD 마감일
        'workplace': config['workplace'], # JD 근무지역

        'crawl_date': f'{ymd_name}', # 크롤링한 년월일
        'label': f'{search_keyword}', # 키워드
    }
    lbl_df = pd.DataFrame(lbl_data)
    path = './data/lbl'
    os.makedirs(path, exist_ok=True)
    csv_name = f'{path}/{search_keyword}_{ymd_name}.csv'
    lbl_df.to_csv(csv_name, index=False, encoding='utf-8-sig')

    print('라벨링 데이터 저장')