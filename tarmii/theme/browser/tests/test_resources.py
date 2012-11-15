import json
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


class TestTreeDataViewMixin:
    """ Mixin class for common test view data
    """

    def testdata(self):
        """ create json representation from topictrees and topics in the
            system.
        """
        t_uid = IUUID(self.topictree)
        t1_uid = IUUID(self.topic1)
        t2_uid = IUUID(self.topic2)
        t3_uid = IUUID(self.topic3)
        base_url = self.portal.absolute_url()
        url1 = base_url + '/@@topicresources?topic_uid=' + t1_uid
        url2 = base_url + '/@@topicresources?topic_uid=' + t2_uid
        url3 = base_url + '/@@topicresources?topic_uid=' + t3_uid

        data1 = { 
                'data': 'Afrikaans (1)',
                'attr': {'url' : url1, 'id': t1_uid, 'node_uid': t1_uid },
                'rel': 'default',
                'children': [],
        }
        data2 = { 
                'data': 'English (2)',
                'attr': {'url' : url2, 'id': t2_uid, 'node_uid': t2_uid },
                'rel': 'default',
                'children': [],
        }
        data3 = { 
                'data': 'Xhosa (0)',
                'attr': {'url' : url3, 'id': t3_uid, 'node_uid': t3_uid },
                'rel': 'default',
                'children': [],
        }
        test_data = {
                    'state' : 'open',
                    'data': 'Language',
                    'attr': {'url' : '#', 'id': t_uid, 'node_uid': t_uid },
                    'rel': 'root',
                    'children': [ data1, data2, data3 ],
        }

        return test_data

class TestTreeDataView(TarmiiThemeTestBase,TestTreeDataViewMixin):
    """ Test TopicData browser view
    """

    def test__call__(self):
        view = self.topictrees.restrictedTraverse('@@treedata')
        self.request.set('context_node_uid',IUUID(self.topictree))
        self.assertEqual(view(),json.dumps(self.testdata()))

    def test_itemcount(self):
        view = self.topictrees.restrictedTraverse('@@treedata')
        itemcount = view.itemcount(IUUID(self.topic2))
        self.assertEqual(2,itemcount)

    def test_topicjson(self):
        view = self.topictrees.restrictedTraverse('@@treedata')
        topicjson = view.topicjson(IUUID(self.topictree))
        self.assertEqual(topicjson,self.testdata())
