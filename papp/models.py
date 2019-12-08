from flask_login import UserMixin
from . import db


class Initials(db.Model):

    __tablename__ = 'Initials'

    initials_id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    user = db.relationship('UserInfo', backref='Initials', lazy='dynamic')


class UserInfo(db.Model, UserMixin):

    __tablename__ = 'UserInfo'

    username = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(100), nullable=False)
    initials_id = db.Column(
        db.Integer,
        db.ForeignKey('Initials.initials_id'),
        nullable=False
    )
    result = db.relationship('Results', backref='UserInfo', lazy='dynamic')

    def get_id(self):
        return self.username


class TaskList(db.Model):

    __tablename__ = 'TaskList'

    task_list_id = db.Column(db.Integer, nullable=False, primary_key=True)
    difficulty = db.Column(db.Integer, nullable=False)
    task = db.relationship('Task', backref='TaskList', lazy='dynamic')


class Task(db.Model):

    __tablename__ = 'Task'

    task_id = db.Column(db.Integer, primary_key=True, nullable=False)
    description = db.Column(db.String(3000), nullable=False)
    task_name = db.Column(db.String(100), nullable=False)
    task_list_id = db.Column(
        db.Integer,
        db.ForeignKey('TaskList.task_list_id'),
        nullable=False
    )
    test_data = db.relationship('TestData', backref='Task', lazy='dynamic')
    result = db.relationship('Results', backref='Task', lazy='dynamic')


class TestData(db.Model):

    __tablename__ = 'TestData'

    task_id = db.Column(
        db.Integer,
        db.ForeignKey('Task.task_id'),
        nullable=False,
        primary_key=True
    )
    test_data_id = db.Column(db.Integer, primary_key=True, nullable=False)
    input_data = db.Column(db.String(200), nullable=False)
    output_data = db.Column(db.String(200), nullable=False)
    __table_args__ = (db.UniqueConstraint('task_id', 'test_data_id'),)


class Results(db.Model):

    __tablename__ = 'Results'

    username = db.Column(
        db.String(100),
        db.ForeignKey('UserInfo.username'),
        nullable=False,
        primary_key=True
    )
    task_id = db.Column(
        db.Integer,
        db.ForeignKey('Task.task_id'),
        nullable=False,
        primary_key=True
    )
    score = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint('username', 'task_id'),)
