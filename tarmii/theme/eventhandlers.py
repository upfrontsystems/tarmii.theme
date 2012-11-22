import os
import tempfile
import subprocess

from five import grok

from Acquisition import aq_parent
from zope.component.hooks import getSite

from Products.ATContentTypes.interfaces.file import IFileContent
from Products.Archetypes.interfaces import IObjectInitializedEvent
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
    if video.aq_parent.Title() != 'Videos':
        return
    
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(video.data)

    try:
        thumb = tempfile.gettempdir() + '/tmp.jpg'    
        # take the 5th second of video for thumb, -y overwrites old tmp.jpgfiles
        subprocess.call(["avconv", "-itsoffset", "-5", "-i", tmp.name,
                         "-vcodec", "mjpeg", "-y", "-vframes", "1", "-an", "-f",
                         "rawvideo", "-s", "265x150", thumb])       
    except: # XXX - change to try, finally -output message from avconv
            # Invalid data found when processing input 
        request = getattr(video, "REQUEST", None)
        IStatusMessage(request).addStatusMessage(
                                    _(u"Thumbnail generation failed"),"error")

    #read in tmp.jpg 
    cwd = os.path.join(tempfile.gettempdir(), 'tmp.jpg')
    f = open(cwd, "rb")
    try:
        fileRawData = f.read()
    except:
        # file could not be read
        # XXX: add exception message
        return

    finally:
        f.close()

    # create an image object from tmp.jpg data
    video_id = video.id + '-thumb'
    video.aq_parent.invokeFactory('Image', video_id, title=video.title,
                                  image=fileRawData)


@grok.subscribe(IPropertiedUser, IUserInitialLoginInEvent)
def on_user_initial_login(user, event):
    """ Create classlists folder inside members folder upon initial login
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

