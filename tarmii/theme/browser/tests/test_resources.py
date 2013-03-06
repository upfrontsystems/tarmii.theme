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

    def test_update(self):
        view = self.topictrees.restrictedTraverse('@@resources')
        self.request.set('select-one', 'one')
        self.request.set('select-two', 'two')
        self.assertEqual(view.update(),['one','two'])

    def test_addresource_addportalcontent(self):
        view = self.topictrees.restrictedTraverse('@@resources')
        self.assertEqual(view.addresource_addportalcontent(),1)

    def test_user_is_admin(self):
        view = self.topictrees.restrictedTraverse('@@resources')
        self.assertEqual(view.user_is_admin(),1)

    def test_add_resource_button_path(self):
        view = self.topictrees.restrictedTraverse('@@resources')
        self.assertEqual(view.add_resource_button_path(), 
            "%s/++add++tarmii.theme.content.teacherresource" % 
                self.topictrees.absolute_url())

