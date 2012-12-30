from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestActivities(TarmiiThemeTestBase):
    """ Test Activities browser view
    """

    def test_activities(self):
        view = self.activities.restrictedTraverse('@@activities')
        self.assertEqual(len(view.activities()), 3)

