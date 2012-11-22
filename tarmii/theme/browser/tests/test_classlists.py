from tarmii.theme.tests.base import TarmiiThemeTestBase

from tarmii.theme.browser.classlists import ClassListAddForm

class TestClassLists(TarmiiThemeTestBase):
    """ Test ClassLists browser view
    """

    def test_classlists(self):
        view = self.classlists.restrictedTraverse('@@classlists')
        self.assertEqual(len(view.classlists()), 2)

    def test_add_classlist_url(self):
        view = self.classlists.restrictedTraverse('@@classlists')
        self.assertEqual(view.add_classlist_url(), 
            "%s/++add++upfront.classlist.content.classlist" % 
            self.classlists.absolute_url())

