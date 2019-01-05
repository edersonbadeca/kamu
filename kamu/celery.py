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
    sender.add_periodic_task(settings.CELERY_TASK_FREQUENCY, tasks.send_borrows_out_of_time_notifications, name='Notification task')


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {
    'Scheduling Notification task': {
        'task': 'books.tasks.send_borrows_out_of_time_notifications',
        'schedule': settings.CELERY_TASK_FREQUENCY
    },
}
app.conf.timezone = 'UTC'
