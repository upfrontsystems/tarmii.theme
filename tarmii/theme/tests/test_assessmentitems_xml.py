import lxml
import requests
from zipfile import ZipFile
from cStringIO import StringIO

from zope.component import getUtility

from tarmii.theme.tests.base import TarmiiThemeTestBase


class TestAssessmentItemsXML(TarmiiThemeTestBase):
    """ Test assessment item XML 
    """
    
    def test_fetch_assessmentitems(self):   
        self.fail()
