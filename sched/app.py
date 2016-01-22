import os

from flask import Flask
from flask import abort, jsonify, redirect, render_template, request, url_for
from flask.ext.login import LoginManager, current_user
from flask.ext.login import login_user, login_required, logout_user
from peewee import SqliteDatabase

from sched import filters
from sched.forms import AppointmentForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'enydM2ANhdcoKwdVa0jWvEsbPFuQpMjf'

# Use Flask-SQLAlchemy for its engine and session configuration. Load the
# extension, giving it the app object, and override its default Model class
# with the pure SQLAlchemy declarative Base class.
DATABASE = os.path.join(os.path.dirname(__file__), 'sched.db')
database = SqliteDatabase(DATABASE)

from sched.models import Appointment, User

# Use Flask-Login to track the current user in Flask's session.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to see your appointments.'


@login_manager.user_loader
def load_user(user_id):
    """Hook for Flask-Login to load a User instance from a user ID."""
    return User.select().where(User.id == user_id).get()


# Load custom Jinja filters from the `filters` module.
filters.init_app(app)


@app.errorhandler(404)
def error_not_found(error):
    """Render a custom template when responding with 404 Not Found."""
    return render_template('error/not_found.html'), 404


@app.route('/appointments/')
@login_required
def appointment_list():
    """Provide HTML page listing all appointments in the database."""
    # Query: Get all Appointment objects, sorted by the appointment date.
    appts = Appointment.select().where(Appointment.user == current_user.id).order_by(Appointment.start.asc())
    return render_template('appointment/index.html', appts=appts)


@app.route('/appointments/<int:appointment_id>/')
@login_required
def appointment_detail(appointment_id):
    """Provide HTML page with all details on a given appointment."""
    # Query: get Appointment object by ID.
    appt = Appointment.get(Appointment.id == appointment_id)
    if appt is None or appt.user_id != current_user.id:
        # Abort with Not Found.
        abort(404)
    return render_template('appointment/detail.html', appt=appt)


@app.route('/appointments/create/', methods=['GET', 'POST'])
@login_required
def appointment_create():
    """Provide HTML form to create a new appointment record."""
    form = AppointmentForm(request.form)
    if request.method == 'POST' and form.validate():
        appt = Appointment()
        form.populate_obj(appt)
        appt.user = current_user.id
        appt.save()
        # Success. Send the user back to the full appointment list.
        return redirect(url_for('appointment_list'))
    # Either first load or validation error at this point.
    return render_template('appointment/edit.html', form=form)


@app.route('/appointments/<int:appointment_id>/edit/', methods=['GET', 'POST'])
@login_required
def appointment_edit(appointment_id):
    """Provide HTML form to edit a given appointment."""
    # appt = db.session.query(Appointment).get(appointment_id)
    appt = Appointment.select().where(Appointment.id == appointment_id).get()
    if appt is None:
        abort(404)
    if appt.user_id != current_user.id:
        abort(403)
    form = AppointmentForm(request.form, appt)
    if request.method == 'POST' and form.validate():
        form.populate_obj(appt)
        appt.save()
        # Success. Send the user back to the detail view of that appointment.
        return redirect(url_for('appointment_detail', appointment_id=appt.id))
    return render_template('appointment/edit.html', form=form)


@app.route('/appointments/<int:appointment_id>/delete/', methods=['DELETE'])
@login_required
def appointment_delete(appointment_id):
    """Delete a record using HTTP DELETE, respond with JSON for JavaScript."""
    appt = Appointment.select().where(Appointment.id == appointment_id).get()
    if appt is None:
        # Abort with simple response indicating appointment not found.
        response = jsonify({'status': 'Not Found'})
        response.status_code = 404
        return response
    if appt.user_id != current_user.id:
        # Abort with simple response indicating forbidden.
        response = jsonify({'status': 'Forbidden'})
        response.status_code = 403
        return response
    appt.delete_instance()
    return jsonify({'status': 'OK'})


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('appointment_list'))
    form = LoginForm(request.form)
    error = None
    if request.method == 'POST' and form.validate():
        email = form.username.data.lower().strip()
        password = form.password.data.lower().strip()
        user, authenticated = User.authenticate(email, password)
        if authenticated:
            login_user(user)
            return redirect(url_for('appointment_list'))
        else:
            error = 'Incorrect username or password. Try again.'
    return render_template('user/login.html', form=form, error=error)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))
