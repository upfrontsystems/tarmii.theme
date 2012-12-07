from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestAssessments(TarmiiThemeTestBase):
    """ Test Assessments browser view
    """

    def test_assessments(self):
        view = self.assessments.restrictedTraverse('@@assessments')
        self.assertEqual(len(view.assessments()), 2)

    def test_add_assessment_url(self):
        view = self.assessments.restrictedTraverse('@@assessments')
        self.assertEqual(view.add_assessment_url(), 
            "%s/++add++upfront.assessment.content.assessment" % 
            self.assessments.absolute_url())

