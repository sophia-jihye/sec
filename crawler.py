# This script will download all the 10-K, 10-Q and 8-K
# provided that of company symbol and its cik code.

from bs4 import BeautifulSoup
import re
import requests
import os
import time

class SecCrawler():

	def __init__(self):
		self.hello = "Welcome to SEC Cralwer!"

	def make_directory(self, companyCode, cik, priorto, filing_type):
		# Making the directory to save comapny filings
#		if not os.path.exists("SEC-Edgar-data/"):
#			os.makedirs("SEC-Edgar-data/")
		if not os.path.exists(f"{filing_type}/"):
			os.makedirs(f"{filing_type}/")
#		if not os.path.exists(f"{filing_type}/{companyCode}/"):
#			os.makedirs(f"{filing_type}/{companyCode}/")

#		if not os.path.exists(f"SEC-Edgar-data/{companyCode}/"):
#			os.makedirs(f"SEC-Edgar-data/{companyCode}/")
#		if not os.path.exists(f"SEC-Edgar-data/{companyCode}/{cik}/"):
#			os.makedirs(f"SEC-Edgar-data/{companyCode}/{cik}/")
#		if not os.path.exists(f"SEC-Edgar-data/{companyCode}/{cik}/{filing_type}/"):
#			os.makedirs(f"SEC-Edgar-data/{companyCode}/{cik}/{filing_type}/")

	def save_in_directory(self, companyCode, cik, priorto, docList, docNameList, filing_type):
		# Save every text document into its respective folder
