#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from celery import Celery
# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings.local')

app = Celery('cms')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    # 'send-certificate-expired-notice': {
    #     'task': 'apps.users_services.tasks.certificate_notice',
    #     'schedule': crontab(minute=0, hour=8),
    #     'args': (),
    # },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
