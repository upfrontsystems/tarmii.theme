from zope.interface import Interface
from five import grok

from Products.CMFCore.utils import getToolByName

grok.templatedir('templates')

class SelectProfileView(grok.View):
    """ View for displaying all non-admin users in the system and allowing users
        to log in with a click.
    """
    grok.context(Interface)
    grok.name('select-profile')
    grok.template('selectprofile')
    grok.require('zope2.View')

    def profiles(self):
        """ Return all non-admin users in the system.
        """

        pm = getToolByName(self.context, 'portal_membership')

        #get all users that are do not have the Site Administrator role.
        non_admins = [member for member in pm.listMembers()
                if not member.has_role('Site Administrator')]

        return non_admins