#		for j in range(len(docList)):
		base_url = docList[0]
		print(base_url)
		headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
		r = requests.get(base_url, headers = headers)
		data = r.text

		path = f"{filing_type}/{companyCode}_{str(docNameList[-1])}"
		print(f"saving to {path}")
		filename = open(path,"wb")
		filename.write(data.encode('ascii', 'ignore'))
		time.sleep(0.3)

	def filing_10K(self, companyCode, cik, priorto, count):
		try:
			self.make_directory(companyCode, cik, priorto, '10-K')
		except:
			print("Not able to create directory")

		#generate the url to crawl
		base_url = f"http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb={priorto}&owner=exclude&output=xml&count={count}"
		print(f"started 10-K for code: {companyCode}")
		headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
		r = requests.get(base_url, headers = headers)
		data = r.text

		time.sleep(1)
		soup = BeautifulSoup(data, features = "lxml") # Initializing to crawl again
		linkList=[] # List of all links from the CIK page

		# If the link is .htm convert it to .html
		for link in soup.find_all('filinghref'):
			URL = link.string
			if link.string.split(".")[len(link.string.split("."))-1] == "htm":
				URL += "l"
			linkList.append(URL)

		linkListFinal = linkList

		print(f"Number of files to download : {len(linkListFinal)}")
		print("Start downloading....")

		docList = [] # List of URL to the text documents
		docNameList = [] # List of document names

		for k in range(len(linkListFinal)):
			requiredURL = str(linkListFinal[k])[0:len(linkListFinal[k])-11]
			txtdoc = requiredURL+".txt"
			docname = txtdoc.split("/")[len(txtdoc.split("/"))-1]
			docList.append(txtdoc)
			docNameList.append(docname)


		print(docNameList)
		try:
			self.save_in_directory(companyCode, cik, priorto, docList, docNameList, '10-K')
		except:
			print("Not able to save the file :( ")

		print(f"Successfully downloaded all {len(linkListFinal)} files")


	def filing_10Q(self, companyCode, cik, priorto, count):
		try:
			self.make_directory(companyCode,cik, priorto, '10-Q')
		except:
			print("Not able to create directory")

		#generate the url to crawl
		base_url = f"http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-Q&dateb={priorto}&owner=exclude&output=xml&count={count}"
		print("started 10-Q for code : {companyCode}")
		headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
		r = requests.get(base_url, headers = headers)
		data = r.text

		time.sleep(1)
		soup = BeautifulSoup(data, features = "lxml") # Initializing to crawl again
		linkList=[] # List of all links from the CIK page

		# If the link is .htm convert it to .html
		for link in soup.find_all('filinghref'):
			URL = link.string
			if link.string.split(".")[len(link.string.split("."))-1] == "htm":
				URL += "l"
			linkList.append(URL)

		linkListFinal = linkList

		print(f"Number of files to download: {len(linkListFinal)}")
		print("Start downloading....")

		docList = [] # List of URL to the text documents
		docNameList = [] # List of document names

		# Get all the doc
		for k in range(len(linkListFinal)):
			requiredURL = str(linkListFinal[k])[0:len(linkListFinal[k])-11]
			txtdoc = requiredURL+".txt"
			docname = txtdoc.split("/")[len(txtdoc.split("/"))-1]
			docList.append(txtdoc)
			docNameList.append(docname)

		try:
			self.save_in_directory(companyCode, cik, priorto, docList, docNameList, '10-Q')
		except:
			print("Not able to save the file :( ")

		print(f"Successfully downloaded all {len(linkListFinal)} files")




	def filing_8K(self, companyCode, cik, priorto, count):
		try:
			self.make_directory(companyCode,cik, priorto, '8-K')
		except:
			print("Not able to create directory")

		#generate the url to crawl
		base_url = f"http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=8-K&dateb={priorto}&owner=exclude&output=xml&count={count}"
		print(f"started crawling 8-K code: {companyCode}")
		headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
		r = requests.get(base_url, headers = headers)
		data = r.text

		time.sleep(1)
		soup = BeautifulSoup(data, features = "lxml") # Initializing to crawl again

		linkList=[] # List of all links from the CIK page

		# If the link is .htm convert it to .html
		for link in soup.find_all('filinghref'):
			URL = link.string
			if link.string.split(".")[len(link.string.split("."))-1] == "htm":
				URL += "l"
				linkList.append(URL)

		linkListFinal = linkList

		print(f"Number of files to download {len(linkListFinal)}")
		print("Start downloading....")

		docList = [] # List of URL to the text documents
		docNameList = [] # List of document names

		for k in range(len(linkListFinal)):
			requiredURL = str(linkListFinal[k])[0:len(linkListFinal[k])-11]
			txtdoc = requiredURL+".txt"
			docname = txtdoc.split("/")[len(txtdoc.split("/"))-1]
			docList.append(txtdoc)
			docNameList.append(docname)

		try:
			self.save_in_directory(companyCode, cik, priorto, docList, docNameList, '8-K')
		except:
			print("Not able to save the file :( ")

		print(f"Successfully downloaded all {len(linkListFinal)} files")

	def filing_13F(self, companyCode, cik, priorto, count):
		try:
			self.make_directory(companyCode,cik, priorto, '13-F')
		except:
			print("Not able to create directory")

		#generate the url to crawl
		base_url = f"http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F&dateb={priorto}&owner=exclude&output=xml&count={count}"
		print(f"started 10-Q for code: {companyCode}")
		headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
		r = requests.get(base_url, headers = headers)
		data = r.text

		time.sleep(1)
		soup = BeautifulSoup(data, features = "lxml") # Initializing to crawl again
		linkList=[] # List of all links from the CIK page

		# If the link is .htm convert it to .html
		for link in soup.find_all('filinghref'):
			URL = link.string
			if link.string.split(".")[len(link.string.split("."))-1] == "htm":
				URL += "l"
				linkList.append(URL)

		linkListFinal = linkList

		print(f"Number of files to download {len(linkListFinal)}")
		print("Start downloading....")

		docList = [] # List of URL to the text documents
		docNameList = [] # List of document names

		# Get all the doc
		for k in range(len(linkListFinal)):
			requiredURL = str(linkListFinal[k])[0:len(linkListFinal[k])-11]
			txtdoc = requiredURL+".txt"
			docname = txtdoc.split("/")[len(txtdoc.split("/"))-1]
			docList.append(txtdoc)
			docNameList.append(docname)

		try:
			self.save_in_directory(companyCode, cik, priorto, docList, docNameList, '13-F')
		except:
			print("Not able to save the file :( ")

		print(f"Successfully downloaded all {len(linkListFinal)} files")
