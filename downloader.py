import os
import re
import json
import ast
import shutil
import requests
import gensim
import pyLDAvis
import pyLDAvis.gensim
import numpy as np
import pandas as pd
from collections import Counter
from sec_edgar_downloader import Downloader
from gensim.utils import simple_preprocess
import gensim.corpora as corpora
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from download.models import MDA, Company
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

#STOP at 20290
#INDEX at 872
base_dir = "C:\\Donkey\\Automation\\FVID"
cik_sp = pd.read_csv('sp500.csv').iloc[:,1]
cik = pd.read_csv('aaer.csv').iloc[:,3]
path = "D:\\Brian\\data\\fraud_true"

# simple word tokenizer
# define stop words + lemmatizer
stop_words = stopwords.words('english')
stop_words.extend(['tr', 'td', 'nbsp', 'div', 'valign', 'nowrap', 'colspan', 'indent', 'noshade',
                   'bgcolor', 'serif', 'inline', 'pt', 'fontsize', 'fontfamily', 'could',
                   'gtltfont', 'roman', 'ltdiv', 'textindent', 'gtamp', 'marginleft', 'marginright', 
                   'bold', 'solid', 'display', 'width', 'right', 'center', 'block', 'colindex', 'br',
                   'textalign', 'fontweight', 'gtltdivgt', 'lttdgt', 'lttrgtlttr', 'borderbottom',
                   'px', 'pagebreak', 'align', 'type', 'left', 'top', 'right', 'color', "style",
                   "font", "arial", "helvetica"])
lemmatizer = WordNetLemmatizer()

def seperator(mda):
    return [lemmatizer.lemmatize(word) for word in simple_preprocess(str(mda), deacc = True) if word not in stop_words]

def generator(year):
    mass = pd.read_csv('export.csv')
    index = [i for i in range(len(mass)) if mass.loc[i, '4'] == year]
    np.random.shuffle(index)
    for row in index:
        yield [mass.loc[row, '0'], mass.loc[row, '1'], mass.loc[row, '2'], mass.loc[row, '3'], mass.loc[row, '4'], seperator(mass.loc[row, '5'])]


# 99, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19
tokenizer = generator(10)
export_tokenize = [i for i in tokenizer]
print(len(export_tokenize))
token_data = [i[5] for i in export_tokenize]

# Create Vocab   
vocabulary = Counter([word for mda in token_data for word in mda])

# Create Dictionary - assign id for each word. filter min count for ALL MDAs 
id2word = corpora.Dictionary(token_data) # assigns token to word
min_count = 100
removal_word_index = {id2word.token2id[word] for word, count in vocabulary.items() if count < min_count}
id2word.filter_tokens(removal_word_index)
id2word.compactify()

# (wordid, frequency) per each mda
corpus = [id2word.doc2bow(text) for text in token_data] # (word id, frequency)

# word and frequency
[[(id2word[index], freq) for index, freq in cp] for cp in corpus[:1]]

lda_model = gensim.models.ldamodel.LdaModel(corpus = corpus,
                                           id2word = id2word,
                                           num_topics = 30, 
                                           random_state = 100,
                                           update_every = 1,
                                           chunksize = 10,
                                           passes = 10,
                                           alpha = 'auto',
                                           per_word_topics = True)

# print topics
lda_model.print_topics()

vis = pyLDAvis.gensim.prepare(lda_model, corpus, id2word)
pyLDAvis.save_html(vis, 'visualize_lda.html')


# form bigram
'''
bigram = gensim.models.Phrases(data_words, min_count = 5, threshold = 100)
bigram_mod = gensim.models.phrases.Phraser(bigram)
def make_bigrams(texts):
    return [bigram_mod[doc] for doc in texts]
data_words_bigrams = make_bigrams(data_words_nostops)
'''

def export_to_csv():
    df = []
    extract = [i for i in MDA.objects.select_related('company').all()]
    
    for index, item in enumerate(extract):
        
        if index % 100 == 0:
            print('extracting: ', index)
        
        row = []    
        row.append(item.company.cik)
        row.append(item.company.fraud)
        row.append(item.company.fraud_year)
        row.append(item.company.industry)
        row.append(item.year)
        row.append(item.mda)
        
        df.append(row)
            
    exported_csv = pd.DataFrame(df)
    exported_csv.to_csv('export.csv')
    print('table exported to csv')


