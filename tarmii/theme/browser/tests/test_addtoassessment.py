from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestAddToAssessment(TarmiiThemeTestBase):
    """ Test AddToAssessment browser view
    """

    def test_activity_id(self):
        view = self.activities.restrictedTraverse('@@add-to-assessment')
        self.request['activity_id'] = 'test'
        self.assertEqual(view.activity_id(),'test')        

    def test_assessments(self):
        view = self.activities.restrictedTraverse('@@add-to-assessment')
        self.assertEqual(view.assessments()[0].getObject().id,'test1')
        self.assertEqual(view.assessments()[1].getObject().id,'test2')

