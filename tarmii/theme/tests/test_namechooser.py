from zope.component import getUtility
from zope.container.interfaces import INameChooser

from plone.dexterity.utils import createContent
from plone.dexterity.utils import createContentInContainer
from plone.i18n.normalizer.interfaces import IURLNormalizer

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
        normalizer = getUtility(IURLNormalizer)
        obj = createContent(
            'upfront.assessmentitem.content.assessmentitem')
        test_name = normalizer.normalize('Q001')
        self.assertEqual(namechooser.checkName(test_name, obj), True)
        obj = createContentInContainer(self.activities,
            'upfront.assessmentitem.content.assessmentitem')
        self.assertEqual(namechooser.checkName(test_name, obj), False)

    def test_chooseName(self):
        namechooser = INameChooser(self.activities)
        obj = createContentInContainer(self.activities,
            'upfront.assessmentitem.content.assessmentitem')        
        self.assertEqual(namechooser.chooseName(None, obj), 'q001')
        obj = createContent(
            'upfront.assessmentitem.content.assessmentitem')
        self.assertEqual(namechooser.chooseName(None, obj), 'q002')
        self.assertEqual(namechooser.chooseName('custom', obj), 'custom')
