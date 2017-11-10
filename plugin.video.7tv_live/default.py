#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
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
import urllib, urllib2


channels = { 'Pro7' : { 'video_id' : 'prosieben-de-24x7', 
                        'client_location': 'https://www.prosieben.de/livestream',
                         'access_token' : 'prosieben', 
                         'getprotocol' : 'http://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=prosieben&client_location=https%3A%2F%2Fwww.prosieben.de%2Flivestream&property_name=prosieben-de-24x7&client_token=01b353c155a9006e80ae7c5ed3eb1c09c0a6995556&secure_delivery=true'
                          },
                         
            'SAT1' : { 'video_id' : 'sat1-de-24x7', 
                        'client_location': 'https://www.sat1.de/livestream',
                            'access_token' : 'sat1',
                            'getprotocol' : 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=sat1&client_location=https%3A%2F%2Fwww.sat1.de%2Flivestream&property_name=sat1-de-24x7&client_token=01e491d866b37341734d691a8acb48af37a77bf26f&secure_delivery=true&callback=_4ma9f1tru71n0'
                           },
            'prosiebenmaxx' : { 'video_id' : 'prosiebenmaxx-de-24x7', 
                        'client_location': 'https://www.prosiebenmaxx.de/livestream',
                            'access_token' : 'prosiebenmaxx',
                            'getprotocol' : 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=prosiebenmaxx&client_location=https%3A%2F%2Fwww.prosiebenmaxx.de%2Flivestream&property_name=prosiebenmaxx-de-24x7&client_token=01963623e9b364805dbe12f113dba1c4914c24d189&secure_delivery=true&callback=_4ma9fzn1n0i0'
                           }
                    }

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'

addon_handle = int(sys.argv[1])
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')

def getJson(channel):
    getprotocol = channel['getprotocol']
    req = urllib2.Request(getprotocol, headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'User-Agent': user_agent, 'Accept-Language' : 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7', 'DNT': '1', 'Connection': 'keep-alive'})
    json_callback = urllib2.urlopen(req).read()
    print json_callback
    res = re.findall('server_token\":\"(.*?)\"', json_callback)
    print res[0]

    server_token = res[0]


    salt = '01!8d8F_)r9]4s[qeuXfP%'
    client_token = salt[:2] + sha1(
                ''.join([str(channel['video_id']), salt, channel['access_token'], server_token, channel['client_location'], 'dash:widevine'
                ]).encode(
                    'utf-8')).hexdigest()


    geturl = 'https://vas-live-mdp.glomex.com/live/1.0/geturls?access_token=' \
 		+ channel['access_token'] + '&client_location=' \
 		+ urllib.quote_plus(channel['client_location']) + '&property_name=' \
		+ channel['video_id'] + '&protocols=dash%3Awidevine&server_token=' \
            + server_token \
            + '&client_token=' \
            + client_token \
            + '&secure_delivery=true&callback=_4ma9f1335ytv1'
    print ''
    print geturl


    print ''
    req = urllib2.Request(geturl, headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'User-Agent': user_agent, 'Accept-Language' : 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7', 'DNT': '1', 'Connection': 'keep-alive'})
    json_callback = urllib2.urlopen(req).read()

    json_string = re.findall('_4ma9f1335ytv1\((.*?)\)', json_callback)[0]

    parsed_json = json.loads(json_string)
    return parsed_json['data']['urls']['dash']['widevine']


def add_listitem(json_data, name):
    mpd_url = json_data['url'];

    is_type="inputstream.adaptive"
    
    listitem = xbmcgui.ListItem(name, path=mpd_url+"|"+user_agent)         
    listitem.setProperty(is_type+".license_type", "com.widevine.alpha")
    listitem.setProperty(is_type+".manifest_type", "mpd")
    listitem.setProperty('inputstreamaddon', is_type)

    #if infoLabels != '':
     #   listitem.setInfo(type="video", infoLabels=ast.literal_eval(infoLabels))
    try:
        lic=json_data["drm"]["licenseAcquisitionUrl"]        
        token=json_data["drm"]["token"]                
        listitem.setProperty(is_type+'.license_key', lic +"?token="+token+"|"+user_agent+"|R{SSM}|")            
    except:
        pass
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=mpd_url, listitem=listitem, isFolder=False)


json_data = getJson(channels['Pro7'])
add_listitem(json_data, 'Pro7')

json_data = getJson(channels['SAT1'])
add_listitem(json_data, 'SAT1')

json_data = getJson(channels['prosiebenmaxx'])
add_listitem(json_data, '7MAXX')

xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)