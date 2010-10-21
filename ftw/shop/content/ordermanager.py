from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from ftw.shop.config import PROJECTNAME
from ftw.shop.config import SESSION_ADDRESS_KEY, SESSION_ORDERS_KEY 
from ftw.shop.exceptions import MissingCustomerInformation, MissingOrderConfirmation
from DateTime import DateTime
from email import message_from_string
from email.Header import Header
from email.Utils import formataddr

from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATBTreeFolder
from Products.ATContentTypes.content.folder import ATBTreeFolderSchema
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.MailHost.MailHost import MailHostError
from zope.component import getMultiAdapter
import socket
import logging
logger  = logging.getLogger('ftw.shop')

schema = atapi.Schema((
    atapi.IntegerField('next_order_id',
        default=1,
        widget=atapi.IntegerWidget(
            label="Next Order ID",
            label_msgid='PloneMallOrder_label_next_order_id',
            description='Enter a value for Next Order ID.',
            description_msgid='PloneMallOrder_help_next_order_id',
            i18n_domain='plonemallorder',
        ),
        required=1,
    ),   
),
)


class OrderManager(UniqueObject, ATBTreeFolder):
    """
    Order Manager
    """
    security = ClassSecurityInfo()
    meta_type = 'OrderManager' 
    schema = ATBTreeFolderSchema + schema

    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        ATBTreeFolder.__init__(self,'portal_ordermanager')


    security.declareProtected("Buy item", 'addOrder')
    def addOrder(self):
        '''
        Add a new Order and returns the order id.
        '''
 
        session = self.REQUEST.SESSION

        # check for cart
        cart_view = getMultiAdapter((self, self.REQUEST), name=u'cart_view')
        cart_data = cart_view.cart_items()
       
        # check for customer data
        customer_data = session.get(SESSION_ADDRESS_KEY, {})
        if not customer_data:
            raise MissingCustomerInformation
        
        # check for order confirmation
        if not session.get('order_confirmation', None):
            raise MissingOrderConfirmation            

        # calculate the next order id
        order_id = self.getNextOrderId()
        
        # change security context to owner
        user = self.getWrappedOwner()
        newSecurityManager(self.REQUEST, user)
        
        # create Order
        self.invokeFactory('ShopOrder', id=order_id)
        order = getattr(self, str(order_id))

        # calc order number
        now  = DateTime()
        order_number = '%03d%s%04d' % (now.dayOfYear()+500, now.yy(), order_id )

        order.setTitle(order_number)
 
        # store customer data
        order.setCustomerData(customer_data)

        # store cart in order
        order.setCartData(cart_data)
        order.setTotal(cart_view.cart_total())

        # now send a mail confirming the order
        self.sendOrderMail(order_id)

        noSecurityManager()
        
        return order_number

    security.declareProtected("Manage", 'sendOrderMail')
    def sendOrderMail(self, orderid):
        """
        Send order confirmation mail of the order with the specified orderid.
        Can be used if initial sending of order mail failed for some reason.
        """
        order = getattr(self, str(orderid))
        
        customer = order.getCustomerData()
        
        fullname = "%s %s" % (customer.get('firstname'),customer.get('lastname'))
        mailTo = formataddr((fullname, customer.get('email')))
        mailFrom = 'no_reply@4teamwork.ch'
        mailSubject = '4teamwork Webshop'

        # get values from properties
        ltool = getToolByName(self, 'portal_languages')
        lang = ltool.getPreferredLanguage()
        properties = getToolByName(self, 'portal_properties', None)
        shop_props = getattr(properties, 'shop_properties', None)
        mailBcc = ''
        if shop_props is not None:
            mailFrom = shop_props.getProperty('mail_from', mailFrom)
            mailBcc = shop_props.getProperty('mail_bcc', mailBcc)
            mailSubject = shop_props.getProperty('mail_subject_%s' % lang, mailSubject)

        mhost = self.MailHost
        mail_view = getMultiAdapter((order,order.REQUEST), name=u'mail_view')
        msg_body = mail_view()

        try:
            # Plone 4
            msg = message_from_string(msg_body.encode('utf-8'))
            msg['BCC']= Header(mailBcc)
            msg.set_charset('utf-8')
            mhost.send(msg,
                         mto=mailTo,
                         mfrom=mailFrom,
                         subject=mailSubject,
                         encode=None,
                         immediate=False,
                         msg_type='text/html',
                         charset='utf8')
        except TypeError:
            # BBB: For Plone 3
            mhost.secureSend(msg_body,
                             mto=mailTo,
                             mfrom=mailFrom,
                             subject=mailSubject,
                             mbcc=mailBcc,
                             subtype='html',
                             charset='utf-8')
            
        except (MailHostError, socket.error), e:
            logger.error("sending mail for order %s failed: %s." % (order.getOrderNumber(),str(e)))

        return

    security.declareProtected("View", 'getOrderById')
    def getOrderById(self, order_id):
        '''
        Return an Order by its order id.
        '''

        return self._getOb(str(order_id), None)
    

    def getNextOrderId(self):
        currid=self.getNext_order_id()
        nextid=int(currid) + 1
        self.setNext_order_id(nextid)
        return currid

def getRfcHeaderValue(value):
    header = None
    try:
        header = Header(value, 'ascii')
    except:
        header = Header(value, 'iso-8859-1')
    return str(header)

atapi.registerType(OrderManager, PROJECTNAME)