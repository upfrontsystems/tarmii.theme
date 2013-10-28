import lxml
import requests
from zipfile import ZipFile
from cStringIO import StringIO

from zope.component import getUtility

from tarmii.theme.tests.base import TarmiiThemeTestBase


class TestSynchronisation(TarmiiThemeTestBase):
    """ Test assessment item synchronisation 
    """
    
    def test_fetch_ids(self):
        self.fail()

    def test_missing_ids(self):
        self.fail()

    def test_fetch_assessments_zip(self):
        self.fail()
    
    def test_import_assessmentitems(self):
        self.fail()

    def test_get_settings(self):
        self.fail()

    def test_validate_settings(self):
        self.fail()
    
    def test_add_errors(self):
        self.fail()

    def test_add_messages(self):
        self.fail()

    def test_fetch_assessmentitems(self):   
        view = self.portal.restrictedTraverse('@@assessmentitem-ids-xml')
        xml = view()

        view = self.portal.restrictedTraverse('@@assessmentitem-xml')
        view.request.form['xml'] = xml
        result = view()
        zipio = StringIO(result)
        zipfile = ZipFile(zipio, 'r')
        assert ('assessmentitems.xml' in zipfile.namelist(),
                'Could no find assessments.xml')
    
    def test_marshal_item(self):  
        view = self.portal.restrictedTraverse('@@assessmentitem-xml')
        item = self.activities.objectValues()[0]
        element = view.marshal_item(item)
        xml = lxml.etree.tostring(element)
        self.assertEqual(xml,
                         '<assessmentitem id="assessmentitem1">Activity1</assessmentitem>',
                         'XML marshalled incorrectly.')
