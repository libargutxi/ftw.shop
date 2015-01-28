from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.schema.interfaces import IVocabularyFactory
from ftw.shop.interfaces import IShopConfiguration
from Products.Five.browser import BrowserView


class CurrencyView(BrowserView):

    def __call__(self):
        term = self.get_currency()
        return term.title

    def get_currency(self):
        registry = getUtility(IRegistry)
        shop_configuration = registry.forInterface(IShopConfiguration)
        selected_currency = shop_configuration.currency
        vocabulary_factory = getUtility(IVocabularyFactory,
            name=u'ftw.shop.currencies_vocabulary')
        vocabulary = vocabulary_factory(self)
        return vocabulary.getTerm(selected_currency)
