from tarmii.theme import MessageFactory as _
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class TARMIIGlobalSectionsViewlet(GlobalSectionsViewlet):

    index = ViewPageTemplateFile('templates/sections.pt')

    def update(self):
        super(TARMIIGlobalSectionsViewlet, self).update()
        
        for x in range(len(self.portal_tabs)):
            self.portal_tabs[x]['name'] =\
                self.context.translate(_('action_' + self.portal_tabs[x]['id']))
                # the translations labels: action_topictree, action_evaluations
                # etc, are defined in actions.xml
