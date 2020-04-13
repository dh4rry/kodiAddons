import base64
import requests
from bs4 import BeautifulSoup
import requests.sessions
import re
import xbmcgui
import xbmcaddon
import xbmc
from xbmcgui import ListItem
import xbmcplugin
from xbmcplugin import addDirectoryItem, endOfDirectory
from urllib import urlencode
from urlparse import parse_qsl

_url = sys.argv[0]
_handle = int(sys.argv[1])

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
	if len(match) < 1:
		dialog = xbmcgui.Dialog()
		soup = BeautifulSoup(site.text, "html.parser")
		sorry = soup.find('h3', text='Es tut uns leid...' )		
		if sorry is None:
			dialog.notification('Fehler', 'Stream konnte nicht ermittelt werden', xbmcgui.NOTIFICATION_ERROR, 5000)		
		else:
			dialog.notification('Nicht verfuegbar', "Film nicht mehr verfuegbar", xbmcgui.NOTIFICATION_WARNING, 5000)
			
	else:
		encoded = match[0]
		xbmc.log("encoded:" + encoded, level=xbmc.LOGNOTICE)
		return "https:" + decode(encoded).decode("utf-8") 


def root():
	addDirectoryItem(_handle, get_url(action='listing', url="/de/top-filme"), ListItem("Top Filme"), True)	
	addDirectoryItem(_handle, get_url(action='listing', url="/de/neu"), ListItem("Neu im Programm"), True)
	addDirectoryItem(_handle, get_url(action='genre'), ListItem("Genres"), True)	
	endOfDirectory(_handle)


def list_genre():
	req = s.get("https://popcorntimes.tv/de/genres")
	soup = BeautifulSoup(req.text, "html.parser")
	genres_h3 = soup.find("div", class_ = "pt-bordered-tiles").find_all("h3")
	for h3 in genres_h3:
		link = h3.find("a");
		addDirectoryItem(_handle, get_url(action='listing', url=link.get("href")), ListItem(link.text), True)
		
	endOfDirectory(_handle)
	

def list_movies(url):
	xbmcplugin.setContent(_handle, 'Movies')
	req = s.get(base_url + url)
	soup = BeautifulSoup(req.text, "html.parser")
	mov_divs = soup.find_all("div", class_ = "pt-movie-tile-full")
	for div in mov_divs:
		if div.find("a") is not None:
			title = div.find("a").find("img").get("alt")
			liz = xbmcgui.ListItem( title)
			year = ""			
			plot = ""
			if div.find("p", class_ = "pt-tile-desc") is not None:			
				plot = div.find("p", class_ = "pt-tile-desc").text
			if div.find("p", attrs={'class': None}) is not None:			
				plot = div.find("p", attrs={'class': None}).text
			
			if div.find("p", class_ = "pt-video-time") is not None:			
				year = div.find("p", class_ = "pt-video-time").text.split('|',1)[0].strip()
			try:
				year = int(year)
			except:
				year = None
			img = div.find("a").find("img").get("data-src")
			if img is None:
				img = div.find("a").find("img").get("src")
			liz.setArt({ 'poster': "https:" + img }),
			liz.setProperty('IsPlayable', 'true')
			liz.setInfo('video', {'Title': title, 'Plot': plot, 'Year': year })
			mov_url = base_url + div.find("a").get("href")
			addDirectoryItem(_handle, get_url(action='play', url=mov_url), liz, False)

	endOfDirectory(_handle)
	xbmcplugin.setContent(_handle, 'Movies')

def play(movie_url):
	title = movie_url
	liz = xbmcgui.ListItem( '', iconImage='', thumbnailImage='')
	streamUrl = getStream(movie_url)
	if streamUrl: 
		fullurl = streamUrl.strip() + "|Referer=" + movie_url.strip()
		liz.setPath(fullurl)
		xbmcplugin.setResolvedUrl(_handle, True, liz)
	#else:
		#xbmcplugin.setResolvedUrl(_handle, False, liz)
	
def get_url(**kwargs):
	"""
	Create a URL for calling the plugin recursively from the given set of keyword arguments.
	:param kwargs: "argument=value" pairs
	:type kwargs: dict
	:return: plugin call URL
	:rtype: str
	"""
	return '{0}?{1}'.format(_url, urlencode(kwargs))


def router(paramstring):
	# Parse a URL-encoded paramstring to the dictionary of
	# {<parameter>: <value>} elements
	params = dict(parse_qsl(paramstring))
	# Check the parameters passed to the plugin
	if params:
		if params['action'] == 'listing':
			# Display the list of videos in a provided category.
			list_movies(params['url'])
		elif params['action'] == 'play':
			# Play a video from a provided URL.
			play(params['url'])
		elif params['action'] == 'genre':
			list_genre()
		else:
			raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
	else:
		root()

if __name__ == '__main__':
	router(sys.argv[2][1:])
