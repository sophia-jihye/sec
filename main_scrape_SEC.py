import os
import pandas as pd
import requests 
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import unicodedata
import re

data_dir = '/media/dmlab/My Passport/DATA/sec'
sp500_filepath = os.path.join(data_dir, '2022-03-02_S&P500_List.csv')
start_date, end_date = '2020-01-01', '2022-09-01'

save_filepath = os.path.join(data_dir, 'Data_2022-03-10.csv')
err_filepath = save_filepath.replace('.csv', '_error.csv')

headers = {
    "User-Agent": "Seoul National University jihyeparkk@snu.ac.kr",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}
def get_soup(url, lxml=False):
    response = requests.get(url, headers=headers)
    time.sleep(0.1) # Current max request rate: 10 requests/second
    if lxml: soup = BeautifulSoup(response.text, "lxml")
    else: soup = BeautifulSoup(response.text, "html.parser")
    return soup

MULTIPLE_SPACES = re.compile(r"\s+")
def clean_content(content):
    content = content.replace('\n', ' ')
    content = unicodedata.normalize("NFKD", content)
    content = MULTIPLE_SPACES.sub(" ", content).strip()
    return content

def get_image_urls(soup, base_url):
    return ['{}/{}'.format(base_url,item['src']) for item in soup.select('img')]

if __name__ == '__main__':
    form_type = "10-K"
    
    
    df = pd.read_csv(sp500_filepath)[['Symbol', 'Security', 'CIK']]
    df.columns = ['Ticker', 'CompanyName', 'CIK']

    ###################
    ### Scrape URLs ###
    ###################
    records, err_records = [], []
    
    for form_type in ['10-K', '10-Q', '8-K']:
        base_url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}&dateb={}&owner=include&count=2000000'
        for (ticker, cik, company_name) in tqdm(df[['Ticker', 'CIK', 'CompanyName']].values):   
            base_url_filled = base_url.format(cik, form_type, end_date.replace('-', ''))
            soup = get_soup(base_url_filled) # ticker or CIK
            try: doc_records = soup.select("#seriesDiv > table.tableFile2 > tr")[1:]
            except:
                print('No files for {} of {}\n {}'.format(form_type, ticker, base_url_filled))
                err_records.append((cik, base_url_filled))
                continue

            for doc_record in doc_records:
                files_url = "https://www.sec.gov" + doc_record.select("a")[0]['href']
                filing_date = doc_record.select("td")[3].text
                if filing_date < start_date:
                    break

                soup = get_soup(files_url)
                period_of_report = soup.select("#formDiv > div.formContent > div > div.info")[-1].text
                form_url = "https://www.sec.gov" + soup.select("#formDiv > div > table > tr > td > a")[0]['href']
                form_url = form_url.replace('ix?doc=/', '') # iXBRL -> HTML

                soup = get_soup(form_url)
                texts_only = soup.get_text()
                texts_only = clean_content(texts_only)
                image_urls = get_image_urls(soup, os.path.dirname(form_url))

                records.append((cik, ticker, company_name, form_type, filing_date, period_of_report, texts_only, image_urls, files_url, form_url))

    df = pd.DataFrame(records, columns=['CIK', 'Ticker', 'CompanyName', 'form_type', 'filing_date', 'period_of_report', 'texts_only', 'image_urls', 'files_url', 'form_url'])
    df.to_csv(save_filepath, index=False)
    print('Created {}'.format(save_filepath))
    
    df = pd.DataFrame(err_records, columns=['CIK', 'url'])
    df.to_csv(err_filepath, index=False)
    print('Created {}'.format(err_filepath))
    