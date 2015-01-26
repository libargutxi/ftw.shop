from decimal import Decimal
from ftw.builder import Builder
from ftw.builder import create
from ftw.shop.interfaces import IShippingRate
from ftw.shop.interfaces import IShopConfiguration
from ftw.shop.interfaces import IShopRoot
from ftw.shop.testing import FTW_SHOP_FUNCTIONAL_TESTING
from ftw.shop.testing import FTW_SHOP_WITH_SHIPPING_FUNCTIONAL_TESTING
from ftw.shop.tests.pages import checkout
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.component import provideAdapter
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
import email
import email.header
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry


class ShippingRateTest(object):
    implements(IShippingRate)

    def __init__(self, context):
        self.context = context

    def calculate(self):
        return Decimal('3.3')

    def taxes(self):
        return Decimal('1.1')


class TestCheckoutMailToCustomerWithShipping(TestCase):

    layer = FTW_SHOP_WITH_SHIPPING_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestCheckoutMailToCustomerWithShipping, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        alsoProvides(self.portal, IShopRoot)
        create(Builder('cart portlet'))
        Mailing(self.portal).set_up()

    def checkout_and_get_mail(self, *items):
        mailing = Mailing(self.portal)
        for item in items:
            checkout.visit_checkout_with_one_item_in_cart(item)
        checkout.goto(checkout.ORDER_REVIEW).finish()
        self.assertEquals(1, len(mailing.get_messages()),
                          'Notifying shop owner is disabled by default, therefore'
                          ' only one mail (to the customer) should be sent.')
        return email.message_from_string(mailing.pop())

    def open_mail_in_browser(self, mail, browser):
        browser.open_html(mail.get_payload(decode=True))

    @browsing
    def test_shipping_costs_in_customer_mail(self, browser):

        vocabulary_factory = getUtility(IVocabularyFactory,
            name=u'ftw.shop.shipping_rates')
        vocabulary = vocabulary_factory(self)
        self.assertTrue(
            vocabulary.getTerm(u'ftw.shop.TestShippingRate33') is not None)

        registry = getUtility(IRegistry)
        shop_config = registry.forInterface(IShopConfiguration)
        shop_config.shipping_rate = u'ftw.shop.TestShippingRate33'
        self.assertTrue(shop_config.shipping_rate,
            u'ftw.shop.TestShippingRate33')

        items = [create(Builder('shop item').having(price='10.00'))]

        self.open_mail_in_browser(self.checkout_and_get_mail(*items), browser)

        footer_rows = browser.css('table tfoot tr')
        shipping_rate_row = footer_rows[1]
        shipping_taxes_row = footer_rows[2]
        self.assertTrue(u'Shipping rate' in shipping_rate_row.css('td')[0].text)
        self.assertTrue(u'3.3' in shipping_rate_row.css('td')[4].text)
        self.assertTrue(u'Shipping taxes' in shipping_taxes_row.css('td')[0].text)
        self.assertTrue(u'1.1' in shipping_taxes_row.css('td')[4].text)

        shop_config.shipping_rate = u'ftw.shop.NullShippingRate'
