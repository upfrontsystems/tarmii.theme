from tarmii.theme import MessageFactory as _
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class TARMIIGlobalSectionsViewlet(GlobalSectionsViewlet):

    def update(self):
        super(TARMIIGlobalSectionsViewlet, self).update()
        
        for x in range(len(self.portal_tabs)):
            self.portal_tabs[x]['name'] =\
                self.context.translate(_(self.portal_tabs[x]['name']))
                # the translations labels: Topic Trees, Evaluations
                # etc, are defined in actions.xml
