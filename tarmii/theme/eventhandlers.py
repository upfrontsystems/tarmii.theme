import os
import subprocess
import tempfile
from five import grok
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent
from zope.component.hooks import getSite

from Products.ATContentTypes.interfaces.file import IFileContent
from Products.Archetypes.interfaces import IObjectInitializedEvent
from Products.ATContentTypes.lib.constraintypes import ENABLED
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from Products.PlonePAS.interfaces.events import IUserInitialLoginInEvent

from Products.statusmessages.interfaces import IStatusMessage

from tarmii.theme import MessageFactory as _

@grok.subscribe(IFileContent, IObjectInitializedEvent)
def on_video_added(video, event):
    """ Create Thumbnail file from a video file.
    """

    # Only create thumbnails for Files uploaded to the videos folder
    # and not for files uploaded elsewhere like teacher resources
    if video.aq_parent.id != 'videos':
        return

    fd, infilename = tempfile.mkstemp()
    fd, outfilename = tempfile.mkstemp()
    try:
        infile = open(infilename, 'w+')
        infile.write(video.data)
    finally:
        infile.close()

    cmdargs = ['avconv', '-loglevel', 'error' , '-ss', '30', '-i', 
               infilename, '-vcodec', 'mjpeg', '-y', '-vframes', '1', '-an', 
               '-f', 'image2', '-s', '265x150', outfilename]
    process = subprocess.Popen(cmdargs, 
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stderr == '':
        #if no errors from avconv - create thumbnail image
        video_id = video.id + '-thumb'
        f = open(outfilename)
        try:
            image_data = f.read()
        finally:
            f.close()
        video.aq_parent.invokeFactory('Image', video_id, title=video.title,
                                      image=image_data)

        # generate link so that we can get the video url from its thumbnail obj
        thumb_obj = video.aq_parent._getOb(video_id)
        thumb_obj.link = thumb_obj.aq_parent.absolute_url() + '/' + video.id
        notify(ObjectModifiedEvent(thumb_obj))

    else:
        #display errors in detail
        request = getattr(video, "REQUEST", None)
        IStatusMessage(request).addStatusMessage(
                                    _(u"Thumbnail generation failed"),"error")
        IStatusMessage(request).addStatusMessage(stderr,"info")

    os.remove(infilename)
    os.remove(outfilename)

    return

@grok.subscribe(IFileContent, IObjectRemovedEvent)
def on_video_deleted(video, event):
    """ Delete the corresponding thumbnail when a video has been deleted.
    """

    portal = getToolByName(video, 'portal_url').getPortalObject()
    if portal.hasProperty('removal_inprogress'):
        if portal.removal_inprogress:
            return

    # We only want to take action when a video file has being deleted
    if video.aq_parent.id != 'videos' or video.portal_type != 'File':
        return

    # find the corresponding thumbnail object
    contentFilter = {"portal_type" : "Image"}    
    thumbname = video.id + '-thumb'
    thumb_obj =  filter(lambda x: x.id == thumbname,
      [x.getObject() for x in video.aq_parent.getFolderContents(contentFilter)])

    # delete the thumbnail object
    parent = thumb_obj[0].aq_parent
    parent.manage_delObjects(thumb_obj[0].getId())

@grok.subscribe(IPropertiedUser, IUserInitialLoginInEvent)
def on_user_initial_login(user, event):
    """ Create classlists and assessments folders inside members folder upon
        initial login
    """

    pm = getSite().portal_membership
    # create members folder
    pm.createMemberArea()
    members_folder = pm.getHomeFolder()
    # create classlists folder in members folder
    members_folder.invokeFactory(type_name='Folder', id='classlists',
                                 title='Class Lists')
    classlists_folder = members_folder._getOb('classlists')
    # set default view to @@classlists view
    classlists_folder.setLayout('@@classlists')

    # create assessments folder in members folder
    members_folder.invokeFactory(type_name='Folder', id='assessments',
                                 title='Assessments')
    assessments_folder = members_folder._getOb('assessments')
    allowed_types = ['upfront.assessment.content.assessment']
    assessments_folder.setConstrainTypesMode(ENABLED)
    assessments_folder.setLocallyAllowedTypes(allowed_types)
    assessments_folder.setImmediatelyAddableTypes(allowed_types)
    # set default view to @@assessments view
    assessments_folder.setLayout('@@assessments')

    # create evaluation folder in members folder
    members_folder.invokeFactory(type_name='Folder', id='evaluations',
                                 title='Evaluations')
    evaluation_folder = members_folder._getOb('evaluations')
    allowed_types = ['upfront.assessment.content.evaluationsheet']
    evaluation_folder.setConstrainTypesMode(ENABLED)
    evaluation_folder.setLocallyAllowedTypes(allowed_types)
    evaluation_folder.setImmediatelyAddableTypes(allowed_types)
    # set default view to @@evaluationsheets view
    evaluation_folder.setLayout('@@evaluationsheets')

    # invokefactory is not setting folder titles correctly, so set them manually
    classlists_folder.title = 'Class Lists'
    assessments_folder.title = 'Assessments'
    evaluation_folder.title = 'Evaluations'

