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

    def test_evaluationsheet_title(self):
        view = self.evaluationsheets.restrictedTraverse('@@evaluationsheets')
        evalsheet_brain = self.evaluationsheets.getFolderContents()[0]
        view.evaluationsheet_title(evalsheet_brain)
        self.assertEqual(view.evaluationsheet_title(evalsheet_brain),
                         'Test1 List1')

