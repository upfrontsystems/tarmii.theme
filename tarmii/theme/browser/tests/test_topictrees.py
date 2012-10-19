from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestTopicTrees(TarmiiThemeTestBase):
    """ Test TopicTrees browser view
    """

    def test_topictrees(self):
        view = self.topictrees.restrictedTraverse('@@topictrees')

        self.assertEqual(len(view.topictrees()), 1)
        self.assertEqual([obj.id for obj in view.topictrees()], ['language'])
        self.assertEqual(view.add_topictree_url(), 
            "%s/++add++collective.topictree.topictree" %
            self.topictrees.absolute_url())
