from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestEvaluationSheets(TarmiiThemeTestBase):
    """ Test Evaluation Sheets browser view
    """

    def test_evaluationsheets(self):
        view = self.evaluationsheets.restrictedTraverse('@@evaluationsheets')
        self.assertEqual(len(view.evaluationsheets()), 2)

    def test_add_evaluationsheets_url(self):
        view = self.evaluationsheets.restrictedTraverse('@@evaluationsheets')
        self.assertEqual(view.add_evaluationsheet_url(), 
            "%s/++add++upfront.assessment.content.evaluationsheet" % 
            self.evaluationsheets.absolute_url())

