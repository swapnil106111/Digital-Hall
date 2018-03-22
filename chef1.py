'''
    Digital School Hall
'''


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


# CHANNEL SETTINGS
SOURCE_DOMAIN = "https://www.youtube.com"                 # content provider's domain
SOURCE_ID = "DIGITAL STUDY HALL"                             # an alphanumeric channel ID
CHANNEL_TITLE = "DIGITAL STUDY HALL"       # a humand-readbale title
CHANNEL_LANGUAGE = "en"                            # language code of channel


# LOCAL DIRS
EXAMPLES_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(EXAMPLES_DIR, 'data')
CONTENT_DIR = os.path.join(EXAMPLES_DIR, 'content')

youtube_ids = ['MdpRpGL6hUg','kRq2C4nLa6Y','M3eMFrKGMdE','lRWInFMqnv4']
playlist_api = "https://www.googleapis.com/youtube/v3/playlists?part=snippet&channelId="+str(channel_id)+"&key="+str(key)+"&maxResults=50"

video_api = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId="


''' Code to Get Tree Hierarchy for Digital School Hall '''
final_tree = {}
try:
    conn = urlopen(playlist_api)
    SAMPLE_TREE = json.loads(conn.read().decode('utf-8'))
    data = SAMPLE_TREE
    final_tree['id']="UP_Board"
    final_tree['title']="UP Board"
    final_tree['description']="v1"
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
            #print(data['items'])
        else:
            final_tree['children'].extend(SAMPLE_TREE['items'])
            break
except Exception as e:
    print(e)

print("Tree received")



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

print("All videos received in API")
 ###################### For Topics arrangement ######################

children = []
topics = []

def create_topics(title, topic_data):
    title1 = title.split(' ')
    if title.startswith('India'):
        pass
    elif title.startswith('Class') or title.startswith('class'):
        name = (title1[0]+' '+title1[1]).lower().replace(' ','_')
        if name in topics:
            for j in range(0,len(children)):
                if children[j]['id']==name:
                    children[j]['children'].append(topic_data)
        else:
            topics.append(name)
            children.append({"id":name,"title":name.replace('_',' '),"children":[]})
            for j in range(0,len(children)):
                if children[j]['id']==name:
                    children[j]['children'].append(topic_data)
    else:
        if "others" in topics:
            for j in range(0,len(children)):
                if children[j]['id']=="others":
                    children[j]['children'].append(topic_data)
        else:
            #print("sample")
            topics.append("others")
            children.append({"id":"others","title":"others","children":[]})
            for j in range(0,len(children)):
                if children[j]['id']=="others":
                    children[j]['children'].append(topic_data)

print("Arranged tree properly")

for i in final_tree['children']:
    create_topics(i['snippet']['title'], i)


final_tree['children']= []
final_tree['children'].extend(children)



''' Code to convert API tree into Ricecooker understandable format '''
SAMPLE_TREE = {}
SAMPLE_TREE['id']=final_tree['id']
SAMPLE_TREE['title']=final_tree['title']
SAMPLE_TREE['description']=final_tree['description']
SAMPLE_TREE['children']=[]
for sub_topic in final_tree['children']:
    sub_topic_sample_tree = {}
    sub_topic_sample_tree['id'] = str(sub_topic['id'])
    sub_topic_sample_tree['title'] = sub_topic['title']
    sub_topic_sample_tree['children'] = []
    for sub_topic_1 in sub_topic['children']:
        if len(sub_topic_1['children']) > 0:
            sub_topic_1_sample_tree = {}
            sub_topic_1_sample_tree['id'] = str(sub_topic_1['id'])
            sub_topic_1_sample_tree['title'] = sub_topic_1['snippet']['title']
            sub_topic_1_sample_tree['children'] = []
            for sub_topic_2 in sub_topic_1['children']:
                if str(sub_topic_2['snippet']['resourceId']['videoId']) not in youtube_ids:
                    sub_topic_2_sample_tree = {}
                    sub_topic_2_sample_tree['id'] = str(sub_topic_2['snippet']['resourceId']['videoId'])
                    sub_topic_2_sample_tree['title'] = sub_topic_2['snippet']['title']
                    sub_topic_2_sample_tree['license'] = "CC BY"
                    sub_topic_2_sample_tree['copyright_holder'] = "Digital Study Hall"
                    final_video_path = destination_path+str(sub_topic_2['snippet']['resourceId']['videoId'])+".mp4"
                    sub_topic_2_sample_tree['files']=[{"path":final_video_path}]
                    final_subtitle_path = source_path+str(sub_topic_2['snippet']['resourceId']['videoId'])+".vtt"
                    if os.path.isfile(final_subtitle_path):
                        sub_topic_2_sample_tree['files'].append({"path":final_subtitle_path,"language":"en"	})
                    sub_topic_1_sample_tree['children'].append(sub_topic_2_sample_tree)
                    youtube_ids.append(str(sub_topic_2['snippet']['resourceId']['videoId']))
                else:
                    print("Repeated Video ::::", str(sub_topic_2['snippet']['resourceId']['videoId']))

            sub_topic_sample_tree['children'].append(sub_topic_1_sample_tree)
        else:
            print(sub_topic_1['snippet']['title'])
            print(len(sub_topic_1['children']))
    SAMPLE_TREE['children'].append(sub_topic_sample_tree)

