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
        import upfront.classlist
        import tarmii.theme
        self.loadZCML(package=collective.topictree)
        self.loadZCML(package=upfront.assessmentitem)
        self.loadZCML(package=upfront.classlist)
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
        self.request = self.layer['request']
        self.topictrees = self.portal.topictrees
        self.questions = self.portal.questions
        self.resources = self.portal.resources
        self.videos = self.portal.videos
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.topictrees.invokeFactory('collective.topictree.topictree',
                                      'language', title='Language')
        topictree = self.topictrees._getOb('language')

        topictree.invokeFactory('collective.topictree.topic',
                                'afrikaans', title='Afrikaans')
        self.topic1 = topictree._getOb('afrikaans')
        topictree.invokeFactory('collective.topictree.topic',
                                'english', title='English')
        self.topic2 = topictree._getOb('english')
        topictree.invokeFactory('collective.topictree.topic',
                                'xhosa', title='Xhosa')
        self.topic3 = topictree._getOb('xhosa')

        self.topictree = topictree

        # add 2 resources
        self.resources.invokeFactory('File','resource1', title='Resource1')
        self.res1 = self.resources._getOb('resource1')
        self.resources.invokeFactory('File','resource2', title='Resource2')
        self.res2 = self.resources._getOb('resource2')

        # link resource1 to topics1 and topics2
        topicsfield = self.res1.Schema().get('topics')
        mutator = topicsfield.getMutator(self.res1)
        mutator([self.topic1, self.topic2])

        # link resource2 to topic2
        topicsfield = self.res2.Schema().get('topics')
        mutator = topicsfield.getMutator(self.res2)
        mutator([self.topic2])

        # add 2 video thumbnails
        self.videos.invokeFactory('Image','vid1thumb', title='Video1')
        self.vid1thumb = self.videos._getOb('vid1thumb')
        self.videos.invokeFactory('Image','vid2thumb', title='Video2')
        self.vid2thumb = self.videos._getOb('vid2thumb')
       
        # create a classlists folder for testing
        self.portal.invokeFactory(type_name='Folder', id='classlists',
                                  title='Classlists')
        self.classlists = self.portal._getOb('classlists') 

        self.classlists.invokeFactory('upfront.classlist.content.classlist',
                                      'list1', title='List1')
        self.classlist1 = self.classlists._getOb('list1')
        self.classlists.invokeFactory('upfront.classlist.content.classlist',
                                      'list2', title='List2')
        self.classlist2 = self.classlists._getOb('list2')

