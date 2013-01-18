import os
import random
from OFS.Image import Image
from cStringIO import StringIO
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
        # user original @@new-user form without some fields
        originalFields = super(TARMIIAddUserForm, self).form_fields
        originalFields = originalFields.omit('password')
        originalFields = originalFields.omit('password_ctl')
        originalFields = originalFields.omit('groups')

        # use TARMIIUserDataSchema (that also inherits from UserDataSchema)
        # but remove fields that would cause duplicate field errors.
        newFields = form.Fields(ITARMIIUserDataSchema)
        newFields = newFields.omit('fullname') # originalfields already has it
        newFields = newFields.omit('email') # originalfields already has it
        newFields = newFields.omit('home_page')
        newFields = newFields.omit('home_page')
        newFields = newFields.omit('description')
        newFields = newFields.omit('location')
        newFields = newFields.omit('pdelete')

        # merge 
        allFields = originalFields + newFields
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

        pm = getToolByName(self.context, 'portal_membership')
        pmdata = getToolByName(self.context, 'portal_memberdata')
        # if no custom user portrait has been supplied
        if pm.getPersonalPortrait(id=user_id).id == 'defaultUser.png':
            # set the portrait to one of a few random avatars in tarmii theme
            num = str(random.randint(1,24))
            path = '++theme++tarmii.theme/images/avatars/avatar' + num + '.png'
            image = self.context.restrictedTraverse(path)
            fullpath = image.path
            f = open(fullpath, "rb")
            fileRawData = f.read()
            portrait = Image(id=user_id, file=fileRawData, title='')
            pmdata._setPortrait(portrait, user_id)
            f.close()

        IStatusMessage(self.request).addStatusMessage(
            _(u"Profile created."), type='info')

        # Fire PropertiesUpdatedEvent since Plone doesn't
        acl_users = getToolByName(self.context, 'acl_users')
        user = acl_users.getUser(user_id)
        notify(PropertiesUpdated(user, {}))

        # XXX CHANGE REDIRECT TO PROFILES LISTING
        self.request.response.redirect(self.context.absolute_url())

