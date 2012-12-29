import os
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.component.hooks import getSite
from plone.app.controlpanel.security import ISecuritySchema
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from base import TarmiiThemeTestBase
from tarmii.theme.eventhandlers import on_user_initial_login, on_video_added

class TestEventhandlers(TarmiiThemeTestBase):
    """ Test event handlers """
    
    def test_on_video_added(self):

        # supply a bad file and test for error status messages
        testpath = os.path.dirname(__file__)
        path = os.path.join(testpath,'test_fakevideo.flv')
        video_data = open(path,'rb')

        self.videos.invokeFactory('File', 'vid1', title='Vid1')
        self.vid1 = self.videos._getOb('vid1')
        self.vid1.data=video_data.read()
        notify(ObjectModifiedEvent(self.vid1))
        video_data.close() 

        on_video_added(self.vid1, None)

        test = IStatusMessage(self.request).show()
        self.assertEqual(test[0].type,'error')
        self.assertEqual(test[0].message,'Thumbnail generation failed')
        self.assertEqual(test[1].type,'info')
        self.assertEqual(test[1].message,
                         'pipe:0: Invalid data found when processing input\n')

        # test that thumbnail was correctly created from a supplied video file
        path = os.path.join(testpath,'test_video.flv')
        video_data = open(path,'rb')

        self.videos.invokeFactory('File', 'vid2', title='Vid2')
        self.vid2 = self.videos._getOb('vid2')
        self.vid2.data=video_data.read()
        notify(ObjectModifiedEvent(self.vid2))
        video_data.close()

        contentFilter = {"portal_type" : "Image"}
        # 2 thumbnails that are in base.py
        self.assertEqual(len(self.videos.getFolderContents(contentFilter)),2)

        on_video_added(self.vid2, None)
        
        #assert that another thumbnail has been created
        self.assertEqual(len(self.videos.getFolderContents(contentFilter)),3)
        thumb = self.videos.getFolderContents(contentFilter)[2].getObject()
        self.assertEqual(thumb.id,'vid2-thumb')


    def test_on_user_initial_login(self):

        #create user
        username = 'testuser1'
        passwd = username
        email = 'testuser1@email.com'
        title = 'Test User1'
        properties = {'username' : username,
                      'fullname' : title.encode("utf-8"),
                      'email' : email,   
                     }

        portal = getSite()
        # allow member folders to be created
        security_adapter =  ISecuritySchema(portal)
        security_adapter.set_enable_user_folders(True)
        # enable self-registration of users
        security_adapter.set_enable_self_reg(True)

        regtool = getToolByName(portal, 'portal_registration')
        member = regtool.addMember(username, passwd, properties=properties)

        pm = portal.portal_membership
        acl = getSite().acl_users
        acl.session._setupSession(username,self.request.RESPONSE)

        # call event
        on_user_initial_login(member,None)

        brains = pm.getHomeFolder().getFolderContents()
        self.assertEquals(brains[0].getObject().id,'classlists')
        self.assertEquals(brains[0].getObject().getLayout(),'@@classlists')
        self.assertEquals(brains[1].getObject().id,'assessments')
        self.assertEquals(brains[1].getObject().getLayout(),'@@assessments')
        self.assertEquals(brains[2].getObject().id,'evaluation')
        self.assertEquals(brains[2].getObject().getLayout(),'@@evaluationsheets')


