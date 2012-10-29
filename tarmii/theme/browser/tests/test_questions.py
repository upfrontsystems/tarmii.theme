from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestQuestions(TarmiiThemeTestBase):
    """ Test Questions browser view
    """

    def test_questions(self):
        view = self.questions.restrictedTraverse('@@questions')
        self.assertEqual(len(view.questions()), 0)

    def test_add_question_url(self):
        view = self.questions.restrictedTraverse('@@questions')
        self.assertEqual(view.add_question_url(), 
            '%s/++add++upfront.assessmentitem.content.assessmentitemcontainer' %
            self.questions.absolute_url())
