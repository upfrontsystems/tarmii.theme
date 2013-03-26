from zope.interface import Interface
from five import grok

from plone.app.layout.navigation.interfaces import INavigationRoot
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
                     ('nr', u'isiNdebele'),
                     ('xh', u'isiXhosa'),
                     ('zu', u'isiZulu'),
                     ('st', u'SeSotho'),
                     ('x-nso', u'SePedi'),
                     ('tn', u'Setswana'),
                     ('ss', u'siSwati'),
                     ('ve', u'Tshivenda'),
                     ('ts', u'Xitsonga')]
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

