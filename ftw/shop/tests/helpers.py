from decimal import Decimal
from ftw.shop.interfaces import IShippingRate
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
import email.header
import operator


def get_mail_header(msg, name):
    return map(operator.itemgetter(0), email.header.decode_header(msg.get(name)))


class ShippingRateTest(object):
    implements(IShippingRate)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def calculate(self):
        return Decimal('3.3')

    def taxes(self):
        return Decimal('1.1')
