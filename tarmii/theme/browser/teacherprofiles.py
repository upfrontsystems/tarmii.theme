from cStringIO import StringIO
from five import grok
from zope.interface import Interface
from zope.component import getUtility
from plone.directives import dexterity
from Products.CMFCore.utils import getToolByName

from tarmii.theme.interfaces import ISiteData

grok.templatedir('templates')

class TeacherProfilesView(grok.View):
    """ View for teacher profiles
    """
    grok.context(Interface)
    grok.name('teacher-profiles')
    grok.template('teacherprofiles')
    grok.require('zope2.View')

    def update(self, **kwargs):

        sitedata = getUtility(ISiteData)

        # display the dictionary nicely
        self.teacher_data = sitedata.extract_teacher_data()


        # XXX debug - currently calling directly
#        view = self.context.restrictedTraverse('@@upload-to-server')
#        test_data = StringIO()
#        test_data.write(view.zip_csv())
#        self.teacher_data = sitedata.extract_test(test_data)

        return

      


