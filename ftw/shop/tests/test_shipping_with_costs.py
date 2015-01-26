from decimal import Decimal
from ftw.shop.interfaces import IShippingRate
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.testing import FTW_SHOP_INTEGRATION_TESTING
from ftw.shop.tests.base import FtwShopTestCase
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.registry.interfaces import IRegistry
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import provideAdapter
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
import unittest


class ShippingRateTest(object):
    implements(IShippingRate)

    def __init__(self, context):
        self.context = context

    def calculate(self):
        return Decimal('3.3')

    def taxes(self):
        return Decimal('1.1')


class TestShippingRateWithShippingCosts(FtwShopTestCase):

    layer = FTW_SHOP_INTEGRATION_TESTING

    def testSetUp(self):
        portal = self.layer['portal']
        pushGlobalRegistry(portal)

    def testTearDown(self):
        portal = self.layer['portal']
        popGlobalRegistry(portal)

    def test_specific_shipping_rate(self):
        provideAdapter(ShippingRateTest,
            (Interface,),
            IShippingRate,
            name=u'ftw.shop.TestShippingRate33')
        vocabulary_factory = getUtility(IVocabularyFactory,
            name=u'ftw.shop.shipping_rates')
        vocabulary = vocabulary_factory(self)
        self.assertTrue(
            vocabulary.getTerm(u'ftw.shop.TestShippingRate33') is not None)

        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        shop_config.shipping_rate = u'ftw.shop.TestShippingRate33'
        # transaction.savepoint(optimistic=True)

        self.cart = getMultiAdapter((self.movie, self.portal.REQUEST),
            name='cart_view')
        self.cart.addtocart("12345", quantity=1)

        self.assertEquals(self.cart.cart.get_shipping_costs(),
            Decimal('3.3') + Decimal('1.1'))

        self.assertEquals(Decimal(self.cart.cart_total()),
            Decimal('7.15') + Decimal('3.3') + Decimal('1.1'))

        shop_config.shipping_rate = u'ftw.shop.NullShippingRate'
        # undo our registration so we don't break tests
        components = getGlobalSiteManager()
        components.unregisterAdapter(ShippingRateTest,
            (Interface,),
            IShippingRate,
            name=u'ftw.shop.TestShippingRate33')
        # transaction.abort()

    # def setUp(self):
    #     super(TestShippingRateWithShippingCosts, self).setUp()
    #     # with ploneSite() as portal:
    #     #     pushGlobalRegistry(portal, new=None)

    # def tearDown(self):
    #     super(TestShippingRateWithShippingCosts, self).tearDown()
    #     # with ploneSite() as portal:
    #     #     popGlobalRegistry(portal)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestShippingRateWithShippingCosts))
    return suite
