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

channels = {'Pro7': {'video_id': 'prosieben-de-24x7',
                     'client_location': 'https://www.prosieben.de/livestream',
                     'access_token': 'prosieben',
                     'getprotocol': 'http://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=prosieben&client_location=https%3A%2F%2Fwww.prosieben.de%2Flivestream&property_name=prosieben-de-24x7&client_token=01b353c155a9006e80ae7c5ed3eb1c09c0a6995556&secure_delivery=true',
                     'lable': 'Pro7'
                     },
            'Kabel1': {'video_id': 'kabeleins-de-24x7',
                       'client_location': 'https://www.kabeleins.de/livestream',
                       'access_token': 'kabeleins',
                       'getprotocol': 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=kabeleins&client_location=https%3A%2F%2Fwww.kabeleins.de%2Flivestream&property_name=kabeleins-de-24x7&client_token=014c87bfe2ce4aebf6219ed699602a1f152194e4cd&secure_delivery=true&callback=_4ma9f1l5bn2m0',
                       'lable': 'Kabel 1'
                       },
            'SAT1': {'video_id': 'sat1-de-24x7',
                     'client_location': 'https://www.sat1.de/livestream',
                     'access_token': 'sat1',
                     'getprotocol': 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=sat1&client_location=https%3A%2F%2Fwww.sat1.de%2Flivestream&property_name=sat1-de-24x7&client_token=01e491d866b37341734d691a8acb48af37a77bf26f&secure_delivery=true&callback=_4ma9f1tru71n0',
                     'lable': 'SAT1'
                     },
            'prosiebenmaxx': {'video_id': 'prosiebenmaxx-de-24x7',
                              'client_location': 'https://www.prosiebenmaxx.de/livestream',
                              'access_token': 'prosiebenmaxx',
                              'getprotocol': 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=prosiebenmaxx&client_location=https%3A%2F%2Fwww.prosiebenmaxx.de%2Flivestream&property_name=prosiebenmaxx-de-24x7&client_token=01963623e9b364805dbe12f113dba1c4914c24d189&secure_delivery=true&callback=_4ma9fzn1n0i0',
                              'lable': '7MAXX'
                              },
            'SIXX': {'video_id': 'sixx-de-24x7',
                     'client_location': 'https://www.sixx.de/livestream',
                     'access_token': 'sixx',
                     'getprotocol': 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=sixx&client_location=https%3A%2F%2Fwww.sixx.de%2Flivestream&property_name=sixx-de-24x7&client_token=017705703133050842d3ca11fc20a6fc205b8b4025&secure_delivery=true&callback=_4ma9f1ucxb4g0',
                     'lable': 'SIXX'
                     },
            'SAT1Gold': {'video_id': 'sat1gold-de-24x7',
                         'client_location': 'https://www.sat1gold.de/livestream',
                         'access_token': 'sat1gold',
                         'getprotocol': 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=sat1gold&client_location=https%3A%2F%2Fwww.sat1gold.de%2Flivestream&property_name=sat1gold-de-24x7&client_token=01107e433196365e4d54d0f90bdf1070cd2df5e190&secure_delivery=true&callback=_4ma9f1uvr83p0',
                         'lable': 'SAT1 Gold'
                         },
            'Kabel1Doku': {'video_id': 'kabeleinsdoku-de-24x7',
                           'client_location': 'https://www.kabeleinsdoku.de/livestream',
                           'access_token': 'kabeleinsdoku',
                           'getprotocol': 'https://vas-live-mdp.glomex.com/live/1.0/getprotocols?access_token=kabeleinsdoku&client_location=https%3A%2F%2Fwww.kabeleinsdoku.de%2Flivestream&property_name=kabeleinsdoku-de-24x7&client_token=01ea6d32ff5de5d50d0290dbdf819f9b856bcfd44a&secure_delivery=true&callback=_4ma9fym65ch0',
                           'lable': 'Kabel1 Doku'
                           }
            }

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'

addon_handle = int(sys.argv[1])
icon_base = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo(
    'path') + '/resource/').decode('utf-8')


def getJson(channel):
    getprotocol = channel['getprotocol']
    req = urllib2.Request(getprotocol, headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                                                'User-Agent': user_agent, 'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7', 'DNT': '1', 'Connection': 'keep-alive'})
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

    req = urllib2.Request(geturl, headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                                           'User-Agent': user_agent, 'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7', 'DNT': '1', 'Connection': 'keep-alive'})
    json_callback = urllib2.urlopen(req).read()

    json_string = re.findall('_4ma9f1335ytv1\((.*?)\)', json_callback)[0]

    parsed_json = json.loads(json_string)
    return parsed_json['data']['urls']['dash']['widevine']


def add_channel(name):
    u = sys.argv[0] + "?channel=" + name
    ch_icon = newimg = os.path.join(
        xbmcaddon.Addon().getAddonInfo('path'), "resources", name + ".png")
    liz = xbmcgui.ListItem(
        channels[name]['lable'], iconImage=ch_icon, thumbnailImage=ch_icon)
    infoLabels = {"Title": name}
    liz.setInfo(type="Video", infoLabels=infoLabels)
    liz.setProperty('IsPlayable', 'true')
    #liz.setProperty("fanart_image", "")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)


def list_channels():
    for k in channels.keys():
        add_channel(k)
    xbmcplugin.endOfDirectory(
        addon_handle, succeeded=True, updateListing=False, cacheToDisc=True)


def play(name):
    json_data = getJson(channels[name])
    mpd_url = json_data['url']

    is_type = "inputstream.adaptive"

    listitem = xbmcgui.ListItem(name, path=mpd_url + "|" + user_agent)
    listitem.setProperty(is_type + ".license_type", "com.widevine.alpha")
    listitem.setProperty(is_type + ".manifest_type", "mpd")
    listitem.setProperty('inputstreamaddon', is_type)

    try:
        lic = json_data["drm"]["licenseAcquisitionUrl"]
        token = json_data["drm"]["token"]
        listitem.setProperty(is_type + '.license_key', lic +
                             "?token=" + token + "|" + user_agent + "|R{SSM}|")
    except:
        pass
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem)


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
        if params['channel']:
            play(params['channel'])
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_channels()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
