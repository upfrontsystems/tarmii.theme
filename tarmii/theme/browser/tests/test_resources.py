from plone.uuid.interfaces import IUUID
from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestResourcesView(TarmiiThemeTestBase):
    """ Test Resources browser view
    """

    def test_topictrees(self):
        view = self.topictrees.restrictedTraverse('@@resources')
        self.assertEqual(len(view.topictrees()), 1)
        self.assertEqual([obj.id for obj in view.topictrees()], ['language'])

    def test_add_resource_button_path(self):
        view = self.topictrees.restrictedTraverse('@@resources')
        self.assertEqual(view.add_resource_button_path(), 
            "%s/createObject?type_name=File" %
            self.topictrees.absolute_url())


class TestTopicResourcesView(TarmiiThemeTestBase):
    """ Test TopicResources browser view
    """

    def test_topictitle(self):
        view = self.topictrees.restrictedTraverse('@@topicresources')

        self.request.set('topic_uid',IUUID(self.topic1))
        self.assertEqual(self.topic1.Title(),view.topictitle())

    def test_itemcount(self):
        view = self.topictrees.restrictedTraverse('@@topicresources')

        self.request.set('topic_uid',IUUID(self.topic2))
        self.assertEqual(2,view.itemcount())

    def test_resources(self):
        view = self.topictrees.restrictedTraverse('@@topicresources')

        self.request.set('topic_uid',IUUID(self.topic2))
        self.assertEqual(self.res1,view.resources()[0])
        self.assertEqual(self.res2,view.resources()[1])



