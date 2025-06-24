# puppycompanyblog/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['BASE_DIR'] = basedir    
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'musicfolder')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['CARD_GENERATION_CHUNK_SIZE'] = 50
 
db = SQLAlchemy(app)
Migrate(app,db)


from app.main.views import main  # noqa: E402
from app.songs.views import songs # noqa: E402
from app.play.views import play  # noqa: E402

app.register_blueprint(main)
app.register_blueprint(songs)
app.register_blueprint(play)