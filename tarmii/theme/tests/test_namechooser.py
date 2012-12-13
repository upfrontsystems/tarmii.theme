from zope.container.interfaces import INameChooser

from plone.dexterity.utils import createContent
from plone.dexterity.utils import createContentInContainer

from tarmii.theme.tests.base import TarmiiThemeTestBase
from tarmii.theme.namechooser import AssessmentItemNameChooser

class TestNameChooser(TarmiiThemeTestBase):
    """ Test AssessmentItemNameChooser
    """

    def test_lookup(self):
        namechooser = INameChooser(self.activities)
        self.assertEqual(namechooser.__class__, AssessmentItemNameChooser)

    def test_checkName(self):
        namechooser = INameChooser(self.activities)
        obj = createContent(
            'upfront.assessmentitem.content.assessmentitem')
        self.assertEqual(namechooser.checkName('Q001', obj), True)
        obj = createContentInContainer(self.activities,
            'upfront.assessmentitem.content.assessmentitem')
        self.assertEqual(namechooser.checkName('Q001', obj), False)

    def test_chooseName(self):
        namechooser = INameChooser(self.activities)
        obj = createContentInContainer(self.activities,
            'upfront.assessmentitem.content.assessmentitem')
        self.assertEqual(namechooser.chooseName(None, obj), 'Q001')
        obj = createContent(
            'upfront.assessmentitem.content.assessmentitem')
        self.assertEqual(namechooser.chooseName(None, obj), 'Q002')
        self.assertEqual(namechooser.chooseName('custom', obj), 'custom')
