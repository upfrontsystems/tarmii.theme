from tarmii.theme import MessageFactory as _
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class TARMIIGlobalSectionsViewlet(GlobalSectionsViewlet):

    index = ViewPageTemplateFile('templates/sections.pt')
