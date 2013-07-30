from five import grok
from zope.interface import Interface
from zope.component import getUtility

from tarmii.theme.interfaces import ISiteData

class TeacherDataView(grok.View):
    """ View for handling the zip data that has been sent from a TARMII system
    """
    grok.context(Interface)
    grok.name('teacher-data')
    grok.require('cmf.ManagePortal')

    def __call__(self):
        """ store a file that is present on the request in a persistent utility
        """
        zipped_data = self.request.get('BODY')
        print 'IN TEACHERDATA'
        import pdb; pdb.set_trace() # so that we can see if were getting anything
                                    # off the request
        sitedata = getUtility(ISiteData)
        sitedata.store_data(zipped_data)

    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''       

