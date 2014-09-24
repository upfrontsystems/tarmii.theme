from zope.interface import Interface
from five import grok

from zope.component import getUtility

from Acquisition import aq_parent, aq_inner, aq_base
from AccessControl import getSecurityManager
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import _checkPermission

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
        username = self.request.get('username', '')
        if username != '':
            self.context.acl_users.session._setupSession(username,
                                                self.context.REQUEST.RESPONSE)
            portal_url = getToolByName(self.context, 'portal_url')()
            return self.request.RESPONSE.redirect('%s/logged_in' % portal_url)

    def profiles(self):
        """ Return all non-admin users in the system.
        """

        pm = getToolByName(self.context, 'portal_membership')

        # get all users that do not have the Site Administrator role.
        non_admins = []
        for member in pm.listMembers():
            if not member.has_role('Site Administrator'):
                non_admins.append(
                    {'username': member.getId(),
                     'fullname': member.getProperty('fullname'),
                     'avatar': pm.getPersonalPortrait(id=member.getId()
                        ).absolute_url()
                    })


        return non_admins

    def create_profile_link(self):
        """ Return url to view used for creating new profiles
        """
        portal_url = getToolByName(self.context, 'portal_url')()
        return '%s/@@tarmii-new-user' % portal_url

    def select_profile_url(self):
        """ Return url to self
        """
        return self.context.absolute_url()

    def language_cookie_status(self):
        """ Return True if the language cookie has been set """
     
        if self.request.cookies.get("PREFERRED_LANGUAGE", "") == "":
            return False
        return True

    def languages(self):
        """ Data to populate language switcher 
        """
        languages = [('af', u'Afrikaans'),
                     ('en', u'English'),
                    # ('nr', u'isiNdebele'),
                    # ('xh', u'isiXhosa'),
                    # ('zu', u'isiZulu'),
                     ('st', u'SeSotho'),
                     ('x-nso', u'SePedi'),
                     ('tn', u'Setswana')]
                    # ('ss', u'siSwati'),
                    # ('ve', u'Tshivenda'),
                    # ('ts', u'Xitsonga')]
        lang_data = []
        context = self.context
        while INavigationRoot.providedBy(context) == False:
            context = context.aq_parent
        for x in languages:
            link = '%s/@@set-language?set_language=%s' %\
                    (context.absolute_url(),x[0])
            lang_data.append(
               {'setlink': link,
                'link': x[1]
               })
        return lang_data


class DeleteUser(grok.View):
    """ custom delete userview
    """
    grok.context(Interface)
    grok.name('delete-user') 
    grok.template('deleteuser')
    grok.require('zope2.View') # because any user can do this

    def username(self):
        return self.request.get('username', '')

    def update(self):
        if not self.request.has_key('form.submitted'):
            return

        # delete user
        pm = getToolByName(self.context, 'portal_membership')
        user_id = self.request.get('username', '')

        # Delete members in acl_users.
        try:
            pm.acl_users.userFolderDelUsers(user_id)
        except (AttributeError, NotImplementedError):
            raise NotImplementedError('The underlying User Folder '
                                     'doesn\'t support deleting members.')

        # Delete member data in portal_memberdata.
        mdtool = getToolByName(self, 'portal_memberdata', None)
        if mdtool is not None:
            mdtool.deleteMemberData(user_id)

        # Delete members' home folders including all content items.
        portal_state = self.context.restrictedTraverse('@@plone_portal_state')
        portal = portal_state.portal()
        members = getattr(portal, 'Members', None)
        if members:
            if hasattr( aq_base(members), user_id):
                members.manage_delObjects(user_id)

        # Delete members' local roles.
        self.deleteLocalRoles( getUtility(ISiteRoot), user_id,
                               reindex=1, recursive=1 )

        # redirect to select-profile view
        portal_state = self.context.restrictedTraverse('@@plone_portal_state')
        portal = portal_state.portal()
        redirect_to = '%s/@@select-profile' % portal.absolute_url()
        self.request.RESPONSE.redirect(redirect_to)

    def deleteLocalRoles(self, obj, member_ids, reindex=1, recursive=0,
                         REQUEST=None):
        """ Delete local roles of specified members.
        """
        for member_id in member_ids:
            if obj.get_local_roles_for_userid(userid=member_id):
                obj.manage_delLocalRoles(userids=member_ids)
                break

        if recursive and hasattr( aq_base(obj), 'contentValues' ):
            for subobj in obj.contentValues():
                self.deleteLocalRoles(subobj, member_ids, 0, 1)

        if reindex and hasattr(aq_base(obj), 'reindexObjectSecurity'):
            # reindexObjectSecurity is always recursive
            obj.reindexObjectSecurity()

