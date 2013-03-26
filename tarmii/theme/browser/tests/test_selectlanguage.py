from plone.uuid.interfaces import IUUID
from Products.CMFPlone.PloneBatch import Batch
from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestSelectLanguageView(TarmiiThemeTestBase):
    """ Test Select Language browser view
    """

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
