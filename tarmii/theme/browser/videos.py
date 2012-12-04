from five import grok

from AccessControl import getSecurityManager
from zope.interface import Interface

from Products.CMFPlone.PloneBatch import Batch
from Products.CMFCore.permissions import AddPortalContent

from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class VideosView(grok.View):
    """ A view to display the all the videos in the system and the upload button
    """
    grok.context(Interface)
    grok.name('videos')
    grok.template('videos')
    grok.require('zope2.View')

    def videos(self):
        """ query for contents of videos folder and return as batch
        """
        contentFilter = {"portal_type" : "Image"}
        brains = self.context.getFolderContents(contentFilter)
        b_size = 9
        b_start = self.request.get('b_start', 0)
        return Batch(brains, b_size, int(b_start), orphan=0)

    def addvideo_visible(self):
        """ test if add video button can be shown based on whether the user
            has "AddPortalContent" Permission on the resouces folder
        """
        return getSecurityManager().checkPermission(AddPortalContent,
                                                    self.context)

    def add_video_button_path(self):
        """ Path string for the Add Video button
        """
        # XXX: we need some sort of check to make sure only flv extensions are
        # allowed to be uploaded.
        return '%s/createObject?type_name=File' % self.context.absolute_url()





