from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestActivities(TarmiiThemeTestBase):
    """ Test Activities browser view
    """

    def test_activities(self):
        view = self.activities.restrictedTraverse('@@activities')
        view.update() # call update first to set self.topics
        self.assertEqual(len(view.activities()), 4)

