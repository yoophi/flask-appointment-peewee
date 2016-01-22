from flask.ext.script import Manager
from flask.ext.script.commands import ShowUrls

from sched.app import app

manager = Manager(app)
app.config['DEBUG'] = True

manager.add_command('show_urls', ShowUrls)

if __name__ == '__main__':
    manager.run()
