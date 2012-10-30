from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestQuestions(TarmiiThemeTestBase):
    """ Test Questions browser view
    """

    def test_questions(self):
        view = self.questions.restrictedTraverse('@@questions')
        self.assertEqual(len(view.questions()), 0)

    def test_addquestion(self):
        view = self.questions.restrictedTraverse('@@addquestion')
        self.assertEqual(view.update(), None)
        self.request['form.submitted'] = 1
        view.update()
        self.assertTrue(self.questions.hasObject('Q001'))
