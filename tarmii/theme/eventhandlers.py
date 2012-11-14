from five import grok
from Acquisition import aq_parent

from Products.ATContentTypes.interfaces.file import IFileContent
from Products.Archetypes.interfaces import IObjectInitializedEvent

@grok.subscribe(IFileContent, IObjectInitializedEvent)
def onVideoAdded(video, event):
    """ Create Thumbnail file from a video file.
    """

    # test that the object created was added to the videos folder (is a video)
    if video.aq_parent.Title() != 'Videos':
        return
    
    print 'Video added'


