import lxml

from zope.component import getUtility

from tarmii.theme.tests.base import TarmiiThemeTestBase


class TestSynchronisation(TarmiiThemeTestBase):
    """ Test assessment item synchronisation 
    """

    def test_get_ids(self):
        view = self.portal.restrictedTraverse('@@synchronise')
        result = view()
        assert result is not None

        import pdb;pdb.set_trace()
        tree = lxml.etree.fromstring(result)
