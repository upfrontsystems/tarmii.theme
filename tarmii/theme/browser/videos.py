from five import grok
import cStringIO

from AccessControl import getSecurityManager
from zope.interface import Interface

from Products.CMFPlone.PloneBatch import Batch
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName

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
        category = self.request.get('category', "")

        if category == '':
            # check cookie first
            cookie = self.request.cookies.get("VIDEO_PAGE", "")
            if cookie == "" or cookie == "Howto":
                brains = self.context.howto.getFolderContents(contentFilter)
            else:
                brains = self.context.pedagogic.getFolderContents(contentFilter)

        if category == 'howto':
            brains = self.context.howto.getFolderContents(contentFilter)
        elif category == 'pedagogic':
            brains = self.context.pedagogic.getFolderContents(contentFilter)
      
        b_size = 9
        b_start = self.request.get('b_start', 0)
        return Batch(brains, b_size, int(b_start), orphan=0)

    def addvideo_visible(self):
        """ test if add video button can be shown based on whether the user
            has "AddPortalContent" Permission on the resouces folder
        """
        return getSecurityManager().checkPermission(AddPortalContent,
                                                    self.context)

    def user_is_admin(self):
        """ Test if the current user is an admin user, test this by checking if
            they have "ManagePortal" Permission on the context
        """
        return getSecurityManager().checkPermission(ManagePortal,self.context)

    def display_howto_videos(self):
        """ Check which video page to display based on VIDEO_PAGE cookie and 
            the category parameter on the request (which takes precedence)".
        """

        category = self.request.get('category', "")

        if category == '':
            # check the cookie
            cookie = self.request.cookies.get("VIDEO_PAGE", "")
            if cookie == "" or cookie == "Howto":
                return True
            else:
                return False

        if category == 'howto':
            self.request.response.setCookie("VIDEO_PAGE", 'Howto')
            return True
        else:
            self.request.response.setCookie("VIDEO_PAGE", 'Pedagogic')
            return False

    def video_link(self, thumb):
        return thumb.absolute_url()[:-6] # strip '-thumb' from the url
    
    def context_url(self):
        return self.context.absolute_url()


class VideoView(grok.View):
    """ A view to display a single video
    """
    grok.context(Interface)
    grok.name('video')
    grok.template('video')
    grok.require('zope2.View')

    def video_link(self):
        """ return the download url of a video 
        """
        return '%s/at_download/file' % self.context.absolute_url()
