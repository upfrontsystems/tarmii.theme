from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from Products.CMFCore.utils import getToolByName

from five import grok
from zope.interface import Interface
from zope.component import getUtility
from plone.directives import dexterity

from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class SyncDataView(grok.View):
    """ View to kick off synchronisation manually
    """
    grok.context(Interface)
    grok.name('sync-data')
    grok.template('sync-data')
    grok.require('zope2.View')

    def update(self, **kwargs):
        """ sync data
        """
        if self.request.has_key('submit'):
            # switch to admin user
            pps = self.context.restrictedTraverse('plone_portal_state')
            portal = pps.portal()
            pms = getToolByName(portal, 'portal_membership')
            user = pms.getMemberById('admin')
            sm = getSecurityManager()
            newSecurityManager(None, user)
            for viewname in ('@@synchronise', '@@upload-to-server'):
                view = self.context.restrictedTraverse(viewname)
                view()

            # switch back to current user
            setSecurityManager(sm)
            return self.render()
