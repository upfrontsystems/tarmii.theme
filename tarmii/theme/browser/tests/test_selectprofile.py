from plone.uuid.interfaces import IUUID
from Products.CMFPlone.PloneBatch import Batch
from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestSelectProfileView(TarmiiThemeTestBase):
    """ Test Select Profile browser view
    """

    def test_update(self):
        view = self.portal.restrictedTraverse('@@select-profile')
        self.request.set('username', "")
        self.assertEqual(view.update(),None)
        self.request.set('username', "Joe")
        self.assertEqual(view.update(),'http://nohost/plone/logged_in')

    def test_profiles(self):
        view = self.portal.restrictedTraverse('@@select-profile')
        ref_data = [{'username': 'test_user_1_',
                     'fullname': '',
                     'avatar': 'http://nohost/plone/defaultUser.png'}]
        self.assertEqual(view.profiles(),ref_data)

    def test_create_profile_link(self):
        view = self.portal.restrictedTraverse('@@select-profile')
        self.assertEqual(view.create_profile_link(),
                        'http://nohost/plone/@@tarmii-new-user')

    def test_select_profile_url(self):
        view = self.portal.restrictedTraverse('@@select-profile')
        self.assertEqual(view.select_profile_url(),'http://nohost/plone')

    def test_language_cookie_status(self):
        view = self.portal.restrictedTraverse('@@select-profile')
        self.request.cookies['PREFERRED_LANGUAGE'] = ''
        self.assertEqual(view.language_cookie_status(),False)
        self.request.cookies['PREFERRED_LANGUAGE'] = 'xx'
        self.assertEqual(view.language_cookie_status(),True)

    def test_languages(self):
        view = self.portal.restrictedTraverse('@@select-language')
        ref = [{'link': u'Afrikaans',
               'setlink': 'http://nohost/plone/@@set-language?set_language=af'},
               {'link': u'English',
               'setlink': 'http://nohost/plone/@@set-language?set_language=en'},
               {'link': u'isiNdebele',
               'setlink': 'http://nohost/plone/@@set-language?set_language=nr'},
               {'link': u'isiXhosa',
               'setlink': 'http://nohost/plone/@@set-language?set_language=xh'},
               {'link': u'isiZulu',
               'setlink': 'http://nohost/plone/@@set-language?set_language=zu'},
               {'link': u'SeSotho',
               'setlink': 'http://nohost/plone/@@set-language?set_language=st'},
               {'link': u'SePedi',
            'setlink': 'http://nohost/plone/@@set-language?set_language=x-nso'},
               {'link': u'Setswana',
               'setlink': 'http://nohost/plone/@@set-language?set_language=tn'},
               {'link': u'siSwati',
               'setlink': 'http://nohost/plone/@@set-language?set_language=ss'},
               {'link': u'Tshivenda',
               'setlink': 'http://nohost/plone/@@set-language?set_language=ve'},
               {'link': u'Xitsonga',
               'setlink': 'http://nohost/plone/@@set-language?set_language=ts'}]
        self.assertEqual(ref,view.languages())
