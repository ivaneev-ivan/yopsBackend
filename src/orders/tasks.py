from celery import shared_task
from celery.utils.log import get_task_logger
from yookassa import Payment
from django.conf import settings

from .models import Order

import json
import os
import time

from celery import shared_task
from celery.utils.log import get_task_logger
from orders.deployment_services import VPNDeployment, RemoteCmdExecutor
from orders.models import Order, OrderOutline, ConfigKey
import requests
from yookassa import Payment

logger = get_task_logger(__name__)


class OrderTitleIsNotAllowed(Exception):
    pass


class PaymentIsLow(Exception):
    pass


@shared_task(autoretry_for=(OrderTitleIsNotAllowed, PaymentIsLow), retry_kwargs={'max_retries': 7, 'countdown': 60})
def create_server_for_order(order_id: int):
    logger.info("Create server for order")
    order = Order.objects.get(pk=order_id)
    server_location = order.location.title.lower()
    url = "https://api.timeweb.cloud/api/v1/servers"
    payload = {
        "os_id": 61,
        "configuration": {
            "configurator_id": 11,
            "disk": 10240,
            "cpu": 1,
            "ram": 1024
        },
        "name": f"Заказ #{order.pk} {server_location}",
        "bandwidth": 200,
        "is_ddos_guard": False
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.TIMEWEB_TOKEN}'
    }
    print(server_location)
    location = 'spb-1'
    if "Нидерланды".lower() in server_location:
        location = 'ams-1'
    if "Казахстан".lower() in server_location:
        location = 'gdn-1'

    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200 or response.status_code == 201:
        logger.info(f'Order #{order.id} is created')
        data = response.json()
        server_id = data['server']['id']

        while data['server']['status'] != "on":
            logger.info('Сервер не запущен')
            time.sleep(10)
            response = requests.get(f'https://api.timeweb.cloud/api/v1/servers/{server_id}', headers=headers)
            logger.info(response)
            logger.info(response.text)
            data = response.json()

        root_pass = data['server']['root_pass']
        # ip = ''
        # for network in data['server']['networks']:
        #     if network['type'] == 'public':
        #         for ip in network['ips']:
        #             if ip['is_main'] and ip['type'] == 'ipv4':
        #                 ip = ip['ip']
        #                 break
        # Создание ip
        response = response.post('https://api.timeweb.cloud/api/v1/floating-ips', headers=headers, data=json.dumps({
            'is_ddos_guard': False,
            'availability_zone': location
        }))
        ip = response.json()['ip']['ip']
        logger.info(f'Создал ip {ip}')
        response.post(f'https://api.timeweb.cloud/api/v1/servers/{server_id}/ips', headers=headers,
                      data=json.dumps({
                          "type": "ipv4",
                          "ptr": ip
                      }))
        logger.info('Добавил ip')
        data['server']['status'] = 'sleep'
        while data['server']['status'] != "on":
            time.sleep(10)
            response = requests.get(f'https://api.timeweb.cloud/api/v1/servers/{server_id}', headers=headers)
            logger.info(response)
            logger.info3(response.text)
            data = response.json()
        time.sleep(30)
        work = True
        logger.info(f'Start connect to {ip} with password {root_pass}')
        while work:
            try:
                vpn = VPNDeployment(RemoteCmdExecutor(host=ip, password=root_pass), client_count=order.count_configs)
                work = False
            except Exception as ex:
                print(ex)
                time.sleep(30)
        if not vpn.deploy("orders/scripts/install-docker"):
            raise Exception("Error: Installation has failed!")
        if "vpn" in order.services:
            outline = vpn.deploy_outline("orders/scripts/outline-install-helper")
            OrderOutline.objects.create(order=order, apiUrl=outline.json_string['apiUrl'],
                                        certSha256=outline.json_string['certSha256'])
            logger.info("Outline created")
            for i in range(1, order.count_configs + 1):
                logger.info(f"start creating config count {i}")
                response = requests.post(f"{outline.api_root}/access-keys/", verify=False)
                data = response.json()
                ConfigKey.objects.create(name=data['name'], password=data['password'], order=order, port=data['port'],
                                         method=data['method'], accessUrl=data['accessUrl'])
        if "files" in order.services:
            vpn.deploy("orders/scripts/install-nextcloud")
            logger.info("nextcloud created")
        order.status = 'done'
        order.save()
    else:
        raise PaymentIsLow(f'Order #${order.id} is not created: status code="{json.dumps(response.json())}"')


class OrderTitleIsNotAllowed(Exception):
    pass


class PaymentIsLow(Exception):
    pass


@shared_task
def check_payments():
    for order in Order.objects.filter(payment__is_paid=False).all():
        payment = Payment.find_one(order.payment.payment_id)
        if payment.status == "succeeded":
            order.status = "payed"
            order.payment.is_paid = True
            order.save()
            order.payment.save()
            create_server_for_order.apply_async((order.pk,))
