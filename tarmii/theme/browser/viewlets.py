from tarmii.theme import MessageFactory as _
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class TARMIIGlobalSectionsViewlet(GlobalSectionsViewlet):

    index = ViewPageTemplateFile('templates/sections.pt')

    def update(self):
        super(TARMIIGlobalSectionsViewlet, self).update()

        self.portal_tabs[0]['name'] = self.context.translate(_(u'Actvities'))
        self.portal_tabs[1]['name'] = self.context.translate(_(u'Resources'))
        self.portal_tabs[2]['name'] = self.context.translate(_(u'Videos'))
        self.portal_tabs[3]['name'] = self.context.translate(_(u'Classlists'))
        self.portal_tabs[4]['name'] = self.context.translate(_(u'Assessments'))
        self.portal_tabs[5]['name'] = self.context.translate(_(u'Evaluations'))
