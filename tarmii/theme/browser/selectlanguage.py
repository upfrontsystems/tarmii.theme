from five import grok
from zope.interface import Interface
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName
from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class SelectLanguageView(grok.View):
    """ View for the changing of site language
    """
    grok.context(Interface)
    grok.name('select-language')
    grok.template('selectlanguage')
    grok.require('zope2.View')

    def languages(self):
        """ Data to populate language switcher 
        """
        languages = [('af', u'Afrikaans'),
                     ('en', u'English'),
                     ('nr', u'IsiNdebele'),
                     ('xh', u'IsiXhosa'),
                     ('zu', u'IsiZulu'),
                     ('st', u'seSotho sa Leboa (Sepedi)'),
                     ('tn', u'Setswana'),
                     ('ss', u'SiSwati'),
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


class SetLanguageView(grok.View):
    """ Set our custom language cookie and plone's language cookie.
    """
    grok.context(Interface)
    grok.name('set-language')
    grok.require('zope2.View')

    def __call__(self):
        """ Set our custom language cookie and plone's language cookie
        """
        i18ncode = self.request.get('set_language')
        self.request.response.setCookie("I18N_LANGUAGE", i18ncode)
        self.request.response.setCookie("PREFERRED_LANGUAGE", i18ncode)
        return self.request.response.redirect(
                '/'.join(self.context.getPhysicalPath()))

    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''
