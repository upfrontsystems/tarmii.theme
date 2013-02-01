from zope.component import getUtility
from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestTeacherProfilesView(TarmiiThemeTestBase):
    """ Test TeacherProfiles view """

    # XXX update, provinces, schools and teachers methods still need to be 
    # tested but for that, update method must be working 100%

    def test_show_provinces(self):
        view = self.portal.restrictedTraverse('@@teacher-profiles')
        view.show_provinces()
        self.assertEqual(view.show_provinces(),True)
        self.request.set('province','Province')
        self.assertEqual(view.show_provinces(),False)
        self.request.set('school','School')
        self.assertEqual(view.show_provinces(),False)

    def test_show_schools(self):
        view = self.portal.restrictedTraverse('@@teacher-profiles')
        view.show_schools()
        self.assertEqual(view.show_schools(),False)
        self.request.set('province','Province')
        self.assertEqual(view.show_schools(),True)
        self.request.set('school','School')
        self.assertEqual(view.show_schools(),False)

    def test_show_teachers(self):
        view = self.portal.restrictedTraverse('@@teacher-profiles')
        view.show_teachers()
        self.assertEqual(view.show_teachers(),False)
        self.request.set('province','Province')
        self.assertEqual(view.show_teachers(),False)
        self.request.set('school','School')
        self.assertEqual(view.show_teachers(),True)

    def test_context_path(self):
        view = self.portal.restrictedTraverse('@@teacher-profiles')
        self.assertEqual(view.context_path(),self.portal.absolute_url())

    def test_province_request(self):
        view = self.portal.restrictedTraverse('@@teacher-profiles')
        self.request.set('province','Province')
        self.assertEqual(view.province_request(),'Province')

    def test_school_request(self):
        view = self.portal.restrictedTraverse('@@teacher-profiles')
        self.request.set('school','School')
        self.assertEqual(view.school_request(),'School')