# find overlap
'''
sp = list(set([str(int(i[1:])) for i in cik_sp]))
aaer = [str(i) for i in set(cik)]

len([i for i in sp if i in aaer])

# no overlap in sp500 cik
# 651 overlap in aaer cik
# 135 overlap between sp500 and aaer
'''

def assign_industry():
    sp = [i for i in Company.objects.all()]
    table = pd.read_csv('.\sp500.csv')
    cik = table.iloc[:,1]
    sic = table.iloc[:,2]
    industry = {str(int(i[1:])):j for i,j in zip(cik, sic)}
    
    for comp in sp:
        comp_industry = industry[str(comp.cik)]
        if comp_industry == '[]':
            comp.industry = ''
        else:
            comp.industry = industry[str(comp.cik)]
        comp.save()

def transfer_mda(fraud):
    included = {i.cik:i.cik for i in MDA.objects.all()}
    
    if fraud:
        path = "D:\\Brian\\data\\fraud_true"
        #fiscal_fraud_year = pd.read_csv('aaer.csv')        
    else:
        path = "D:\\Brian\\data\\fraud_false"
    
    cik = os.listdir(os.path.join(path, 'sec_edgar_filings'))
    
    for cik_num in cik:
        if cik_num not in included:
            
            new_company = Company()
            new_company.cik = cik_num
            if fraud:
                new_company.fraud = 'True'
                #new_comapny.fraud_year = 
            else:
                new_company.fraud = 'False'
            new_company.save()                
            
            filing = os.listdir(os.path.join(path, 'sec_edgar_filings', cik_num, '10-K'))
            
            for bs in filing:
                
                new_instance = MDA()
                
                new_instance.company = new_company
                new_instance.year = re.findall('-([0-9]{2})-', bs)[0]
                                    
                with open(os.path.join(path, 'sec_edgar_filings', cik_num, "10-K", bs), 'r') as txt:
                    text = txt.read()
                    new_instance.mda = re.sub(' {1,}', ' ', text)                    
                new_instance.save()    
        else:
            print('cik exists for: ', cik_num)
                
                
def one_to_many(cik):
    return Company.objects.prefetch_related('mda_set').get(cik = cik).mda_set.all()
  
def add_industry(cik):
    sic = []
    for index, cik_num in enumerate(cik):
        print(index)
        url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + str(cik_num)
        text = requests.get(url).text
        reg_search = re.findall('SIC(?:.*?)</a> ?- ?(.*?)<br />State', text)
        try:
            company = reg_search[0]
        except:
            company = reg_search
        sic.append(company)
    
    pd.concat([cik, pd.DataFrame(sic)], axis = 1).to_csv('sp500.csv')

#####################          
#ARCHIVED
#####################

# download from EDGAR 
def batch_download(path, cik): 
    if os.path.exists(path):    
        dl = Downloader(path)
        for index, identifier in enumerate(cik):
            #identifier = identifier[1:] # to include leading zeros
            identifier = (10 - len(str(identifier))) * '0' + str(identifier)# to include leading zeros
            try:
                if os.path.exists(os.path.join(path, 'sec_edgar_filings', str(int(identifier)))):
                    print('File exists for: ', identifier)
                else:
                    print('downloading: ', identifier)
                    dl.get_10k_filings(identifier, include_amends = False)
                    #dl.get_8k_filings(identifier, include_amends=True)
                    #dl.get_10q_filings(identifier, include_amends=True) 
                    extract_mda(path, identifier, '10-K')
            except:
                print('raise exception: ', identifier)
        print('error_case_downloaded - stop at index: ', 0)
    else:
        print('undefined path')
        
def try_regex(mda, identifier, form, file):
    if len(mda) > 0:  
        with open(os.path.join(path, 'sec_edgar_filings', str(int(identifier)), form, file), 'w') as txt_write:
            combined = ''
            for i in mda:
                combined = combined + i + '_seperator_'
            if len(combined) < 200:
                return False            
            txt_write.write(combined)
            txt_write.close()
            return True
    elif len(mda) == 0:
        return False
               
