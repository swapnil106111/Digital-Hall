#!/usr/bin/env python
from pathlib import Path
from config import key, channel_id, source_path, destination_path
from enum import Enum
import sys
import json
import os
from os.path import join
import re
from urllib.request import urlopen, HTTPError
from ricecooker.chefs import SushiChef
from ricecooker.classes import nodes, questions, files
from ricecooker.classes.licenses import get_license
from ricecooker.classes.files import VideoFile, HTMLZipFile, DocumentFile, YouTubeVideoFile
from ricecooker.exceptions import UnknownContentKindError, UnknownFileTypeError, UnknownQuestionTypeError, raise_for_invalid_channel
from le_utils.constants import content_kinds,file_formats, format_presets, licenses, exercises, languages
from pressurecooker.encodings import get_base64_encoding
import youtube_dl
import pprint
from multiprocessing import Pool
from pathlib import Path
import os 
# test video

#video_url='https://www.youtube.com/watch?v=bKbioetO4AE' # highres = 25MB
#video_url='https://vimeo.com/238190750' # lowres = 5MB
def downloader(id):
    # path = "/home/nalanda/Documents/video/"+id+".mp4"
    path = source_path+id+".mp4"
    # my_file = Path(path)
    print(path)
    if os.path.exists(path):
        print("Already Downloaded::", path)
    else:
        video_url = 'https://www.youtube.com/watch?v=' + id
        ydl_options = {
            'outtmpl': '%(id)s.%(ext)s',  # use the video id for filename
            'writethumbnail': False,
            'no_warnings': True,
            'continuedl': False,
            'restrictfilenames': True,
            'quiet': False,
            'writesubtitles': True,
            'format': "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]"}
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            try:
                ydl.add_default_info_extractors()
                vinfo = ydl.extract_info(video_url, download=True)
            except (youtube_dl.utils.DownloadError, youtube_dl.utils.ContentTooShortError, youtube_dl.utils.ExtractorError) as e:
                print('error_occured')




playlist_api = "https://www.googleapis.com/youtube/v3/playlists?part=snippet&channelId="+str(channel_id)+"&key="+str(key)+"&maxResults=50"

video_api = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId="


''' Code to Get Tree Hierarchy for Digital School Hall '''
final_tree = {}
try:
    conn = urlopen(playlist_api)
    SAMPLE_TREE = json.loads(conn.read().decode('utf-8'))
    data = SAMPLE_TREE
    final_tree['children'] = []
    totalResults = SAMPLE_TREE['pageInfo']['totalResults']
    count = totalResults / 50
    count = count + 1

    #print(SAMPLE_TREE['items'])
    for i in range(0,int(count)):
        if "nextPageToken" in data.keys():
            nextPageToken = data['nextPageToken']
            playlist_api = playlist_api + "&pageToken="+str(nextPageToken)
            conn = urlopen(playlist_api)
            data = json.loads(conn.read().decode('utf-8'))
            SAMPLE_TREE['items'].extend(data['items'])
        else:
            final_tree['children'].extend(SAMPLE_TREE['items'])
            break
except Exception as e:
    print(e)

print("Tree received")
final = []


for i in final_tree['children']:
    id = i['id']
    final_video_api = video_api +str(id)+"&key="+str(key)
    conn = urlopen(final_video_api)
    video_tree = json.loads(conn.read().decode('utf-8'))
    tree = video_tree
    totalResults = video_tree['pageInfo']['totalResults']
    count = totalResults / 50
    count = count + 1
    i['children']=[]
    for j in range(0,int(count)):
        if "nextPageToken" in tree.keys():
            nextPageToken = tree['nextPageToken']
            final_video_api = video_api+str(id)+"&key="+str(key)+"&pageToken="+nextPageToken
            conn = urlopen(final_video_api)
            tree = json.loads(conn.read().decode('utf-8'))
            video_tree['items'].extend(tree['items'])

        else:
            i['children'].extend(video_tree['items'])
            for k in i['children']:
            	final.append(k['snippet']['resourceId']['videoId'])

print(final)
print(len(final))
p = Pool(4)
try:
	arrLevel = []
	arrLevel = p.map(downloader, final)
	p.close()
	p.join()
except Exception as e:
	print(e)


