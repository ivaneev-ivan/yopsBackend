from __future__ import absolute_import, unicode_literals
import os
from kombu import Exchange, Queue
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
#
# app.conf.task_default_queue = 'default'
# app.conf.task_queues = (
#     Queue('default', routing_key='task.#'),
#     Queue('orders', routing_key='orders.#'),
# )
# app.conf.task_default_exchange = 'tasks'
# app.conf.task_default_exchange_type = 'topic'
# app.conf.task_default_routing_key = 'task.default'

default_queue_name = 'default'
default_exchange_name = 'default'
default_routing_key = 'default'

sunshine_queue_name = 'sunshine'
sunshine_routing_key = 'sunshine'

moon_queue_name = 'moon'
moon_routing_key = 'moon'

default_exchange = Exchange(default_exchange_name, type='direct')
default_queue = Queue(
    default_queue_name,
    default_exchange,
    routing_key=default_routing_key)

server = Queue(
    sunshine_queue_name,
    default_exchange,
    routing_key=sunshine_routing_key)

payment = Queue(
    moon_queue_name,
    default_exchange,
    routing_key=moon_queue_name)

app.conf.task_queues = (default_queue, server, payment)

app.conf.task_default_queue = default_queue_name
app.conf.task_default_exchange = default_exchange_name
app.conf.task_default_routing_key = default_routing_key

app.conf.beat_schedule = {
    'check_payments': {
        'task': 'orders.tasks.check_payments',
        'schedule': 10.0
    }
}

