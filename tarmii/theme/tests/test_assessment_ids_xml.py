import lxml
import requests
from zipfile import ZipFile
from cStringIO import StringIO

from zope.component import getUtility

from tarmii.theme.tests.base import TarmiiThemeTestBase


class TestAssessmentItemIdsXML(TarmiiThemeTestBase):
    """ Test assessment item ids XML 
    """
    
    def test_assessmentitem_ids_xml(self):
        view = self.portal.restrictedTraverse('@@assessmentitem-ids-xml')
        result = view()
        tree = lxml.etree.fromstring(result)
        num_activities = len(self.portal.activities.objectIds())
        items = tree.findall('assessmentitem')
        self.assertEqual(len(items), num_activities)
        for number in range(1, num_activities + 1):
            item = tree.find('assessmentitem[@id="assessmentitem%s"]' % number)
            assert item is not None
