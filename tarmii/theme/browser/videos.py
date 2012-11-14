from five import grok
from subprocess import call

from Acquisition import aq_inner
#from Products.CMFCore.utils import getToolByName
from zope.interface import Interface

from Products.CMFPlone.PloneBatch import Batch

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
        brains = self.context.getFolderContents()
        b_size = 5
        b_start = self.request.get('b_start', 0)
        import pdb; pdb.set_trace()
        return Batch(brains, b_size, int(b_start), orphan=0)


