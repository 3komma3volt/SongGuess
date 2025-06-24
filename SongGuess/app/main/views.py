from flask import render_template,Blueprint, url_for, current_app
from app.models import db, Songs

main = Blueprint('main',__name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/help')
def info():
    return render_template('help.html', chunk_size=current_app.config['CARD_GENERATION_CHUNK_SIZE'])

@main.route('/play')
def play():
    songs = db.session.query(Songs.id).all()
    if not songs:
         return render_template('error.html', error_message='<p>No songs available. Please add some songs to the database.</p>' +
                               f'<p><a href="{ url_for('songs.songs_add') }">Add songs</a></p>')
    return render_template('scan.html')