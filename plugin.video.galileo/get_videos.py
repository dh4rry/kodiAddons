from bs4 import BeautifulSoup
import urllib
import urllib2
from urlparse import parse_qsl
import urlparse

def geturl(url,data="x",header=""):
    print("Get Url: " +url)

    opener = urllib2.build_opener()           
    userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
    if header=="":
        opener.addheaders = [('User-Agent', userAgent)]        
    else:
        opener.addheaders = header        
    try:
        if data!="x" :
            content=opener.open(url,data=data).read()
        else:
            content=opener.open(url).read()
    except urllib2.HTTPError as e:
            cc=e.read()  
            debug("Error : " +cc)
    
    opener.close()
    return content



html_doc = geturl('https://www.galileo.tv/video-typ/episode/')
soup = BeautifulSoup(html_doc, 'html.parser')
items = soup.find_all("div", class_="item")
print( items[0] )