from zope.component.hooks import getSite
from plone.uuid.interfaces import IUUID
from tarmii.theme.browser.forms import TeacherResourceAddForm

from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestTeacherResourceAddForm(TarmiiThemeTestBase):

    def test_nextURL(self):
        form = TeacherResourceAddForm(self.resources, self.request)
        nextURL = form.nextURL()
        site = getSite()
        path = '%s/resources' % (site.absolute_url())
        self.assertEquals(path,nextURL)
