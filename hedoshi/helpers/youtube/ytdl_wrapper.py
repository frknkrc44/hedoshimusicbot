from yt_dlp import YoutubeDL
from yt_dlp.postprocessor.common import PostProcessor
from os import getcwd
from re import sub
from pyrogram.types import Message
from time import time
from logging import info
from ... import translator as _

yt_host_names = [
    'youtube.com',
    'www.youtube.com',
    'm.youtube.com'
]

yt_valid_ends = [
    '.m3u8'
]


class FilenameCollectorPP(PostProcessor):
    # https://stackoverflow.com/a/68165682
    def __init__(self):
        super(FilenameCollectorPP, self).__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information['filepath'])
        return [], information


'''
def _is_valid_ends(url: str):
    for item in yt_valid_ends:
        if item in yt_valid_ends:
            return True

    return False
'''


def is_valid(url: str):
    url = sub('https?://', '', url)
    return url.split('/', 1)[0] in yt_host_names  # or _is_valid_ends(url)


def download_media(url: str, reply: Message, audio: bool = False) -> str:
    globals()['last_percent'] = -1
    globals()['last_percent_epoch'] = 0

    opts = {
        'ignoreerrors': True,
        'outtmpl': f'{getcwd()}/downloads/%(id)s-{"audio" if audio else "video"}.%(ext)s',
        'cachedir': f'{getcwd()}/downloads'
    }

    if audio:
        opts['format'] = 'm4a'  # bestaudio is very big!
    else:
        opts['format'] = 'bestvideo+bestaudio/best'

    filename_collector = FilenameCollectorPP()
    with YoutubeDL(opts) as ytdl:
        ytdl.add_post_processor(filename_collector)
        ytdl.download([url])

    return filename_collector.filenames[-1]