print(json.dumps(SAMPLE_TREE))


SAMPLE_TREE1 = []
SAMPLE_TREE1.append(SAMPLE_TREE)
print(SAMPLE_TREE1)








# A utility function to manage absolute paths that allows us to refer to files
# in the CONTENT_DIR (subdirectory `content/' in current directory) using content://
def get_abspath(path, content_dir=CONTENT_DIR):
    """
    Replaces `content://` with absolute path of `content_dir`.
    By default looks for content in subdirectory `content` in current directory.
    """
    if path:
        file = re.search('content://(.+)', path)
        if file:
            return os.path.join(content_dir, file.group(1))
    return path



class FileTypes(Enum):
    """ Enum containing all file types Ricecooker can have

        Steps:
            AUDIO_FILE: mp3 files
            THUMBNAIL: png, jpg, or jpeg files
            DOCUMENT_FILE: pdf files
    """
    AUDIO_FILE = 0
    THUMBNAIL = 1
    DOCUMENT_FILE = 2
    VIDEO_FILE = 3
    YOUTUBE_VIDEO_FILE = 4
    VECTORIZED_VIDEO_FILE = 5
    VIDEO_THUMBNAIL = 6
    YOUTUBE_VIDEO_THUMBNAIL_FILE = 7
    HTML_ZIP_FILE = 8
    SUBTITLE_FILE = 9
    TILED_THUMBNAIL_FILE = 10
    UNIVERSAL_SUBS_SUBTITLE_FILE = 11
    BASE64_FILE = 12
    WEB_VIDEO_FILE = 13


