# Scrape and Parse SEC documents (10-Ks, 10-Qs, 8-Ks)
* Reference
    - https://github.com/rsljr/edgarParser/blob/36db169129d747cc12fc15bb99c1f8a8ec71b0f0/parse_10K.py
    
### main_scrape_SEC.py
* input
    - `start_date` (ex. '2020-01-01')
    - `end_data` (ex. '2022-09-01')
    - List of `('Ticker', 'CompanyName', 'CIK')` (ex. [('MMM', '3M', 66740), ...])
        - Refer to `Check scraped 10-Ks, 10-Qs, 8-Ks.ipynb`
* output
    - Records of `['CIK', 'Ticker', 'CompanyName', 'form_type', 'filing_date', 'period_of_report', 'texts_only', 'image_urls', 'files_url', 'form_url']`
        - Refer to `Check scraped 10-Ks, 10-Qs, 8-Ks.ipynb`
```
# output of main_scrape_SEC.py
CIK: 91142
form_type: 10-K
filing_date: 2022-02-11
period_of_report: 2021-12-31
image_urls: ['https://www.sec.gov/Archives/edgar/data/91142/000009114222000028/aos-20211231_g1.jpg']
files_url: https://www.sec.gov/Archives/edgar/data/91142/000009114222000028/0000091142-22-000028-index.htm
form_url: https://www.sec.gov/Archives/edgar/data/91142/000009114222000028/aos-20211231.htm
Ticker: AOS
CompanyName: A. O. Smith
```

### main_parse_10Ks.py
* input
    - List of `form_url` (ex. ['https://www.sec.gov/Archives/edgar/data/91142/000009114222000028/aos-20211231.htm', ...])
* output
    - Records of `['item1_business', 'item1a_risk', 'item7_mda']`
        - Refer to `Check parsed 10-Ks.ipynb`
* limitation
    - section texts also include `tables`.