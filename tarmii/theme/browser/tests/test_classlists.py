from tarmii.theme.tests.base import TarmiiThemeTestBase

from tarmii.theme.browser.classlists import ClassListAddForm

class TestClassLists(TarmiiThemeTestBase):
    """ Test ClassLists browser view
    """

    def test_classlists(self):
        view = self.classlists.restrictedTraverse('@@classlists')
        self.assertEqual(len(view.classlists()), 2)

    def test_import_learners_url(self):
        view = self.classlists.restrictedTraverse('@@classlists')
        self.assertEqual(view.import_learners_url(), 
            "%s/@@import-learners" % self.classlists.absolute_url())

    def test_add_classlist_url(self):
        view = self.classlists.restrictedTraverse('@@classlists')
        self.assertEqual(view.add_classlist_url(), 
            "%s/++add++upfront.classlist.content.classlist" % 
            self.classlists.absolute_url())


class TestClassListAddForm(TarmiiThemeTestBase):
    """ Test ClassLists add form
    """

    def test_createAndAdd(self):
        data = {'IBasic.title': u'List1', 'IBasic.description': u''}
        contentFilter = {
            'portal_type': 'upfront.classlist.content.classlist',
            'sort_on': 'sortable_title'}
        classlists_before = self.classlists.getFolderContents(contentFilter)
        form = ClassListAddForm(self.classlists, self.request)
        form.portal_type = 'upfront.classlist.content.classlist'
        createAndAdd = form.createAndAdd(data)
        contentFilter = {
            'portal_type': 'upfront.classlist.content.classlist',
            'sort_on': 'sortable_title'}
        classlists_after = self.classlists.getFolderContents(contentFilter)
        self.assertEquals(len(classlists_after),len(classlists_before)+1)

    def test_nextURL(self):
        # save
        form = ClassListAddForm(self.classlists, self.request)
        form.classlist = self.classlist1
        nextURL = form.nextURL()
        path = self.classlist1.absolute_url()
        self.assertEquals(path,nextURL)

        # cancel
        self.request.form['form.buttons.cancel'] = 'aplaceholder'
        nextURL = form.nextURL()
        path = self.classlists.absolute_url()
        self.assertEquals(path,nextURL)












