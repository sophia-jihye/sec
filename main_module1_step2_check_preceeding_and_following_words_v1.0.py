import os, re, requests, unicodedata, time
import pandas as pd
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
tqdm.pandas()

from nltk import word_tokenize

root_dir = '/media/dmlab/My Passport/DATA/sec'
scraped_filepath = os.path.join(root_dir, 'Scraped_2022-03-10_20413.csv')

save_filepath = os.path.join(root_dir, 'preceeding_following_words_20413.csv')

headers = {
    "User-Agent": "Seoul National University jihyeparkk@snu.ac.kr",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}
def get_text(link):
    page = requests.get(link, headers=headers)
    time.sleep(0.1) # Current max request rate: 10 requests/second
    html = bs(page.content, "lxml")
    text = html.get_text()
    text = unicodedata.normalize("NFKD", text).encode('ascii', 'ignore').decode('utf8')
    text = text.split("\n")
    text = " ".join(text)
    return text

if __name__ == '__main__':
    df = pd.read_csv(scraped_filepath)
    print('Number of documents={}'.format(len(df)))
    
    item_start = re.compile("item[s]*\s*[1|I]\s*[\.\;\:\-\_\–\|]*\s*\\b", re.IGNORECASE) # Item 1. Business
#     item_end = re.compile("item[s]*\s*1[\.\;\:\-\_\–\(]*a[\)]*\s*[\.\;\:\-\_\–\|]*\s*Risk", re.IGNORECASE) # Item 1a. Risk
    records = []
    for _, row in tqdm(df.iterrows()):
        text = get_text(row['form_url'])
        starts = [i.start() for i in item_start.finditer(text)]
        for start in starts:
            record = [row.CompanyName, row.period_of_report, row.form_url]
            preceeding_10words = word_tokenize(text[start-100:start])[-10:]
            record.extend(preceeding_10words)
            following_10words = word_tokenize(text[start:start+100])[:10]
            record.extend(following_10words)

            records.append(record)

    columns = ['CompanyName', 'period_of_report', 'form_url']
    columns.extend(['word-{}'.format(i) for i in range(10,0,-1)])
    columns.extend(['word+{}'.format(i) for i in range(0,10,1)])
    result_df = pd.DataFrame(records, columns=columns)
    print('Number of rows = {}'.format(len(result_df)))

    result_df.to_csv(save_filepath, index=False)
    print('Created {}'.format(save_filepath))