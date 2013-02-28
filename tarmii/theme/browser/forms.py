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

    # this method needed so we can successfully point our nextURL method
    def createAndAdd(self, data):
        teacherresource = super(TeacherResourceAddForm, self).createAndAdd(data)
        # Acquisition wrap patient in the current context
        self.teacherresource = teacherresource.__of__(self.context)
        return self.teacherresource

    def nextURL(self):
        if self.request.form.has_key('form.buttons.cancel'):
            site = getSite()
            return '%s/resources' % (site.absolute_url())
        else:
            # overwrite to point to the prescription view
            teacherresource = self.teacherresource
            return teacherresource.aq_parent.absolute_url()
