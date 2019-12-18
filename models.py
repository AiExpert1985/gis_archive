from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import and_

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///sqlite/gis_archive.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()

class Cityside(db.Model):
	__tablename__ = "citysides"
	id = db.Column(db.Integer, primary_key=True)
	cityside = db.Column(db.String(30), nullable=False)
	uploaders = db.relationship('Uploader', backref='cityside', lazy=True)
	stations = db.relationship('Station', backref='cityside', lazy=True)

class Privilege(db.Model):
	__tablename__ = "privileges"
	id = db.Column(db.Integer, primary_key=True)
	privilege = db.Column(db.String(30), nullable=False)
	uploaders = db.relationship('Uploader', backref='privilege', lazy=True)

class Language(db.Model):
	__tablename__ = "languages"
	id = db.Column(db.Integer, primary_key=True)
	language = db.Column(db.String(30), nullable=False)
	uploaders = db.relationship('Uploader', backref='language', lazy=True)

class Uploader(db.Model):
	__tablename__ = "uploaders"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), nullable=False)
	userId = db.Column(db.String(30), unique=True, nullable=False)
	password = db.Column(db.String(30), nullable=False)
	creationDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	privilege_id = db.Column(db.Integer, db.ForeignKey("privileges.id"), nullable=False)
	cityside_id = db.Column(db.Integer, db.ForeignKey("citysides.id"), nullable=False)
	language_id = db.Column(db.Integer, db.ForeignKey("languages.id"), nullable=False)
	files = db.relationship('File', backref='uploader', lazy=True)

class Station(db.Model):
	__tablename__ = "stations"
	id = db.Column(db.Integer, primary_key=True)
	station = db.Column(db.String(30), nullable=False)
	cityside_id = db.Column(db.Integer, db.ForeignKey("citysides.id"), nullable=False)
	feeders = db.relationship('Feeder', backref='station', lazy=True)
	files = db.relationship('File', backref='station', lazy=True)

class Feeder(db.Model):
	__tablename__ = "feeders"
	id = db.Column(db.Integer, primary_key=True)
	feeder = db.Column(db.String(30), nullable=False)
	station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
	files = db.relationship('File', backref='feeder', lazy=True)

class File(db.Model):
	__tablename__ = "files"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), nullable=False)
	creationDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	updatingDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  
	updator = db.Column(db.String(30), nullable=False)
	note = db.Column(db.String(80), nullable=False)
	uploader_id = db.Column(db.Integer, db.ForeignKey("uploaders.id"), nullable=False)
	station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
	feeder_id = db.Column(db.Integer, db.ForeignKey("feeders.id"), nullable=False)

class Log(db.Model):
	__tablename__ = "logs"
	id = db.Column(db.Integer, primary_key=True)
	action = db.Column(db.String(80), nullable=False)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	name = db.Column(db.String(80), nullable=False)  

class Login(db.Model):
	__tablename__ = "logins"
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	name = db.Column(db.String(80), nullable=False)