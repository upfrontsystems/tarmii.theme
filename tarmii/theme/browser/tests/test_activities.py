from plone.uuid.interfaces import IUUID
from Products.CMFPlone.PloneBatch import Batch
from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestActivities(TarmiiThemeTestBase):
    """ Test Activities browser view
    """

    def test_update(self):
        view = self.activities.restrictedTraverse('@@activities')
        self.request.set('select-one', 'one')
        self.request.set('select-two', 'two')
        self.assertEqual(view.update(),['one','two'])

    def test_user_is_admin(self):
        view = self.activities.restrictedTraverse('@@activities')
        self.assertEqual(view.user_is_admin(),1)

    def test_topictrees(self):
        view = self.activities.restrictedTraverse('@@activities')
        self.assertEqual(len(view.topictrees()), 4)        
        self.assertEqual([obj.id for obj in view.topictrees()],
            ['language', 'grade', 'term','subject'])

    def test_relations_lookup(self):
        view = self.activities.restrictedTraverse('@@activities')
        self.assertEqual(view.relations_lookup(IUUID(self.topic1)),
                         [IUUID(self.activity1)])        
        self.assertEqual(view.relations_lookup(IUUID(self.topic2)),
                         [IUUID(self.activity1),IUUID(self.activity2)])
        self.assertEqual(view.relations_lookup(IUUID(self.topic3)),
                         [IUUID(self.activity1),IUUID(self.activity2)])

    def test_activities(self):
        view = self.activities.restrictedTraverse('@@activities')
        view.update() # call update first to set self.topics
        self.assertEqual(len(view.activities()), 4)

        # len(self.topics) = 0
        self.topics = view.update() # call update first to set self.topics
        contentFilter = {
                'portal_type': 'upfront.assessmentitem.content.assessmentitem'}
        ref = self.activities.getFolderContents(contentFilter)
        ref_obj = [ x.getObject() for x in ref]
        self.assertEqual([x.getObject() for x in view.activities()],ref_obj)

        # len(self.topics) = 1
        self.request.set('select-lange', IUUID(self.topic1))
        self.topics = view.update() # call update first to set self.topics        
        self.assertEqual([ x.getObject() for x in view.activities()],
                         [self.activity1])

    def test_activities_2(self):
        view = self.activities.restrictedTraverse('@@activities')
        # len(self.topics) > 1
        self.request.set('select-grade', IUUID(self.topic2))
        self.request.set('select-subject', IUUID(self.topic3))
        self.topics = view.update() # call update first to set self.topics
        self.assertEqual([ x.getObject() for x in view.activities()],
                         [self.activity1, self.activity2])

    def test_activities_batch(self):
        view = self.activities.restrictedTraverse('@@activities')
        self.request.set('select-grade', IUUID(self.topic2))
        self.topics = view.update() # call update first to set self.topics
        b_start = self.request.get('b_start', 0)
        ref = Batch(view.activities(), 10, int(b_start), orphan=0)
        self.assertEqual(view.activities_batch().length,ref.length)

    def test_activities_count(self):
        view = self.activities.restrictedTraverse('@@activities')
        self.request.set('select-grade', IUUID(self.topic2))
        self.topics = view.update() # call update first to set self.topics
        self.assertEqual(view.activities_count(),2)
