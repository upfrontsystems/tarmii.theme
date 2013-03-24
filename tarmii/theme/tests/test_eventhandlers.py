import os
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.component.hooks import getSite
from plone.app.controlpanel.security import ISecuritySchema
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from base import TarmiiThemeTestBase
from tarmii.theme.eventhandlers import on_user_initial_login, on_video_added,\
                                       on_video_deleted

class TestEventhandlers(TarmiiThemeTestBase):
    """ Test event handlers """
    
    def test_on_video_added(self):

        # supply a bad file and test for error status messages
        testpath = os.path.dirname(__file__)
        path = os.path.join(testpath,'test_fakevideo.flv')
        video_data = open(path,'rb')

        self.videos_howto.invokeFactory('File', 'vid1', title='Vid1')
        self.vid1 = self.videos_howto._getOb('vid1')
        self.vid1.data=video_data.read()
        notify(ObjectModifiedEvent(self.vid1))
        video_data.close() 

        on_video_added(self.vid1, None)

        test = IStatusMessage(self.request).show()
        self.assertEqual(test[0].type,'error')
        self.assertEqual(test[0].message,'Thumbnail generation failed')
        self.assertEqual(test[1].type,'info')
        # the last part of the error message should be 
        # 'Invalid data found when processing input\n'
        # Before that it mentions a specific temporary file path
        self.assertEqual(test[1].message[-41:],
                                'Invalid data found when processing input\n')

        # test that thumbnail was correctly created from a supplied video file
        path = os.path.join(testpath,'test_video.flv')
        video_data = open(path,'rb')

        self.videos_howto.invokeFactory('File', 'vid2', title='Vid2')
        self.vid2 = self.videos_howto._getOb('vid2')
        self.vid2.data=video_data.read()
        notify(ObjectModifiedEvent(self.vid2))
        video_data.close()

        cFilter = {"portal_type" : "Image"}
        # 2 thumbnails that are in base.py
        self.assertEqual(len(self.videos_howto.getFolderContents(cFilter)),2)

        on_video_added(self.vid2, None)
        
        #assert that another thumbnail has been created
        self.assertEqual(len(self.videos_howto.getFolderContents(cFilter)),3)
       
        thumb = self.videos_howto.getFolderContents(cFilter)[2].getObject()
        self.assertEqual(thumb.id,'vid2-thumb')


    def test_on_video_deleted(self):

        # add a video to the system and create thumbnail
        testpath = os.path.dirname(__file__)
        path = os.path.join(testpath,'test_video.flv')
        video_data = open(path,'rb')
        self.videos_howto.invokeFactory('File', 'vid2', title='Vid2')
        self.vid2 = self.videos_howto._getOb('vid2')
        self.vid2.data=video_data.read()
        notify(ObjectModifiedEvent(self.vid2))
        video_data.close()
        cFilter = {"portal_type" : "Image"}
        # 2 thumbnails that are in base.py
        self.assertEqual(len(self.videos_howto.getFolderContents(cFilter)),2)
        on_video_added(self.vid2, None)        
        # assert that another thumbnail has been created
        self.assertEqual(len(self.videos_howto.getFolderContents(cFilter)),3)       
        thumb = self.videos_howto.getFolderContents(cFilter)[2].getObject()
        self.assertEqual(thumb.id,'vid2-thumb')

        # delete the thumbnail of self.vid2
        on_video_deleted(self.vid2, None)
        # thumbnail has been deleted - only 2 thumbnails remain
        self.assertEqual(len(self.videos_howto.getFolderContents(cFilter)),2)
        ref = [x.id for x in self.videos_howto.getFolderContents(cFilter)]
        self.assertEqual(ref,['vid1thumb','vid2thumb'])
        # self.vid2 has not been deleted because the eventhandler only deletes
        # the thumbnail
        self.assertEqual(self.videos_howto.getFolderContents()[2].getObject(),
                         self.vid2)

    def test_on_user_initial_login(self):

        # create user
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
        # first 3 folder objects are the ones created in base.py
        # the ones created by on_user_initial_login are effectively objects 4-6
        self.assertEquals(brains[3].getObject().id,'classlists')
        self.assertEquals(brains[3].getObject().getLayout(),'@@classlists')
        self.assertEquals(brains[4].getObject().id,'assessments')
        self.assertEquals(brains[4].getObject().getLayout(),'@@assessments')
        self.assertEquals(brains[5].getObject().id,'evaluations')
        self.assertEquals(brains[5].getObject().getLayout(),'@@evaluationsheets')

