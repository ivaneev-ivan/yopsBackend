from celery import shared_task
from celery.utils.log import get_task_logger
from yookassa import Payment

from .models import Order

logger = get_task_logger(__name__)


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
