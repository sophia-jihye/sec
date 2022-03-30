# Reference: https://github.com/rsljr/edgarParser
# https://github.com/rsljr/edgarParser/blob/36db169129d747cc12fc15bb99c1f8a8ec71b0f0/parse_10K.py

import os, re, requests, unicodedata, time
import pandas as pd
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
tqdm.pandas()

data_dir = '/media/dmlab/My Passport/DATA/sec'
data_filepath = os.path.join(data_dir, 'Data_2022-03-10.csv')

save_filepath = os.path.join(data_dir, '10K_parsed.csv')

headers = {
    "User-Agent": "Seoul National University jihyeparkk@snu.ac.kr",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

def parse_10k_filing(link, section):
    
    if section not in [0, 1, 2, 3]:
        print("Not a valid section")
        sys.exit()
    
    def get_text(link):
        page = requests.get(link, headers=headers)
        time.sleep(0.1) # Current max request rate: 10 requests/second
        html = bs(page.content, "lxml")
        text = html.get_text()
        text = unicodedata.normalize("NFKD", text).encode('ascii', 'ignore').decode('utf8')
        text = text.split("\n")
        text = " ".join(text)
        return(text)
    
    def extract_text(text, item_start, item_end, median_item_length, min_item_length=7000):
        item_start = item_start
        item_end = item_end
        starts = [i.start() for i in item_start.finditer(text)]
        ends = [i.start() for i in item_end.finditer(text)]
        
        ################### 길이 조건 추가 ###################
        # 최소 길이 조건에 미달하는 텍스트는 제외
        positions = [(s,e) for s in starts for e in ends if e-s>min_item_length]
        
        ################### 길이 조건 추가 ###################
        # median_item_length에 가장 가까운 길이의 텍스트를 최종 추출 텍스트로 선택
        abs_diff = 100000
        item_position = list()
        for p in positions:
            if abs((p[1]-p[0]) - median_item_length) < abs_diff:
                abs_diff = abs((p[1]-p[0]) - median_item_length)
                item_position = p

        item_text = text[item_position[0]:item_position[1]]

        return(item_text)

    text = get_text(link)
        
    if section == 1 or section == 0:
        try:
            item1_start = re.compile("item[s]*\s*[1]\s*[\.\;\:\-\_]*\s*\\b", re.IGNORECASE)
            item1_end = re.compile("item[s]*\s*1a\s*[\.\;\:\-\_]\s*Risk", re.IGNORECASE)
            businessText = extract_text(text, item1_start, item1_end, 40000)
        except:
            businessText = "Something went wrong!"
        
    if section == 2 or section == 0:
        try:
            item1a_start = re.compile("item[s]*\s*1a\s*[\.\;\:\-\_]\s*Risk", re.IGNORECASE)
            item1a_end =re.compile("item[s]*\s*1b\s*[\.\;\:\-\_]\s*Unresolved", re.IGNORECASE)
            riskText = extract_text(text, item1a_start, item1a_end, 57000)
        except:
            riskText = "Something went wrong!"
            
    if section == 3 or section == 0:
        try:
            item7_start = re.compile("item[s]*\s*[7]\s*[\.\;\:\-\_]*\s*\\bM", re.IGNORECASE)
            item7_end = re.compile("item[s]*\s*7a\s*[\.\;\:\-\_]\sQuanti|item\s*8[\.\,\;\:\-\_]\s*", re.IGNORECASE)
            mdaText = extract_text(text, item7_start, item7_end, 75000)
        except:
            mdaText = "Something went wrong!"
    
    ################## Section info #####################
    if section == 0:
        data = [businessText, riskText, mdaText]
    elif section == 1:
        data = [businessText]
    elif section == 2:
        data = [riskText]
    elif section == 3:
        data = [mdaText]
    return(data)

if __name__ == '__main__':
    print('Loading {}..'.format(data_filepath))
    df = pd.read_csv(data_filepath).set_index('form_type').loc['10-K'].reset_index()
    
    records = []
    for url in tqdm(df['form_url'].values):
        item1_business, item1a_risk, item7_mda = parse_10k_filing(url, 0)
        records.append((item1_business, item1a_risk, item7_mda))
    section_df = pd.DataFrame(records, columns=['item1_business', 'item1a_risk', 'item7_mda'])
    
    concat_df = pd.concat([df, section_df], axis=1)
    concat_df.to_csv(save_filepath, index=False)
    print('Created {}'.format(save_filepath))