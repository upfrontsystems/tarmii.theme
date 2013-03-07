from plone.uuid.interfaces import IUUID
from Products.CMFPlone.PloneBatch import Batch
from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestResourcesView(TarmiiThemeTestBase):
    """ Test Resources browser view
    """

    def test_topictrees(self):
        view = self.resources.restrictedTraverse('@@resources')
        self.assertEqual(len(view.topictrees()), 3)        
        self.assertEqual([obj.id for obj in view.topictrees()],
            ['language', 'grade', 'subject'])

    def test_update(self):
        view = self.resources.restrictedTraverse('@@resources')
        self.request.set('select-one', 'one')
        self.request.set('select-two', 'two')
        self.assertEqual(view.update(),['one','two'])

    def test_addresource_addportalcontent(self):
        view = self.resources.restrictedTraverse('@@resources')
        self.assertEqual(view.addresource_addportalcontent(),1)

    def test_user_is_admin(self):
        view = self.resources.restrictedTraverse('@@resources')
        self.assertEqual(view.user_is_admin(),1)

    def test_add_resource_button_path(self):
        view = self.resources.restrictedTraverse('@@resources')
        self.assertEqual(view.add_resource_button_path(), 
            "%s/++add++tarmii.theme.content.teacherresource" % 
                self.resources.absolute_url())

    def test_relations_lookup(self):
        view = self.resources.restrictedTraverse('@@resources')
        self.assertEqual(view.relations_lookup(IUUID(self.topic1)),
                         [IUUID(self.res1)])
        self.assertEqual(view.relations_lookup(IUUID(self.topic2)),
                         [IUUID(self.res1),IUUID(self.res2)])

    def test_resources(self):
        view = self.resources.restrictedTraverse('@@resources')

        # len(self.topics) = 0
        self.topics = view.update() # call update first to set self.topics
        ref = [x.getObject() for x in self.resources.getFolderContents()]
        self.assertEqual(view.resources(),ref)        

        # len(self.topics) = 1
        self.request.set('select-grade', IUUID(self.topic2))
        self.topics = view.update() # call update first to set self.topics
        self.assertEqual(view.resources(),[self.res1, self.res2])

        # len(self.topics) > 1
        self.request.set('select-lang', IUUID(self.topic1))
        self.request.set('select-grade', IUUID(self.topic2))
        self.topics = view.update() # call update first to set self.topics
        self.assertEqual(view.resources(),[self.res1])

    def test_resources_batch(self):
        view = self.resources.restrictedTraverse('@@resources')
        self.request.set('select-grade', IUUID(self.topic2))
        self.topics = view.update() # call update first to set self.topics
        b_start = self.request.get('b_start', 0)
        ref = Batch(view.resources(), 10, int(b_start), orphan=0)
        self.assertEqual(view.resources_batch().length,ref.length)

    def test_resource_count(self):
        view = self.resources.restrictedTraverse('@@resources')
        self.request.set('select-grade', IUUID(self.topic2))
        self.topics = view.update() # call update first to set self.topics
        self.assertEqual(view.resource_count(),2)
