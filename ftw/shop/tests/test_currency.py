from decimal import Decimal
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.testing import FTW_SHOP_INTEGRATION_TESTING
from ftw.shop.testing import FTW_SHOP_FUNCTIONAL_TESTING
from ftw.shop.tests.base import FtwShopTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.app.testing import pushGlobalRegistry
from plone.app.testing import popGlobalRegistry
import unittest


class TestCurrency(FtwShopTestCase):

    layer = FTW_SHOP_FUNCTIONAL_TESTING

    def test_which_is_default_currency(self):
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        self.assertEquals(shop_config.currency,
            'CHF')
        self.c_name = getMultiAdapter((self.movie, self.portal.REQUEST),
            name='selected_currency_name')

        self.assertEquals(self.c_name(), 'CHF')

    def test_eur_as_currency(self):
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        shop_config.currency = 'EUR'

        self.c_name = getMultiAdapter((self.movie, self.portal.REQUEST),
            name='selected_currency_name')

        self.assertEquals(self.c_name(), 'Eur')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCurrency))
    return suite
