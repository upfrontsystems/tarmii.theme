from plone.uuid.interfaces import IUUID
from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestResourcesView(TarmiiThemeTestBase):
    """ Test Resources browser view
    """

    def test_topictrees(self):
        view = self.topictrees.restrictedTraverse('@@resources')
        self.assertEqual(len(view.topictrees()), 3)        
        self.assertEqual([obj.id for obj in view.topictrees()],
            ['language', 'grade', 'subject'])

    def test_add_resource_button_path(self):
        view = self.topictrees.restrictedTraverse('@@resources')
        self.assertEqual(view.add_resource_button_path(), 
            "%s/++add++tarmii.theme.content.teacherresource" % 
                self.topictrees.absolute_url())
