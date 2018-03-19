import json
import requests
from bs4 import BeautifulSoup
import requests.sessions
from simpleplugin import Plugin
import xbmcaddon

plugin = Plugin()

s = requests.Session()

def login():
    addon = xbmcaddon.Addon('plugin.video.open_sap')
    user = addon.getSetting('Username')
    pw = addon.getSetting('Password')
    r = s.get('https://open.sap.com/sessions/new')
    soup = BeautifulSoup(r.content, 'html.parser')
    auth_token = soup.find("input", { "name": "authenticity_token"} )['value']
    payload = { "authenticity_token": auth_token, 'login[email]': user, 'login[password]': pw, 'login[redirect_url]': "/dashboard"}
    r = s.post('https://open.sap.com/sessions', data=payload)

@plugin.action()
def root():
    login()
    r = s.get('https://open.sap.com/api/v2/courses?include=channel%2Cuser_enrollment')
    j = json.loads(r.content)
    enrollments = []
    for data in j['data']:
        if 'user_enrollment' in data['relationships']:
            enrollments.append( {'label': data['attributes']['title'], 'url': plugin.get_url(action='show_course', course_id = data['id']) } )
            print(data['id'])
    return enrollments
 
 
@plugin.action()
def show_course(params):
    login()
    r = s.get('https://open.sap.com/api/v2/course-items?filter[course]=' + params.course_id)
    j = json.loads(r.content)
    streams = []
    for data in j['data']:
        if data['attributes']['content_type'] == 'video':
            streams.append( get_stream(data['relationships']['content']['data']['id']) )

def get_stream(video_id):
    try:
        r = s.get('https://open.sap.com/api/v2/videos/' + video_id)
        j = json.loads(r.content)
        
        return {'label': j['data']['attributes']['title'], 'thumb': j['data']['attributes']['single_stream']['thumbnail_url'], 'url': j['data']['attributes']['single_stream']['hd_url'], 'is_playable': True}
    except:
        print('Fehler bei video' + video_id)
        return {'label': 'Error at video_id' + video_id }

plugin.run()  # Start plugin