#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import re
import urllib2
from hashlib import sha1
import json
import urllib
import urllib2
from urlparse import parse_qsl
try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.path.append('/storage/.kodi/addons/script.module.beautifulsoup4/lib')
    from bs4 import BeautifulSoup


user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'

addon_handle = int(sys.argv[1])

def debug(content):
    print content

def list_videos():
    base_url = 'https://www.galileo.tv'
    html_doc = geturl('https://www.galileo.tv/video-typ/episode/')
    soup = BeautifulSoup(html_doc, 'html.parser')
    items = soup.find_all("div", class_="item")
    for item in items:
        a = item.find('a')
        u = sys.argv[0] + "?video=" + base_url + a.attrs['href']
        liz = xbmcgui.ListItem( a.find('h2').text, iconImage='', thumbnailImage=base_url + a.find('img').attrs['src'])
        infoLabels = {"Title": a.find('h2').text}
        liz.setInfo(type="Video", infoLabels=infoLabels)
        liz.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)

    xbmcplugin.endOfDirectory(addon_handle, succeeded=True, updateListing=False, cacheToDisc=True)


def getvideoid(client_location):
    debug("getvideoid client_location :"+client_location)
    inhalt = geturl(client_location)
    metadataurl =re.compile("getJSON\(atob\('(.+?)'\)", re.DOTALL).findall(inhalt)[0]
    metadataurl = str(base64.b64decode(metadataurl))
    video_id = metadataurl.split('/')[-1]
    source_id = '16'
    videos = playvideo(video_id, client_location,  source_id)
    
def playvideo(video_id,  client_location, source_id=None):
    from hashlib import sha1

    is_type="inputstream.adaptive"
    access_token = 'prosieben'  
    salt = '01!8d8F_)r9]4s[qeuXfP%'
    client_name=''
    print "is_type :"+is_type
    if source_id is None:
        source_id=0 
        json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s?' \
                    'access_token=%s&client_location=%s&client_name=%s' \
                    % (video_id, access_token, client_location, client_name)
        json_data = geturl(json_url)
        json_data = json.loads(json_data) 
        print json_data
        print "........................"
        if not is_type=="":
            for stream in json_data['sources']:
                if  stream['mimetype']=='application/dash+xml': 
                    if int(source_id) <  int(stream['id']):               
                        source_id = stream['id']
                        print source_id
        
    client_id_1 = salt[:2] + sha1( ''.join([str(video_id), salt, access_token, client_location, salt, client_name]).encode('utf-8')).hexdigest()
        
    json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?' \
                'access_token=%s&client_location=%s&client_name=%s&client_id=%s' \
                % (video_id, access_token, client_location, client_name, client_id_1)            
    json_data = geturl(json_url)
    json_data = json.loads(json_data) 
    print json_data
    print "........................"
    server_id = json_data['server_id']
    
    #client_name = 'kolibri-1.2.5'    
    client_id = salt[:2] + sha1(''.join([salt, video_id, access_token, server_id,client_location, str(source_id), salt, client_name]).encode('utf-8')).hexdigest()
    url_api_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources/url?%s' % (video_id, urllib.urlencode({
        'access_token': access_token,
        'client_id': client_id,
        'client_location': client_location,
        'client_name': client_name,
        'server_id': server_id,
        'source_ids': str(source_id),
    }))
    print "url_api_url :"+url_api_url
    json_data = geturl(url_api_url)
    json_data = json.loads(json_data) 
    debug ("---------------------------")
    debug( json_data)
    debug( "........................")
    max_id=0
    for stream in json_data["sources"]:
        ul=stream["url"]
        try:
            sid=re.compile('-tp([0-9]+).mp4', re.DOTALL).findall(ul)[0]
            id=int(sid)
            if max_id<id:
                max_id=id
                data=ul
        except:
            data=ul                                 
    userAgent = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    addon_handle = int(sys.argv[1])
    listitem = xbmcgui.ListItem(path=data+"|"+userAgent)         
    listitem.setProperty(is_type+".license_type", "com.widevine.alpha")
    listitem.setProperty(is_type+".manifest_type", "mpd")
    listitem.setProperty('inputstreamaddon', is_type)
    try:
        lic=json_data["drm"]["licenseAcquisitionUrl"]        
        token=json_data["drm"]["token"]                
        listitem.setProperty(is_type+'.license_key', lic +"?token="+token+"|"+userAgent+"|R{SSM}|")            
    except:
        pass

    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

    return ""


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

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    print(paramstring)
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['video']:
            getvideoid(params['video'])
    else:
        list_videos()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
