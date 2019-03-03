
import urllib.request
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
PTT_URL="https://www.ptt.cc"
def get_what_you_want(article):
	global request 
	if article.find(request)>=0:
		return 1
	else:
		return 0


def parse(dom):
	soup=BeautifulSoup(dom,"html.parser")
	#print(soup)
	links=soup.find(id="main-content").find_all("a")
	#print(links)
	img_urls=[]
	for link in links:
		if re.match(r"^https?://(i.)?(m.)?imgur.com",link["href"]):
			img_urls.append(link["href"])
			#print("網址",img_urls)
	return img_urls

def save(img_urls,title):
	#global name
	if img_urls:
		try:
			dname=title.strip()
			os.makedirs(dname)
			for img_url in img_urls:
				if img_url.split("//")[1].startswith("m."):
					img_url=img_url.replace("//m.","//i.")
				if not img_url.split("//")[1].startswith("i."):
					img_url=img_url.split("//")[0]+"//i."+img_url.split("//")[1]
				if not img_url.endswith(".jpg"):
					img_url+=".jpg"
				fname=img_url.split("/")[-1]
				urllib.request.urlretrieve(img_url, os.path.join(dname,fname))
			#os.path.join(request,dname)
		except Exception as e:
			print(e)

def get_web_page(url):
	resp=requests.get(url=url,cookies={"over18":"1"})
	if resp.status_code!=200:
		print("invalid url:",resp.url)
		return None
	else:
		return resp.text

def get_articles(dom,how_much):
	global count
	soup=BeautifulSoup(dom,"html5lib")
	paging_div=soup.find("div","btn-group btn-group-paging")
	prev_url=paging_div.find_all("a")[1]["href"]
	articles=[]
	divs=soup.find_all("div","r-ent")
	for d in divs:
		if get_what_you_want(d.text) and count<how_much :
			count=count+1
			push_count=0
			push_str=d.find("div","nrec").text
			if push_str:
				try:
					push_count=int(push_str)
				except ValueError:
					if push_str=="爆":
						push_count=99
					elif push_str.startswith("X"):
						push_count=-10
			if d.find("a"):
				href=d.find("a")["href"]
				title=d.find("a").text
				author=d.find("div","author").text if d.find("div","author") else ""
				articles.append({"title":title,"href":href,"author":author,"push_count":push_count})
	return articles ,prev_url


request=str(input("想要找的條件"))
#name=str(input("檔名"))
#os.makedirs(name)
current_page=get_web_page("https://www.ptt.cc/bbs/Beauty/search?q="+request)
#request=input("想要找的條件")
how_much=int(input("幾組照片"))
count=0
if current_page:
	articles=[]
	#date=time.strftime("%m/%d").lstrip("0")
	current_articles, prev_url=get_articles(current_page,how_much)
	while current_articles:
		articles+=current_articles
		current_page=get_web_page(PTT_URL+prev_url)
		current_articles ,prev_url=get_articles(current_page,how_much)
	for article in articles:
		print("processing",article)
		page=get_web_page(PTT_URL+article["href"])
		if page:
			img_urls=parse(page)
			save(img_urls,article["title"])
			article["num_image"]=len(img_urls)
	with open("data.json","w",encoding="utf-8") as f:
		json.dump(articles,f,indent=2,sort_keys=True,ensure_ascii=False)
