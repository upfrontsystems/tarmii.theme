from five import grok
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName

from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class HomeView(grok.View):
    """ View to display the front page
    """
    grok.context(Interface)
    grok.name('home')
    grok.template('home')
    grok.require('cmf.SetOwnProperties')

    def portal_root(self):
        """ URL for the portal
        """
        return self.context.absolute_url()

    def members_folder(self):
        """ URL for the members folder
        """
        pm = getToolByName(self.context, 'portal_membership')        
        return pm.getHomeUrl()
