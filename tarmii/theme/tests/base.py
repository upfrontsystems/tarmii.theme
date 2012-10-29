from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
import unittest2 as unittest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plone.testing import z2

PROJECTNAME = "tarmii.theme"

class TestCase(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.topictree
        import upfront.assessmentitem
        import tarmii.theme
        self.loadZCML(package=collective.topictree)
        self.loadZCML(package=upfront.assessmentitem)
        self.loadZCML(package=tarmii.theme)
        z2.installProduct(app, PROJECTNAME)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, '%s:default' % PROJECTNAME)

    def tearDownZope(self, app):
        z2.uninstallProduct(app, PROJECTNAME)

FIXTURE = TestCase()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="fixture:Integration")


class TarmiiThemeTestBase(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.topictrees = self.portal.topictrees
        self.questions = self.portal.questions
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.topictrees.invokeFactory('collective.topictree.topictree',
                                      'language', title='Language')
        topictree = self.topictrees._getOb('language')

        topictree.invokeFactory('collective.topictree.topic',
                                'afrikaans', title='Afrikaans')
        topictree.invokeFactory('collective.topictree.topic',
                                'english', title='English')
        topictree.invokeFactory('collective.topictree.topic',
                                'xhosa', title='Xhosa')
