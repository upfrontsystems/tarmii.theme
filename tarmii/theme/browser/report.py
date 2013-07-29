from five import grok
from zope.interface import Interface
from plone.directives import dexterity
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized

grok.templatedir('templates')
class ReportsView(grok.View):
    """ View for reports
    """
    grok.context(Interface)
    grok.name('reports')
    # using report.py and report.pt instead of 
    # reports.pyas we already have a reports
    # folder inside tarmii.theme.browser folder
    grok.template('report') 
    grok.require('zope2.View')

    def user_anonymous(self):
        """ Raise Unauthorized if user is anonymous
        """
        pm = getToolByName(self.context, 'portal_membership')
        if pm.isAnonymousUser():
            raise Unauthorized("You do not have permission to view this page.")
