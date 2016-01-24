from datetime import datetime
from flask.ext.security import RoleMixin
from flask.ext.security import UserMixin
from peewee import DateTimeField, CharField, BooleanField, ForeignKeyField, TextField
from werkzeug.security import check_password_hash, generate_password_hash
from sched.app import database


class Role(database.Model, RoleMixin):
    name = CharField(unique=True)
    description = TextField(null=True)


class User(database.Model, UserMixin):
    email = CharField(max_length=100, unique=True, null=False)
    active = BooleanField(default=True)
    password = CharField(max_length=100)
    active = BooleanField(default=True)
    confirmed_at = DateTimeField(null=True)

    created = DateTimeField(default=datetime.now)
    modified = DateTimeField(default=datetime.now)

    name = CharField(max_length=200)

    def set_password(self, password):
        if password:
            password = password.strip()
        self.password = generate_password_hash(password)

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
    def authenticate(cls, email, password):
        email = email.strip().lower()
        try:
            user = User.select().where(cls.email == email).get()
        except cls.DoesNotExist:
            user = None

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


class UserRoles(database.Model):
    # Because peewee does not come with built-in many-to-many
    # relationships, we need this intermediary class to link
    # user to roles.
    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)


class Appointment(database.Model):
    """An appointment on the calendar."""
    created = DateTimeField(default=datetime.now)
    modified = DateTimeField(default=datetime.now)

    user = ForeignKeyField(User)

    title = CharField()
    start = DateTimeField()
    end = DateTimeField()
    allday = BooleanField()
    location = CharField()
    description = TextField()

    def save(self, *args, **kwargs):
        self.modified = datetime.now()
        return super(Appointment, self).save(*args, **kwargs)

    @property
    def duration(self):
        delta = self.end - self.start
        return delta.days * 24 * 60 * 60 + delta.seconds

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.id}>'.format(self=self)
