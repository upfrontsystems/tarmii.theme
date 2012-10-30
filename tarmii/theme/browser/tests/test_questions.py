from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestQuestions(TarmiiThemeTestBase):
    """ Test Questions browser view
    """

    def test_questions(self):
        view = self.questions.restrictedTraverse('@@questions')
        self.assertEqual(len(view.questions()), 0)

