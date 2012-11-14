import os
import tempfile
from five import grok
from Acquisition import aq_parent
from subprocess import call

from Products.ATContentTypes.interfaces.file import IFileContent
from Products.Archetypes.interfaces import IObjectInitializedEvent

@grok.subscribe(IFileContent, IObjectInitializedEvent)
def onVideoAdded(video, event):
    """ Create Thumbnail file from a video file.
    """

    # test that the object created was added to the videos folder 
    # (test that this File is indeed a video file.)
    if video.aq_parent.Title() != 'Videos':
        return
    
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(video.data)

    thumb = tempfile.gettempdir() + '/tmp.jpg'
    # take the 5th second of video for thumb, -y overwrites old tmp.jpg files.
    call(["ffmpeg", "-itsoffset", "-5", "-i", tmp.name, "-vcodec", "mjpeg", "-y",
          "-vframes", "1", "-an", "-f", "rawvideo", "-s", "320x180", thumb])

    #read in tmp.jpg 
    cwd = os.path.join(tempfile.gettempdir(), 'tmp.jpg')
    f = open(cwd, "rb")
    fileRawData = f.read()

    # create an image object from tmp.jpg data
    video_id = video.title + '_'
    video.aq_parent.invokeFactory('Image', video_id, image=fileRawData)
