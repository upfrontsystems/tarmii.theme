from zope.interface import Interface
from five import grok

from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite

grok.templatedir('templates')

class SelectProfileView(grok.View):
    """ View for displaying all non-admin users in the system and allowing users
        to log in with a click.
    """
    grok.context(Interface)
    grok.name('select-profile')
    grok.template('selectprofile')
    grok.require('zope2.View')

    #  __call__ calls update before generating the template
    def update(self, **kwargs):
        """ if one of the select profile buttons has been submitted, log that 
            user in
        """
        if self.request.form.has_key('buttons.profile.login.submit'):
            username = self.request.form['buttons.profile.login.submit']
            self.context.acl_users.session._setupSession(username,
                                                self.context.REQUEST.RESPONSE)
            self.request.RESPONSE.redirect(self.context.absolute_url())
            acl = getSite().acl_users
            acl.credentials_cookie_auth.login_path = '@@select-profile'

    def profiles(self):
        """ Return all non-admin users in the system.
        """

        pm = getToolByName(self.context, 'portal_membership')

        #get all users that are do not have the Site Administrator role.
        non_admins = [member for member in pm.listMembers()
                if not member.has_role('Site Administrator')]

        return non_admins
