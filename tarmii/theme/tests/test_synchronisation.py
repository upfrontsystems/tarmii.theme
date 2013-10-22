import lxml
import requests

from zope.component import getUtility

from tarmii.theme.tests.base import TarmiiThemeTestBase


class TestSynchronisation(TarmiiThemeTestBase):
    """ Test assessment item synchronisation 
    """
    
    def test_fetch_ids(self):
        view = self.portal.restrictedTraverse('@@assessmentitem-ids-xml')
        result = view()
        tree = lxml.etree.fromstring(result)
        self.assertEqual(len(tree.findall('assessmentitem')), 4)

    def test_fetch_assessments(self):
        self.fail()
    
    def test_marshal_item(self):  
        view = self.portal.restrictedTraverse('@@assessmentitem-xml')
        item = self.activities.objectValues()[0]
        element = view.marshal_item(item)
        xml = lxml.etree.tostring(element)
        self.assertEqual(xml,
                         '<assessmentitem id="assessmentitem1">Activity1</assessmentitem>',
                         'XML marshalled incorrectly.')