def extract_mda(path, identifier, form): 
    files = os.listdir(os.path.join(path, 'sec_edgar_filings', str(int(identifier)), form))
    for file in files:
        if re.findall('-([0-9]{2})-', file)[0] not in [str(i) for i in range(91, 99)]: # 91 ~ 98            
            if os.path.exists(os.path.join(path, 'sec_edgar_filings', str(int(identifier)), form, file)):
                with open(os.path.join(path, 'sec_edgar_filings', str(int(identifier)), form, file), 'r') as txt:
                    text = txt.read().lower()
                    text = re.sub('(\n|\t| {1,}|nbsp)' ,' ', text)
                    text = re.sub('(</?.*?>|&#x[0-9]{3,4}|\\$bull|rsquo)', '', text)
                    clean = re.sub('[^a-z\"\' ]', '', text)                
                    pattern_text = [
                                    "manage?ment'?s *(?:narrative *analysis|discussion *and *analysis) *of" + "(.*?)" + "(?:consolidated)? *financial *statement[s]? *and *supplement(?:ary|al) *(?:data|information)",
                                    "manage?ment'?s *(?:narrative *analysis|discussion *and *analysis) *of" + "(.*?)" + "change[s]? *in *and *disagreement[s]?",
                                    "manage?ment'?s *(?:narrative *analysis|discussion *and *analysis)" + "(.*?)" + "(?:consolidated)? *financial *statement[s]? *and *supplement(?:ary|al) *(?:data|information)",
                                    "manage?ment'?s *(?:narrative *analysis|discussion *and *analysis)" + "(.*?)" + "change[s]? *in *and *disagreement[s]?"
                                    ]
                    
                    regex_search = []
                    txt.close() 
                for pattern in pattern_text:
                    # ordered by precision -> if match, break loop
                    regex_search.append(try_regex(re.findall(pattern, clean), identifier, form, file))
                    if sum(regex_search) > 0:       
                        break
                if sum(regex_search) == 0:
                    # if no regex match - delete file
                    print('regex mismatch - remove: ', identifier, file)
                    os.remove(os.path.join(path, 'sec_edgar_filings', str(int(identifier)), form, file))               
        else:
            os.remove(os.path.join(path, 'sec_edgar_filings', str(int(identifier)), form, file))
   
# Scrape from SEC AAER
def get_aaer():
    pages = ['/friactions' + str(i) for i in range(1999, 2019)] + [""] #"" for 2019 first html template
    root = "https://www.sec.gov/"
    pattern = r'<a href="(.+)">.+</a></td>(?:\r\n){0,3}<td ?(?:nowrap){0,1}>(.+?)</td>(?:\r\n){0,3}<td ?(?:nowrap){0,1}>(.+?)(?:\r\n){0,3}<br>'
    aaer = []
    for page in pages:
        print('downloading: ', page)
        url = "https://www.sec.gov/divisions/enforce/friactions" + page + ".shtml"        
        text = requests.get(url)
        aaer = aaer + [[(root + d[0]).strip(), d[1].strip(), d[2].strip()] for d in re.findall(pattern, text.text)]
    to_pd = pd.DataFrame(aaer)
    to_pd.to_csv(aaer_csv)
    print('download complete')

