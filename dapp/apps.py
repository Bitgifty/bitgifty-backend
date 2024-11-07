import os

from django.apps import AppConfig


class DappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dapp'

    def ready(self):
        from . import jobs

        if (
            os.environ.get('RUN_MAIN', None) != 'true'
        ) and (
            os.environ['DEBUG'] != 'True'
        ) and os.environ.get('CELERY', 'True') != 'True':
            jobs.start_scheduler()
