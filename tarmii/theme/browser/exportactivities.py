from csv import DictWriter
from cStringIO import StringIO
from DateTime import DateTime

from five import grok
from zope.interface import Interface

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.utils import getToolByName

from tarmii.theme import MessageFactory as _

class ExportActivitiesView(grok.View):
    """ Export all activities in the system 
    """
    grok.context(Interface)
    grok.name('export-activities')
    grok.require('cmf.ManagePortal')

    def all_activities_csv(self):
        """ Export all activities in the system 
        """

        csv_content = None
        activities_csv = StringIO()

        # get all activities in the system
        catalog = getToolByName(self.context, 'portal_catalog')
        activities = catalog(portal_type=\
                                'upfront.assessmentitem.content.assessmentitem')

        # need to iterate over list of topictrees
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        for x in brains:
            if x.getObject().use_with_activities:
                topictree_list.append(x.getObject().title)

        fieldnames = ['ItemID'] + topictree_list

        if activities is not None and len(activities) > 0:
            writer = DictWriter(activities_csv,
                                fieldnames,
                                restval='',
                                extrasaction='ignore',
                                dialect='excel'
                               )

            for activity in activities:
                ldict={}

                writer.writerow(ldict)
           
            csv_content = activities_csv.getvalue()
            activities_csv.close()

        return csv_content

    def __call__(self):
        """ Return csv content as http response or return info IStatusMessage
        """

        csv_content = self.all_activities_csv()

        if csv_content is not None:
            now = DateTime()
            nice_filename = '%s_%s' % ('activities_', now.strftime('%Y%m%d'))
            self.request.response.setHeader("Content-Disposition",
                                            "attachment; filename=%s.csv" % 
                                             nice_filename)
            self.request.response.setHeader("Content-Type", "text/csv")
            self.request.response.setHeader("Content-Length", len(csv_content))
            self.request.response.setHeader('Last-Modified',
                                            DateTime.rfc822(DateTime()))
            self.request.response.setHeader("Cache-Control", "no-store")
            self.request.response.setHeader("Pragma", "no-cache")
            self.request.response.write(csv_content)
        else:
            msg = _('No activities exist')
            IStatusMessage(self.request).addStatusMessage(msg,"info")

        # redirect to show the info message
        self.request.response.redirect(
                '/'.join(self.context.getPhysicalPath()))

        return csv_content

    def render(self):
        """ No-op to keep grok.View happy
        """
        return ''
