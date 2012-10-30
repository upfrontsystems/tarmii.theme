from zope.component import getUtility

from tarmii.theme.tests.base import TarmiiThemeTestBase
from tarmii.theme.interfaces import IItemVersion


class TestItemVersion(TarmiiThemeTestBase):
    """ Test ItemVersion utility
    """

    def test_next_version(self):
        utility = getUtility(IItemVersion)
        self.assertEqual(utility.next_version(), 1)
        self.assertEqual(utility.next_version(), 2)
        self.assertEqual(utility.next_version(), 3)
