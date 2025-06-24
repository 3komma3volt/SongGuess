from mutagen.easyid3 import EasyID3  
from mutagen.id3 import ID3NoHeaderError

def song_info(song):
    try:
        song_info = EasyID3(song)
    except ID3NoHeaderError:
        return {'artist': ["Unknown"], 'title': ["Unknown"], 'date': [0]}
    except Exception as e:
        raise e
    return song_info
