from decimal import Decimal
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.testing import FTW_SHOP_INTEGRATION_TESTING
from ftw.shop.tests.base import FtwShopTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.app.testing import pushGlobalRegistry
from plone.app.testing import popGlobalRegistry
import unittest


class TestShippingRate(FtwShopTestCase):

    layer = FTW_SHOP_INTEGRATION_TESTING

    def testSetUp(self):
        portal = self.layer['portal']
        pushGlobalRegistry(portal)

    def testTearDown(self):
        portal = self.layer['portal']
        popGlobalRegistry(portal)

    def test_which_is_default_shipping_rate(self):
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        self.assertEquals(shop_config.shipping_rate,
            u'ftw.shop.NullShippingRate')

    def test_default_null_shipping_rate(self):
        # Add an item with no variations to cart
        self.cart = getMultiAdapter((self.movie, self.portal.REQUEST),
            name='cart_view')
        self.cart.addtocart("12345", quantity=1)
        self.assertEquals(self.cart.cart.get_shipping_costs(), Decimal(0.0))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestShippingRate))
    return suite
