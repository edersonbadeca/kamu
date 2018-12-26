import datetime
import os

from celery import Celery

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kamu.settings')
app = Celery('kamu')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(60, tasks.send_borrows_out_of_time_notifications, name='add every 10')


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'books.tasks.send_borrows_out_of_time_notifications',
        'schedule': 60
    },
}
app.conf.timezone = 'UTC'
