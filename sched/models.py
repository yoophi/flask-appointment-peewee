from datetime import datetime
from peewee import BaseModel, IntegerField, DateTimeField, CharField, BooleanField, ForeignKeyField, TextField, Model

# from sqlalchemy import Column, ForeignKey
# from sqlalchemy import Boolean, DateTime, Integer, String, Text
# from sqlalchemy.orm import relationship, synonym
# from sqlalchemy.ext.declarative import declarative_base
from werkzeug import check_password_hash, generate_password_hash
from sched.app import database


# Base = declarative_base()

class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    # __tablename__ = 'user'

    id = IntegerField(primary_key=True)
    created = DateTimeField(default=datetime.now)
    modified = DateTimeField(default=datetime.now)

    name = CharField(max_length=200)  # Column('name', String(200))
    email = CharField(max_length=100, unique=True, null=False)  # Column(String(100), unique=True, nullable=False)
    active = BooleanField(default=True)  # Column(Boolean, default=True)

    # _password = Column('password', String(100))
    password = CharField(max_length=100)

    # def _get_password(self):
    #     return self._password
    #
    # def _set_password(self, password):
    #     if password:
    #         password = password.strip()
    #     self._password = generate_password_hash(password)
    #
    # password_descriptor = property(_get_password, _set_password)
    # password = synonym('_password', descriptor=password_descriptor)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        return super(User, self).save(*args, **kwargs)

    def check_password(self, password):
        if self.password is None:
            return False
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, query, email, password):
        email = email.strip().lower()
        user = query(cls).filter(cls.email == email).first()
        if user is None:
            return None, False
        if not user.active:
            return user, False
        return user, user.check_password(password)

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.id}>'.format(self=self)


class Appointment(BaseModel):
    """An appointment on the calendar."""

    # __tablename__ = 'appointment'

    id = IntegerField(primary_key=True)  # Column(Integer, primary_key=True)
    created = DateTimeField(default=datetime.now)  # Column(DateTime, default=datetime.now)
    modified = DateTimeField(default=datetime.now)  # Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # user_id = IntegerField()# Column(Integer, ForeignKey('user.id'), nullable=False)
    # user = # relationship(User, lazy='joined', join_depth=1, viewonly=True)
    user = ForeignKeyField(User)

    title = CharField()  # Column(String(255))
    start = DateTimeField()  # Column(DateTime, nullable=False)
    end = DateTimeField()  # Column(DateTime, nullable=False)
    allday = BooleanField()  # Column(Boolean, default=False)
    location = CharField()  # Column(String(255))
    description = TextField()  # Column(Text)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        return super(Appointment, self).save(*args, **kwargs)

    @property
    def duration(self):
        delta = self.end - self.start
        return delta.days * 24 * 60 * 60 + delta.seconds

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.id}>'.format(self=self)


if __name__ == '__main__':
    from datetime import timedelta

    database.connect()
    database.create_tables([User, Appointment])

    # Add a sample user.
    user = User(name='Pyunghyuk Yoo',
                email='yoophi@gmail.com',
                password='secret')
    # print 'user.save()', user.save()
    # print 'user.id', user.id
    # print User.select(User.email == 'yoophi@gmail.com').first()
    #
    # print User.select().first()

    now = datetime.now()
    Appointment(
        user=user,
        title='Important Meeting',
        start=now + timedelta(days=3),
        end=now + timedelta(days=3, seconds=3600),
        allday=False,
        location='The Office').save()

    Appointment(
        user=user,
        title='Past Meeting',
        start=now - timedelta(days=3, seconds=3600),
        end=now - timedelta(days=3),
        allday=False,
        location='The Office').save()

    Appointment(
        user=user,
        title='Follow Up',
        start=now + timedelta(days=4),
        end=now + timedelta(days=4, seconds=3600),
        allday=False,
        location='The Office').save()

    Appointment(
        user=user,
        title='Day Off',
        start=now + timedelta(days=5),
        end=now + timedelta(days=5),
        allday=True).save()
