from .celery import app as celery_app
celery_app.conf.broker_url = 'redis://redis:6379/0'
__all__ = ['celery_app']
