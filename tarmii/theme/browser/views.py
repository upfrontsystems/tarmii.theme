from zope.formlib import form
from zope.event import notify

from plone.app.form.validators import null_validator
from plone.app.users.browser.register import AddUserForm
from plone.app.users.browser.personalpreferences import UserDataConfiglet

from AccessControl import getSecurityManager
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.PluggableAuthService.events import PropertiesUpdated 

from zExceptions import Forbidden

from tarmii.theme import MessageFactory as _
from tarmii.theme.userdataschema import ITARMIIUserDataSchema

class TARMIIUserDataConfiglet(UserDataConfiglet):

    def __init__(self, context, request):
        super(TARMIIUserDataConfiglet, self).__init__(context, request)
        self.form_fields = self.form_fields.omit('home_page')
        self.form_fields = self.form_fields.omit('description')
        self.form_fields = self.form_fields.omit('location')
        self.form_fields = self.form_fields.omit('portrait')
        self.form_fields = self.form_fields.omit('pdelete')


class TARMIIAddUserForm(AddUserForm):

    label = _(u'heading_add_user_form', default=u'Create Profile')

    @property
    def form_fields(self):
        allFields = form.Fields(ITARMIIUserDataSchema)
        allFields = allFields.omit('home_page')
        allFields = allFields.omit('description')
        allFields = allFields.omit('location')
        allFields = allFields.omit('portrait')
        allFields = allFields.omit('pdelete')
        return allFields    

    @form.action(_(u'label_register', default=u'Register'),
                 validator='validate_registration', name=u'register')
    def action_join(self, action, data):
        """ Override Plone's AddUserForm so that we can fire
            the PropertiesUpdated event and redirect to select profile page
        """
        super(AddUserForm, self).handle_join_success(data)

        portal_groups = getToolByName(self.context, 'portal_groups')
        user_id = data['username']
        is_zope_manager = getSecurityManager().checkPermission(
            ManagePortal, self.context)

        try:
            # Add user to the selected group(s)
            if 'groups' in data.keys():
                for groupname in data['groups']:
                    group = portal_groups.getGroupById(groupname)
                    if 'Manager' in group.getRoles() and not is_zope_manager:
                        raise Forbidden
                    portal_groups.addPrincipalToGroup(user_id, groupname,
                                                      self.request)
        except (AttributeError, ValueError), err:
            IStatusMessage(self.request).addStatusMessage(err, type="error")
            return

        IStatusMessage(self.request).addStatusMessage(
            _(u"Profile created."), type='info')

        # Fire PropertiesUpdatedEvent since Plone doesn't
        acl_users = getToolByName(self.context, 'acl_users')
        user = acl_users.getUser(user_id)
        notify(PropertiesUpdated(user, {}))

        # XXX CHANGE REDIRECT TO PROFILES LISTING
        self.request.response.redirect(self.context.absolute_url())
