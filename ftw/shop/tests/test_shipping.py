from decimal import Decimal
from ftw.shop.interfaces import IShippingRate
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.tests.base import FtwShopTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory


class ShippingRateTest(object):
    implements(IShippingRate)

    def __init__(self, context):
        self.context = context

    def calculate(self):
        return Decimal('3.3')

    def taxes(self):
        return Decimal('1.1')


class TestShippingRate(FtwShopTestCase):

    def afterSetUp(self):
        super(TestShippingRate, self).afterSetUp()

    def add_something_to_cart(self):
        # Add an item with no variations to cart
        self.cart = getMultiAdapter((self.movie, self.portal.REQUEST),
            name='cart_view')
        self.cart.addtocart("12345", quantity=1)

    def test_which_is_default_shipping_rate(self):
        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        self.assertEquals(shop_config.shipping_rate,
            u'ftw.shop.NullShippingRate')

    def test_default_null_shipping_rate(self):
        self.add_something_to_cart()
        self.assertEquals(self.cart.cart.get_shipping_costs(), Decimal(0.0))

    def test_specific_shipping_rate(self):
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(factory=ShippingRateTest,
            required=(Interface,),
            name=u'ftw.shop.TestShippingRate33', provided=IShippingRate)

        vocabulary_factory = getUtility(IVocabularyFactory,
            name=u'ftw.shop.shipping_rates')
        vocabulary = vocabulary_factory(self)
        self.assertTrue(
            vocabulary.getTerm(u'ftw.shop.TestShippingRate33') is not None)

        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        shop_config = registry.forInterface(IShopConfiguration)
        shop_config.shipping_rate = u'ftw.shop.TestShippingRate33'

        self.add_something_to_cart()
        self.assertEquals(self.cart.cart.get_shipping_costs(),
            Decimal('3.3') + Decimal('1.1'))

        self.assertEquals(Decimal(self.cart.cart_total()),
            Decimal('7.15') + Decimal('3.3') + Decimal('1.1'))
