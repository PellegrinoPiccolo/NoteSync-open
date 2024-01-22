from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
import pytz

# Imposta il fuso orario desiderato
tz = pytz.timezone('Europe/Rome')

# Ottieni la data e l'ora correnti con il fuso orario impostato
current_time = datetime.now(tz)
tz = pytz.timezone('Europe/Rome')

# Ottieni la data e l'ora correnti con il fuso orario impostato
current_time = datetime.now(tz)

# Funziona
user_groups = db.Table('user_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

# Funziona
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=current_time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', foreign_keys=[user_id])
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group', foreign_keys=[group_id])
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    folder = db.relationship('Folder', foreign_keys=[folder_id])


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(140))
    password = db.Column(db.String(100))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.relationship('Note', cascade="all, delete-orphan")
    creator = db.relationship('User', foreign_keys=[creator_id])
    users = db.relationship('User', secondary=user_groups, back_populates='groups', passive_deletes=True)
    folders = db.relationship('Folder', cascade="all, delete-orphan")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note', cascade="all, delete-orphan")
    groups = db.relationship('Group', secondary=user_groups, back_populates='users', cascade="all, delete")
    folders = db.relationship('Folder', cascade="all, delete-orphan")

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    creator = db.relationship('User', foreign_keys=[creator_id])
    group = db.relationship('Group', foreign_keys=[group_id])
    notes = db.relationship('Note', cascade="all, delete-orphan")
    folders = db.relationship('Folder', cascade="all, delete-orphan")