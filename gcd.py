import re
import requests
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime

print 'Initializing...'
today = datetime.today().strftime("%Y-%m-%d")

myComicsList = ['unbelievable-gwenpool','thanos','secret-empire','amazing-spider-man','infamous-iron-man','mosaic','invincible-iron-man','captain-america-steve-rogers']

#get html from url
def returnHTML(url):
	hdr = {'Accept': 'text/html', 'User-Agent' : "Fiddler"}
	req = urllib2.Request(url, headers=hdr)
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError, e:
		print e.fp.read()
	html = response.read()
	return html

#get inner html from tag
def getTagData(html, tag, classname):
	soup = BeautifulSoup(html, 'html.parser')
	list = soup.find_all(tag, class_=classname)
	return list

#find download link
def downCom(url):
	print "Found " + url
	html = returnHTML(url)
	downButtons = getTagData(html, 'div', 'aio-pulse')
	for button in downButtons:
		if 'zippyshare' in str(button):
			downComZippy(button.a['href'])
	return
	
#just optimizing
def regexNightmare(html, regex):
	urlPattern = re.compile(regex, re.I)
	return urlPattern.search(str(html)).group(1)

#download from zippyshare
def downComZippy(url):
	zippyHTML = returnHTML(url)
	downButton = getTagData(zippyHTML, 'div', 'right')
	
	#disassemble url
	comRawUrl0 = regexNightmare(downButton, '.*?getElementById.*?href = \"(.*?)\"');
	comRawUrl1 = regexNightmare(downButton, '.*?getElementById.*?href = \".*?\" \+ \((.*?)\) \+ \".*?\"\;');
	comRawUrl2 = regexNightmare(downButton, '.*?getElementById.*?href = \".*?\" \+ .*? \+ \"(.*?)\"\;');
	
	#calculating the id and forming url | that is an extremely dirty way, I know
	urlPattern = re.compile('(.*?) \% (.*?) \+ (.*?) \% (.*?)$', re.I)
	urlNum1 = urlPattern.search(str(comRawUrl1)).group(2)
	urlNum2 = urlPattern.search(str(comRawUrl1)).group(3)
	urlNum3 = urlPattern.search(str(comRawUrl1)).group(4)
	urlNumFull = (int(urlNum2) % int(urlNum1)) + (int(urlNum2) % int(urlNum3))
	fullURL = url[:-21] + comRawUrl0 + str(urlNumFull) + comRawUrl2
	
	#download from url & trim it a little bit
	print "Downloading from " + fullURL
	r = requests.get(fullURL, stream=True)
	fileName = comRawUrl2[1:].replace('%20','_').replace('%28','(').replace('%29',')')
	with open('downloaded/' + fileName, 'wb') as f:
		try:
			for block in r.iter_content(1024):
				f.write(block)
		except KeyboardInterrupt:
			pass
	print ('Done\r\n--')
	return
	
#get latest archive on the current page
htmlMain = returnHTML("http://getcomics.info/tag/marvel-now/")
lastPost = getTagData(htmlMain, 'article', 'type-post')[0]

#check if today's archive is there, and retrieve its url
print "Latest weekly post: " + lastPost.time['datetime']
if today in lastPost.time['datetime']:
	print 'There is a new one today. Hurrah!'
else:
	print 'Nothing yet. Exiting...'
	quit()
postUrl = lastPost.h1.a['href']
interm = getTagData(returnHTML(postUrl), 'section', 'post-contents')

#array of new comic books
comList = getTagData(str(interm), 'li', '')
for test in comList:
	try:
		for myComic in myComicsList:
			if myComic in test.strong.a['href']:
				downCom(test.a['href'])
				pass
	except:
		pass