FILE_TYPE_MAPPING = {
    content_kinds.AUDIO : {
        file_formats.MP3 : FileTypes.AUDIO_FILE,
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
    content_kinds.DOCUMENT : {
        file_formats.PDF : FileTypes.DOCUMENT_FILE,
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
    content_kinds.HTML5 : {
        file_formats.HTML5 : FileTypes.HTML_ZIP_FILE,
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
    content_kinds.VIDEO : {
        file_formats.MP4 : FileTypes.VIDEO_FILE,
        file_formats.VTT : FileTypes.SUBTITLE_FILE,
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
    content_kinds.EXERCISE : {
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
}



def guess_file_type(kind, filepath=None, youtube_id=None, web_url=None, encoding=None):
    """ guess_file_class: determines what file the content is
        Args:
            filepath (str): filepath of file to check
        Returns: string indicating file's class
    """
    if youtube_id:
        return FileTypes.YOUTUBE_VIDEO_FILE
    elif web_url:
        return FileTypes.WEB_VIDEO_FILE
    elif encoding:
        return FileTypes.BASE64_FILE
    else:
        ext = os.path.splitext(filepath)[1][1:].lower()
        if kind in FILE_TYPE_MAPPING and ext in FILE_TYPE_MAPPING[kind]:
            return FILE_TYPE_MAPPING[kind][ext]
    return None

def guess_content_kind(path=None, web_video_data=None, questions=None):
    """ guess_content_kind: determines what kind the content is
        Args:
            files (str or list): files associated with content
        Returns: string indicating node's kind
    """
    # If there are any questions, return exercise
    if questions and len(questions) > 0:
        return content_kinds.EXERCISE

    # See if any files match a content kind
    if path:
        ext = os.path.splitext(path)[1][1:].lower()
        if ext in content_kinds.MAPPING:
            return content_kinds.MAPPING[ext]
        raise InvalidFormatException("Invalid file type: Allowed formats are {0}".format([key for key, value in content_kinds.MAPPING.items()]))
    elif web_video_data:
        return content_kinds.VIDEO
    else:
        return content_kinds.TOPIC



class SampleChef(SushiChef):
    """
    The chef class that takes care of uploading channel to the content curation server.

    We'll call its `main()` method from the command line script.
    """
    channel_info = {    
        'CHANNEL_SOURCE_DOMAIN': SOURCE_DOMAIN,       # who is providing the content (e.g. learningequality.org)
        'CHANNEL_SOURCE_ID': SOURCE_ID,                   # channel's unique id
        'CHANNEL_TITLE': CHANNEL_TITLE,
        'CHANNEL_LANGUAGE': CHANNEL_LANGUAGE,
        'CHANNEL_THUMBNAIL': 'https://yt3.ggpht.com/-8WqhSmWf904/AAAAAAAAAAI/AAAAAAAAAAA/6cJNPhnxgpY/s288-mo-c-c0xffffffff-rj-k-no/photo.jpg', # (optional) local path or url to image file
        'CHANNEL_DESCRIPTION': 'Digital School Hall Youtube Video',      # (optional) description of the channel (optional)
    }

    def construct_channel(self, *args, **kwargs):
        """
        Create ChannelNode and build topic tree.
        """
        channel = self.get_channel(*args, **kwargs)   # creates ChannelNode from data in self.channel_info
        
        _build_tree(channel, SAMPLE_TREE1)
        print(channel)
        raise_for_invalid_channel(channel)
        return channel


def _build_tree(node, sourcetree):
    """
    Parse nodes given in `sourcetree` and add as children of `node`.
    """
    for child_source_node in sourcetree:
        try:
            main_file = child_source_node['files'][0] if 'files' in child_source_node else {}
            kind = guess_content_kind(path=main_file.get('path'), web_video_data=main_file.get('youtube_id') or main_file.get('web_url'), questions=child_source_node.get("questions"))
        except UnknownContentKindError:
            continue

        if kind == content_kinds.TOPIC:
            child_node = nodes.TopicNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                author=child_source_node.get("author"),
                description=child_source_node.get("description"),
                thumbnail=child_source_node.get("thumbnail"),
            )
            node.add_child(child_node)

            source_tree_children = child_source_node.get("children", [])

            _build_tree(child_node, source_tree_children)

        elif kind == content_kinds.VIDEO:
            child_node = nodes.VideoNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                license=get_license(child_source_node.get("license"), description="Description of license", copyright_holder=child_source_node.get('copyright_holder')),
                author=child_source_node.get("author"),
                description=child_source_node.get("description"),
                derive_thumbnail=True, # video-specific data
                thumbnail=child_source_node.get('thumbnail'),
            )
            add_files(child_node, child_source_node.get("files") or [])
            node.add_child(child_node)

        else:                   # unknown content file format
            continue

    return node

def add_files(node, file_list):
    for f in file_list:

        path = f.get('path')
        if path is not None:
            abspath = get_abspath(path)      # NEW: expand  content://  -->  ./content/  in file paths
        else:
            abspath = None

        file_type = guess_file_type(node.kind, filepath=abspath, youtube_id=f.get('youtube_id'), web_url=f.get('web_url'), encoding=f.get('encoding'))

        if file_type == FileTypes.AUDIO_FILE:
            node.add_file(files.AudioFile(path=abspath, language=f.get('language')))
        elif file_type == FileTypes.THUMBNAIL:
            node.add_file(files.ThumbnailFile(path=abspath))
        elif file_type == FileTypes.DOCUMENT_FILE:
            node.add_file(files.DocumentFile(path=abspath, language=f.get('language')))
        elif file_type == FileTypes.HTML_ZIP_FILE:
            node.add_file(files.HTMLZipFile(path=abspath, language=f.get('language')))
        elif file_type == FileTypes.VIDEO_FILE:
            node.add_file(files.VideoFile(path=abspath, language=f.get('language'), ffmpeg_settings=f.get('ffmpeg_settings')))
        elif file_type == FileTypes.SUBTITLE_FILE:
            node.add_file(files.SubtitleFile(path=abspath, language=f['language']))
        elif file_type == FileTypes.BASE64_FILE:
            node.add_file(files.Base64ImageFile(encoding=f['encoding']))
        elif file_type == FileTypes.WEB_VIDEO_FILE:
            node.add_file(files.WebVideoFile(web_url=f['web_url'], high_resolution=f.get('high_resolution')))
        elif file_type == FileTypes.YOUTUBE_VIDEO_FILE:
            node.add_file(files.YouTubeVideoFile(youtube_id=f['youtube_id'], high_resolution=f.get('high_resolution')))
            node.add_file(files.YouTubeSubtitleFile(youtube_id=f['youtube_id'], language='en'))
        else:
            raise UnknownFileTypeError("Unrecognized file type '{0}'".format(f['path']))



if __name__ == '__main__':
    """
    This code will run when the sushi chef is called from the command line.
    """

    chef = SampleChef()
    chef.main()

