from DateTime import DateTime
from five import grok
from zope.interface import Interface

from tarmii.theme import MessageFactory as _

class DownloadTeacherDataView(grok.View):
    """ Return the teacher data from uploadtoserver view as a http response.
    """
    grok.context(Interface)
    grok.name('download-teacher-data')
    grok.require('zope2.View')

    def __call__(self):
        """ Return zip content as http response
        """

        view = self.context.restrictedTraverse('@@upload-to-server')
        zip_data = view.zip_csv()
        now = DateTime()
        nice_filename = '%s_%s' % ('tarmii_logs_',now.strftime('%Y%m%d'))
        self.request.response.setHeader("Content-Disposition",
                                        "attachment; filename=%s.zip" % 
                                         nice_filename)
        self.request.response.setHeader("Content-Type", 
                                        'application/octet-stream')
        self.request.response.setHeader("Content-Length", len(zip_data))
        self.request.response.setHeader('Last-Modified',
                                         DateTime.rfc822(DateTime()))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(zip_data)

    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''
