from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
import unittest2 as unittest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plone.testing import z2

from z3c.relationfield import RelationValue
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from plone.registry.interfaces import IRegistry
from plone.app.controlpanel.security import ISecuritySchema
from zope.component.hooks import getSite

from tarmii.theme.interfaces import ITARMIIRemoteServerSettings

PROJECTNAME = "tarmii.theme"

class TestCase(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.topictree
        import upfront.assessmentitem
        import upfront.assessment
        import upfront.classlist
        import upfront.pagetracker
        import tarmii.theme
        self.loadZCML(package=collective.topictree)
        self.loadZCML(package=upfront.assessmentitem)
        self.loadZCML(package=upfront.assessment)
        self.loadZCML(package=upfront.classlist)
        self.loadZCML(package=upfront.pagetracker)
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
        self.activities = self.portal.activities
        self.resources = self.portal.resources
        self.videos = self.portal.videos
        self.videos_howto = self.portal.videos.howto
        self.videos_pedagogic = self.portal.videos.pedagogic
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.intids = getUtility(IIntIds)

        # create members folder
        self.portal.invokeFactory(type_name='Folder', id='Members',
                                     title='Members')

        # language directory and topics are created by setuphandlers
        if not self.topictrees.hasObject('language'):
            self.topictrees.invokeFactory('collective.topictree.topictree',
                                          'language', title='Language')
        topictree = self.topictrees._getOb('language')
        topictree.use_with_activities = True
        topictree.use_with_resources = True

        if not topictree.hasObject('afrikaans'):
            topictree.invokeFactory('collective.topictree.topic',
                                    'afrikaans', title='Afrikaans')
        if not topictree.hasObject('english'):
            topictree.invokeFactory('collective.topictree.topic',
                                    'english', title='English')
        if not topictree.hasObject('xhosa'):
            topictree.invokeFactory('collective.topictree.topic',
                                    'xhosa', title='Xhosa')

        # add topictree 2 for grades with topic grade1
        if not self.topictrees.hasObject('grade'):
            self.topictrees.invokeFactory('collective.topictree.topictree',
                                          'grade', title='Grade')
        topictree2 = self.topictrees._getOb('grade')
        topictree2.use_with_activities = True
        topictree2.use_with_resources = True

        if not topictree2.hasObject('grade1'):
            topictree2.invokeFactory('collective.topictree.topic',
                                    'grade1', title='Grade1')

        # add topictree 3 for subjects with topic mathematics
        if not self.topictrees.hasObject('subject'):
            self.topictrees.invokeFactory('collective.topictree.topictree',
                                          'subject', title='Subject')
        topictree3 = self.topictrees._getOb('subject')
        topictree3.use_with_activities = True
        topictree3.use_with_resources = True

        if not topictree3.hasObject('mathematics'):
            topictree2.invokeFactory('collective.topictree.topic',
                                    'mathematics', title='Mathematics')

        self.topictree = topictree
        self.topic1 = topictree._getOb('afrikaans')
        self.topic2 = topictree2._getOb('grade1')
        self.topic3 = topictree3._getOb('mathematics')       

        # add 2 resources
        self.resources.invokeFactory('tarmii.theme.content.teacherresource',
                                      'resource1', title='Resource1')
        self.res1 = self.resources._getOb('resource1')
        self.resources.invokeFactory('tarmii.theme.content.teacherresource',
                                      'resource2', title='Resource2')
        self.res2 = self.resources._getOb('resource2')
       
        # link resource1 to topic1 and topic2
        topic_list = [RelationValue(self.intids.getId(self.topic1)),
                      RelationValue(self.intids.getId(self.topic2))]
        self.res1.topics = topic_list
        notify(ObjectModifiedEvent(self.res1))

        # link resource2 to topic2
        topic_list = [RelationValue(self.intids.getId(self.topic2))]
        self.res2.topics = topic_list
        notify(ObjectModifiedEvent(self.res2))

        # add 2 video thumbnails
        self.videos_howto.invokeFactory('Image','vid1thumb', title='Video1')
        self.vid1thumb = self.videos_howto._getOb('vid1thumb')
        self.videos_howto.invokeFactory('Image','vid2thumb', title='Video2')
        self.vid2thumb = self.videos_howto._getOb('vid2thumb')


        # allow member folders to be created
        security_adapter =  ISecuritySchema(self.portal)
        security_adapter.set_enable_user_folders(True)
        # enable self-registration of users
        security_adapter.set_enable_self_reg(True)

        pm = getSite().portal_membership
        # create members folder
        pm.createMemberArea()
        members_folder = pm.getHomeFolder()

        # create classlists folder in members folder
        members_folder.invokeFactory(type_name='Folder', id='classlists_',
                                     title='Class Lists')
        self.classlists = members_folder._getOb('classlists_')
        # create assessments folder in members folder
        members_folder.invokeFactory(type_name='Folder', id='assessments_',
                                     title='Assessments')
        self.assessments = members_folder._getOb('assessments_')
   
        # create evaluation folder in members folder
        members_folder.invokeFactory(type_name='Folder', id='evaluation_',
                                     title='Evaluation')
        self.evaluationsheets = members_folder._getOb('evaluation_')

       
        self.classlists.invokeFactory('upfront.classlist.content.classlist',
                                      'list1', title='List1')
        self.classlist1 = self.classlists._getOb('list1')
        self.classlists.invokeFactory('upfront.classlist.content.classlist',
                                      'list2', title='List2')
        self.classlist2 = self.classlists._getOb('list2')

        self.assessments.invokeFactory('upfront.assessment.content.assessment',
                                      'test1', title='Test1')
        self.assessment1 = self.assessments._getOb('test1')
        self.assessments.invokeFactory('upfront.assessment.content.assessment',
                                      'test2', title='Test2')
        self.assessment2 = self.assessments._getOb('test2')

        eval_factory = 'upfront.assessment.content.evaluationsheet'
        self.evaluationsheets.invokeFactory(eval_factory,
                                      'evalsheet1', title='EvalSheet1')
        self.evaluationsheet1 = self.evaluationsheets._getOb('evalsheet1')
        self.evaluationsheets.invokeFactory(eval_factory,
                                      'evalsheet2', title='EvalSheet2')
        self.evaluationsheet2 = self.evaluationsheets._getOb('evalsheet2')

        classlist1_intid = self.intids.getId(self.classlist1)
        classlist2_intid = self.intids.getId(self.classlist2)
        self.evaluationsheet1.classlist = RelationValue(classlist1_intid)
        self.evaluationsheet2.classlist = RelationValue(classlist2_intid)

        assessment1_intid = self.intids.getId(self.assessment1)
        assessment2_intid = self.intids.getId(self.assessment2)
        self.evaluationsheet1.assessment = RelationValue(assessment1_intid)
        self.evaluationsheet2.assessment = RelationValue(assessment2_intid)

        notify(ObjectModifiedEvent(self.evaluationsheet1))
        notify(ObjectModifiedEvent(self.evaluationsheet2))
        

        # create activities
        self.activities.invokeFactory('upfront.assessmentitem.content.assessmentitem',
                                      'assessmentitem1', title='Activity1')
        self.activity1 = self.activities._getOb('assessmentitem1')
        self.activities.invokeFactory('upfront.assessmentitem.content.assessmentitem',
                                      'assessmentitem2', title='Activity2')
        self.activity2 = self.activities._getOb('assessmentitem2')
        self.activities.invokeFactory('upfront.assessmentitem.content.assessmentitem',
                                      'assessmentitem3', title='Activity3')
        self.activity3 = self.activities._getOb('assessmentitem3')

        # link activity1 to topic1, topic2, topic3
        topic_list = [RelationValue(self.intids.getId(self.topic1)),
                      RelationValue(self.intids.getId(self.topic2)),
                      RelationValue(self.intids.getId(self.topic3))]
        self.activity1.topics = topic_list
        notify(ObjectModifiedEvent(self.activity1))

        # link activity2 to topic2 and topic3
        topic_list = [RelationValue(self.intids.getId(self.topic2)),
                      RelationValue(self.intids.getId(self.topic3))]
        self.activity2.topics = topic_list
        notify(ObjectModifiedEvent(self.activity2))

        # add activities to assessment1
        self.assessment1.assessment_items = [
                            RelationValue(self.intids.getId(self.activity1)),
                            RelationValue(self.intids.getId(self.activity2)),
                            RelationValue(self.intids.getId(self.activity3)),
                            ]
        notify(ObjectModifiedEvent(self.assessment1))

        self.activities.invokeFactory('upfront.assessmentitem.content.assessmentitem',
                                      'assessmentitem4', title='Activity4')
        self.activity4 = self.activities._getOb('assessmentitem4')
        
        # make sure we have server urls for sync and upload testing
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITARMIIRemoteServerSettings)
        settings.server_url = u'http://localhost:8080'
        settings.sync_server_url = u'http://localhost:8080/tarmii/'
        settings.sync_server_user = u'admin'
        settings.sync_server_password = u'admin'
