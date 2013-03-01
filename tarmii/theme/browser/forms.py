from five import grok
from zope.component.hooks import getSite
from plone.directives import dexterity
from tarmii.theme import MessageFactory as _
from tarmii.theme.interfaces import ITARMIIThemeLayer

grok.templatedir('templates')
grok.layer(ITARMIIThemeLayer)

class TeacherResourceAddForm(dexterity.AddForm):
    grok.name('tarmii.theme.content.teacherresource')
    grok.layer(ITARMIIThemeLayer)

    def nextURL(self):
        # both save and cancel buttons redirect to the same place
        site = getSite()
        return '%s/resources' % (site.absolute_url())
