#models.py
from app import db

class Songs(db.Model):

    __tablename__ = 'songs'

    id = db.Column(db.Integer,primary_key=True)
    song_token = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(64),unique=False)
    artist = db.Column(db.String(64),unique=False)
    year = db.Column(db.Integer,nullable=False, default=2000)
    file_name = db.Column(db.String(64))
    active = db.Column(db.Boolean,default=True)
    card_print_date = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, title, artist, year, song_token, file_name, active=True):
        self.title = title
        self.artist = artist    
        self.year = year
        self.song_token = song_token
        self.file_name = file_name
        self.active = active
        self.card_print_date = None


    def __repr__(self):
        return f"Title: {self.title} -- Writer: {self.artist} -- Year: {self.year} -- Token: {self.song_token}"
