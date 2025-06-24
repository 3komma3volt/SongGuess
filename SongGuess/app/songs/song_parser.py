from mutagen.easyid3 import EasyID3  


def song_info(song):
    return EasyID3(song)
