import base64
import requests
from bs4 import BeautifulSoup
import requests.sessions
import re
import routing
import xbmcgui
import xbmcaddon
import xbmc
from xbmcgui import ListItem
import xbmcplugin
from xbmcplugin import addDirectoryItem, endOfDirectory


plugin = routing.Plugin()

s = requests.Session()
base_url = "https://popcorntimes.tv" 
def decodeS1Char(c):
	i = 122
	if c <= "Z":
		i = 90
	j = (ord(c) + 13)
	if i >= j:
		r = j
	else:
		r = j -26
	return chr(r)

def decodeS1(enc):
	decodedS1 = ""
	for c in enc:
		if type(c) is not int:
			if c >= "0" and c <= "9":
				decodedS1 = decodedS1 + c
			else:
				decodedS1 = decodedS1 + decodeS1Char(c)
	return decodedS1

def decode(enc):
	decodedS1 = decodeS1(enc)
	print(decodedS1)
	return base64.b64decode(decodedS1)



def getStream(siteUrl):
	site = s.get(siteUrl)
	match = re.findall(r"PCTMLOC = \"(.*)\"", site.text)
	encoded = match[0]
	print(encoded)
	return "https:" + decode(encoded).decode("utf-8") 


@plugin.route('/')
def root():
	addDirectoryItem(plugin.handle, plugin.url_for(list_movies, "/de/top-filme"), ListItem("Top Filme"), True)	
	addDirectoryItem(plugin.handle, plugin.url_for(list_movies, "/de/neu"), ListItem("Neu im Programm"), True)
	addDirectoryItem(plugin.handle, plugin.url_for(list_gerne), ListItem("Gernes"), True)	
	endOfDirectory(plugin.handle)

@plugin.route('/list_gerne')
def list_gerne():
	req = s.get("https://popcorntimes.tv/de/genres")
	soup = BeautifulSoup(req.text, "html.parser")
	gernes_h3 = soup.find("div", class_ = "pt-bordered-tiles").find_all("h3")
	for h3 in gernes_h3:
		link = h3.find("a");
		addDirectoryItem(plugin.handle, plugin.url_for(list_movies, link.get("href")), ListItem(link.text), True)
		
	endOfDirectory(plugin.handle)
	
@plugin.route('/list_movies/<path:url>')
def list_movies(url):
	req = s.get(base_url + url)
	soup = BeautifulSoup(req.text, "html.parser")
	mov_divs = soup.find_all("div", class_ = "pt-movie-tile-full")
	for div in mov_divs:
		title = div.find("a").find("img").get("alt")
		liz = xbmcgui.ListItem( title)
		img = div.find("a").find("img").get("data-src")
		if img is None:
			img = div.find("a").find("img").get("src")
		liz.setArt({ 'poster': "https:" + img }),
		liz.setProperty('IsPlayable', 'true')
		liz.setInfo('video', {'Title': title})
		mov_url = base_url + div.find("a").get("href")
		addDirectoryItem(plugin.handle, plugin.url_for(play, mov_url), liz)

	endOfDirectory(plugin.handle)


@plugin.route('/play/<path:movie_url>')
def play(movie_url):
	title = movie_url
	liz = xbmcgui.ListItem( 'Hard to Fight', iconImage='', thumbnailImage='')
	streamUrl = getStream(movie_url)
	xbmc.log("sitemurl:" + movie_url, level=xbmc.LOGNOTICE)        	
	xbmc.log("streamurl:" + streamUrl, level=xbmc.LOGNOTICE)        
	fullurl = streamUrl.strip() + "|Referer=" + movie_url.strip()
	liz.setPath(fullurl)
	xbmcplugin.setResolvedUrl(plugin.handle, True, liz)

if __name__ == '__main__':
	plugin.run()

