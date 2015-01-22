from decimal import Decimal
from ftw.shop.interfaces import IShippingRate
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class NullShippingRate(object):
    implements(IShippingRate)
    adapts(Interface)

    title = u'Null Shipping Rate'

    def __init__(self, context):
        self.context = context

    def calculate(self):
        return Decimal(0.0)

    def taxes(self):
        return Decimal(0.0)
