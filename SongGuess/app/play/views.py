import os
import re

from flask import render_template,Blueprint, current_app, send_from_directory

from app.models import Songs

play = Blueprint('play',__name__)
@play.route('/play')
def play_song():
    return redirect('/')

@play.route('/play/file/<path:filename>')
def play_file(filename):
    current_app.logger.info(f'Request to play file: {filename}')
    music_folder = current_app.config.get('UPLOAD_FOLDER', 'static')
    return send_from_directory(music_folder, filename)

@play.route('/play/<song_token>')
def song(song_token):

    if not song_token:
        current_app.logger.error('Song token is missing.')
        return render_template('error.html', error_message='Song ID is required.')
    
    # Sometimes unreadable characters are transmitted from the qr scanner
    song_token = re.sub(r'[^a-zA-Z0-9_-]', '', song_token)

    song = Songs.query.filter_by(song_token=song_token).first()

    if not song:
        current_app.logger.error(f'Song with token {song_token} not found.')
        return render_template('error.html', error_message=f'Song with ID {song_token} not found.')
    
    song_file = song.song_token + '.mp3'

    if not os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], song_file)):
        current_app.logger.error(f'Song file {song_file} does not exist in the upload folder.')
        return render_template('error.html', error_message=f'Song file {song_file} not found.')
    
    return render_template('play.html', song_token=song_token, song_file=song_file)

