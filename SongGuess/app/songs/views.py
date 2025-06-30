import os
import secrets
import tempfile
import time

import sqlalchemy
from flask import Blueprint, current_app, jsonify, render_template, request, send_file, url_for

from app.models import db, Songs
from app.songs.song_parser import song_info
from app.utils.CardGenerator import CardGenerator

songs = Blueprint('songs',__name__)


ALLOWED_EXTENSIONS = {'mp3'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    

@songs.route('/songs')
def songs_list():
    try:
        song_list = Songs.query.all()
    except sqlalchemy.exc.OperationalError as err:
        return render_template('error.html', error_message="Database connection error. Please try again later.")
    if not song_list:
        return render_template('error.html', error_message='<p>No songs available. Please add some songs to the database.</p>' +
                               f'<p><a href="{ url_for('songs.songs_add') }">Add songs</a></p>')
    return render_template('songs_list.html', songs=song_list, chunk_size=current_app.config['CARD_GENERATION_CHUNK_SIZE'])

@songs.route('/songs/add')
def songs_add():
    return render_template('songs_add.html')

@songs.route('/songs/generate_cards', methods=['POST'])
def generate_cards():
    if request.method == 'POST':
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({
                'error': 60,
                'message': 'Invalid data format.'
            })
        if not len(data):
            return jsonify({
                'error': 70,
                'message': 'No valid song data provided.'
            })
        cards = []
        for song in data:
            # Directly use data from JS to prevent unnecessary database queries
            cards.append({
                    'artist': song.get('artist', 'Unknown'),
                    'title': song.get('title', 'Unknown'),
                    'year': song.get('year', 0),
                    'token': song.get('token', ''),
                })
            song_data = Songs.query.filter_by(song_token=song.get('token')).first()
            if song_data:
                song_data.card_print_date = db.func.now()
                db.session.commit()

        cg = CardGenerator()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            cg.pdf_from_songs(cards, tmpfile.name, "FRONT")
            tmpfile.flush()
            tmpfile_path = tmpfile.name

        return send_file(
            tmpfile_path,
            as_attachment=True,
            download_name=f"songs_cards_{secrets.token_hex(4)}.pdf",
            mimetype="application/pdf"
        )

    return render_template('songs_add.html')

@songs.route('/songs/upload', methods=['POST'])
def songs_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({
            'error': 10,
            'message': 'No file part in the request.'
            })
        
        file = request.files['file']

        if file and not allowed_file(file.filename):
            return jsonify({
            'error': 20,
            'message': f'{file.filename}: Wrong file format.'
            })
        try:
            if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                os.makedirs(current_app.config['UPLOAD_FOLDER'])

            if file and allowed_file(file.filename):
                file_token = secrets.token_hex(4)
                while os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], file_token + '.mp3')):
                    file_token = secrets.token_hex(4)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file_token) + '.mp3')

                song_data = song_info(os.path.join(current_app.config['UPLOAD_FOLDER'], file_token + '.mp3'))

                if not song_data:
                    return jsonify({
                        'error': 30,
                        'message': 'File is not a valid MP3.'
                    })

                artist = song_data.get('artist', ["Unknown"])[0]
                title = song_data.get('title', ["Unknown"])[0]
                year = song_data.get('date', [0])[0]

                song_data = Songs(
                    artist=artist,
                    title=title,
                    year=year,
                    file_name=file.filename,
                    song_token=file_token,
                    active=True
                )

                db.session.add(song_data)
                db.session.commit()
                
                return jsonify({
                    'error': 0,
                    'message': {'artist': artist,
                                'title': title,
                                'year': year,
                                'token': file_token,
                                'filename': file.filename}
                    })
            
        except OSError as e:
            current_app.logger.error(f"Could not create upload folder: {e}")
            return jsonify({
                'error': 21,
                'message': f'Could not create upload folder: {e}'
            })
        except sqlalchemy.exc.OperationalError as err:
            current_app.logger.error(f"Database error: {err}")
            db.session.rollback()

            try:
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], file_token) + '.mp3')
            except OSError as e:
                current_app.logger.error(f"Could not remove file {file_token}.mp3: {e}")

            return jsonify({
                'error': 31,
                'message': f'Database error: Could not save song data. {str(err)}'
            })


@songs.route('/songs/delete', methods=['POST'])
def songs_remove():
    if request.method == 'POST':
        data = request.get_json()
        if len(data) == 0:
            return jsonify({
                'error': 70,
                'message': 'No valid song data provided.'
            })
        try:
            for song in data:
                if os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], song + '.mp3')):
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], song + '.mp3'))
                song_data = Songs.query.filter_by(song_token=song).first()
                if song_data:
                    db.session.delete(song_data)
            db.session.commit()
            return jsonify({
                'error': 0,
                'message': 'Songs deleted successfully.'
            })
        except OSError as e:
            current_app.logger.error(f"Could not remove file: {e}")
            db.session.rollback()
            return jsonify({
                'error': 21,
                'message': f'Could not remove file: {e}'
            })
        except sqlalchemy.exc.OperationalError as err:
            current_app.logger.error(f"Database error: {err}")
            db.session.rollback()
            return jsonify({
                'error': 32,
                'message': f'Database error: Could not delete songs. {str(err)}'
            })
        
    else:
        return jsonify({
            'error': 1,
            'message': 'Invalid request method.'
        })

@songs.route('/songs/save', methods=['POST'])
def songs_save():
    if request.method == 'POST':
        data = request.get_json()
        song = Songs.query.filter_by(song_token=data['token']).first()

        if not song:
            return jsonify({
                'error': 40,
                'message': 'Song not found.'
            })
        
        if 'artist' not in data or 'title' not in data or 'year' not in data:
            return jsonify({
                'error': 41,
                'message': 'Missing required fields: artist, title, year.'
            })
        if not data['artist'] or not data['title']:
            return jsonify({
                'error': 42,
                'message': 'Artist and title cannot be empty.'
            })
        current_year = time.localtime().tm_year
        if int(data.get('year', 0)) < 1800 or int(data.get('year', current_year + 1)) > current_year:
            return jsonify({
                'error': 50,
                'message': 'Year not plaussible.'
            })

        try:
            song.artist = data['artist']
            song.title = data['title']
            song.year = data['year']
            db.session.commit()

        except sqlalchemy.exc.OperationalError as err:
            current_app.logger.error(f"Database error: {err}")
            db.session.rollback()
            return jsonify({
                'error': 32,
                'message': f'Database error: Could not update song data. {str(err)}'
            })

        return jsonify({
            'error': 0,
            'message': 'Song updated successfully.',
            'data': {
                'artist': song.artist,
                'title': song.title,
                'year': song.year,
                'token': song.song_token
            }
        })