from datetime import datetime
from peewee import BaseModel, DateTimeField, CharField, BooleanField, ForeignKeyField, TextField, Model
from werkzeug.security import check_password_hash, generate_password_hash
from sched.app import database


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    created = DateTimeField(default=datetime.now)
    modified = DateTimeField(default=datetime.now)

    name = CharField(max_length=200)  # Column('name', String(200))
    email = CharField(max_length=100, unique=True, null=False)  # Column(String(100), unique=True, nullable=False)
    active = BooleanField(default=True)  # Column(Boolean, default=True)
    password = CharField(max_length=100)

    def set_password(self, password):
        if password:
            password = password.strip()
        self.password = generate_password_hash(password)

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        return super(User, self).save(*args, **kwargs)

    def check_password(self, password):
        return True
        if self.password is None:
            return False
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def authenticate(cls, email, password):
        email = email.strip().lower()
        user = User.select().where(cls.email == email).get()
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
    created = DateTimeField(default=datetime.now)  # Column(DateTime, default=datetime.now)
    modified = DateTimeField(default=datetime.now)  # Column(DateTime, default=datetime.now, onupdate=datetime.now)

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
    now = datetime.now()

    # Add a sample user.
    user = User(name='Pyunghyuk Yoo',
                email='yoophi@gmail.com',
                )
    user.set_password('secret')
    user.save()

    Appointment(
        user=user,
        title='Important Meeting',
        start=now + timedelta(days=3),
        end=now + timedelta(days=3, seconds=3600),
        allday=False,
        location='The Office',
        description='...',
    ).save()

    Appointment(
        user=user,
        title='Past Meeting',
        start=now - timedelta(days=3, seconds=3600),
        end=now - timedelta(days=3),
        allday=False,
        location='The Office',
        description='...',
    ).save()

    Appointment(
        user=user,
        title='Follow Up',
        start=now + timedelta(days=4),
        end=now + timedelta(days=4, seconds=3600),
        allday=False,
        location='The Office',
        description='...',
    ).save()

    Appointment(
        user=user,
        title='Day Off',
        start=now + timedelta(days=5),
        end=now + timedelta(days=5),
        allday=True,
        location='The Office',
        description='...',
    ).save()