# Clean AAER Dataset
class FraudTicker(object):

    def __init__(self):
        self.aaer = pd.read_csv(os.path.join(base_dir, aaer_csv))

    def clean(self, x): 
        x = re.sub('\\,? (inc|llc|llp|ltd|plc|company)\\.?', '', x)
        x = re.sub(' (in)?corp(oration|orated)?', '', x)       
        return x
            
    def correct(self, x):
        x = x.lower()
        x = re.sub('\\,? inc(orporated)?\\.?', ' inc', x)
        x = re.sub('\\,? llc\\.?', ' llc', x)
        x = re.sub('\\,? llp\\.?', ' llp', x)
        x = re.sub('\\,? ltd\\.?', ' ltd', x)
        x = re.sub('\\,? plc\\.?', ' plc', x)  
        x = re.sub('(,? ?(f|n)/k/a ?|;|\\,? and )', ',', x)
        x = re.sub('\\.com', ' com', x)    
        x = re.sub("(et al|\\.| ?\\(.*\\)|')", '', x)
        x = re.sub('&', '%26', x)        
        x = re.sub('(-|the)', ' ', x)  
        return x
    
    def check(self, x):
        for indicator in ['llc', 'inc', 'corp', 'llp', 'ltd', 'plc', 'holding', 'international', 'associates', 'global', '&', 'group', 'company']:
            if indicator in x:
                return True
        return False
    
    def filter_institution(self):     
        accused = self.aaer.loc[:,'accused']
        new_col = []
        ticker = []
        for index, _ in enumerate(accused):
            
            if index%100 == 0:
                print(index)
            
            filtered = [self.clean(i) for i in re.split(', ?', self.correct(accused[index])) if self.check(i)]
            ticker_row = []
            for item in filtered:
                q = '+'.join(item.split())
                url = 'https://www.sec.gov/cgi-bin/browse-edgar?company=' + q + '&owner=exclude&action=getcompany'
                text = requests.get(url)
                cik = [i.strip() for i in list(set(re.findall(r'CIK=([0-9]+)?&amp', text.text)))]
                ticker_row = ticker_row + cik
                                
            ticker.append(ticker_row)     
            new_col.append(filtered)
                        
        if len(self.aaer) == len(new_col) == len(ticker):
            data = pd.concat([self.aaer, pd.Series(new_col), pd.Series(ticker)], axis = 1)
            data.to_csv('aaer_cik.csv')
            return data
        
        def filter_aaer(self):
            data = pd.read_csv(os.path.join(base_dir, 'aaer_cik.csv'))
            finalized = []
            for index in range(len(data)):
                if data.loc[index, '1'] != '[]':
                    first_mention = data.loc[index,'accused']
                    decision = np.where(first_mention == np.array(data.loc[:,'accused']))[0]    
                    decision_by_line = []
                    for sub in decision:
                        url = data.loc[sub,'grounds']
                        text = requests.get(url)
                        # 'allege', 'complaint seek'
                        pattern = ['cease ?-?and ?-?desist',
                                   'revoke', 'registration',
                                   'civil penalty', 'disgorgement', 'enjoin',
                                   'ordered', 'without admitting or denying','settle']            
                        if len(re.findall('\\.html?$', url)) > 0: 
                            file = text.text.lower()
                            for pat in pattern:
                                if len(re.findall(pat, file)) > 0:
                                    decision_by_line.append(pat) 
                        elif len(re.findall('\\.pdf$', url)) > 0:
                            file_raw = text.content                
                            with open(os.path.join(base_dir, "aaer.pdf"), 'wb') as my_data:
                                my_data.write(file_raw)                
                            open_pdf_file = open(os.path.join(base_dir, "aaer.pdf"), 'rb')
                            read_pdf = PyPDF2.PdfFileReader(open_pdf_file)
                            number_of_pages = read_pdf.getNumPages()
                            file = ''
                            for page_number in range(number_of_pages):
                                page = read_pdf.getPage(page_number)
                                page_content = page.extractText()
                                file = file + page_content.lower()
                            for pat in pattern: 
                                if len(re.findall(pat, file)) > 0:
                                    decision_by_line.append(pat) 
                    finalized.append(decision_by_line)
                else:
                    finalized.append('')
            aaer_final = pd.concat([data, pd.Series(finalized)], axis = 1)
            aaer_final.to_csv('aaer_final.csv')
            print('filtered aaer saved')

#fraud_ticker = FraudTicker()
#data = fraud_ticker.filter_aaer()        

# json sp 500
def sort_json():    
    with open(os.path.join('./s&p/sp500_cik.json')) as f:
        sp = json.loads(f.read())
    sp_cik = []
    for i in sp:
        if i['cik'] in sp_cik:
            print(i['cik'])
        sp_cik.append('c' + i['cik'])
    print('all items length: ', len(sp_cik))
    print('unique items length: ', len(set(sp_cik)))
    data = pd.DataFrame(list(set(sp_cik)))
    data.to_csv('cik.csv')

