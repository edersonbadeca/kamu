import datetime
import os

from celery import Celery

from django.conf import settings
from books import tasks

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kamu.settings')
app = Celery('kamu')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(0.5, tasks.send_borrows_out_of_time_notification, name='add every 10')


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'books.tasks.send_borrows_out_of_time_notification',
        'schedule': 0.5
    },
}
app.conf.timezone = 'UTC'
