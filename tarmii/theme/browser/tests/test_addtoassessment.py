from plone.uuid.interfaces import IUUID

from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestAddToAssessment(TarmiiThemeTestBase):
    """ Test AddToAssessment browser view
    """

    def test_update_1(self):
        view = self.activities.restrictedTraverse('@@add-to-assessment')

        # hit cancel
        self.request.set('activity_id', self.activity4.id)
        self.request.form['buttons.add.to.assessment.cancel'] = 'aplaceholder'
        url = view.update()
        self.assertEqual(url,self.activities.absolute_url())

    def test_update_2(self):
        view = self.activities.restrictedTraverse('@@add-to-assessment')
        
        # hit submit and there is nothing on list, nothing typed
        self.request.set('activity_id', self.activity4.id)
        self.request.form['buttons.add.to.assessment.submit'] = 'aplaceholder'
        self.request.form['buttons.add.to.assessment.text.input'] = ''
        url = view.update()
        self.assertEqual(url,self.activities.absolute_url())

        # hit submit and valid choice is selected, nothing typed
        self.request.set('assessment_uid_selected', IUUID(self.assessment1))
        self.assertEqual(len(self.assessment1.assessment_items),3)
        url = view.update()
        self.assertEqual(len(self.assessment1.assessment_items),4)

    def test_update_3(self):
        view = self.activities.restrictedTraverse('@@add-to-assessment')
        
        # hit submit and there is something on list and something typed or
        # hit submit and there is nothing on list and something typed
        self.request.set('activity_id', self.activity4.id)
        self.request.form['buttons.add.to.assessment.submit'] = 'aplaceholder'
        self.request.form['buttons.add.to.assessment.text.input'] = 'something'
        self.request.set('assessment_uid_selected', IUUID(self.assessment1))
        self.assertEqual(len(self.assessments.getFolderContents()),2)
        url = view.update()
        self.assertEqual(len(self.assessments.getFolderContents()),3)
        added_assessment = self.assessments.getFolderContents()[2].getObject()
        self.assertEqual(added_assessment.id,'something')
        self.assertEqual(added_assessment.assessment_items[0].to_object,
                         self.activity4)

        # hit submit and there is something on list and something typed or
        # hit submit and there is nothing on list and something typed
        # and the assessment already exists and doesnt contain the activity
        self.request.set('activity_id', self.activity3.id)
        self.assertEqual(len(added_assessment.assessment_items),1)
        url = view.update()
        self.assertEqual(len(added_assessment.assessment_items),2)

        # hit submit and there is something on list and something typed or
        # hit submit and there is nothing on list and something typed
        # and the assessment already exists and already contains the activity
        self.assertEqual(len(added_assessment.assessment_items),2)
        url = view.update()
        self.assertEqual(len(added_assessment.assessment_items),2)

    def test_activity_id(self):
        view = self.activities.restrictedTraverse('@@add-to-assessment')
        self.request['activity_id'] = 'test'
        self.assertEqual(view.activity_id(),'test')        

    def test_available_assessments(self):
        view = self.activities.restrictedTraverse('@@add-to-assessment')

        # activity 4 is not yet in either of the two assessments
        self.request.set('activity_id', self.activity4.id)
        view.available_assessments()
        self.assertEqual(len(view.available_assessments()),2)

        # activity 3 is already in test1
        self.request.set('activity_id', self.activity3.id)
        view.available_assessments()
        self.assertEqual(len(view.available_assessments()),1)
