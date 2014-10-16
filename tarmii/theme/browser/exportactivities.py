import xlwt
import csv
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
    grok.name('export-activities-csv')
    grok.require('cmf.ManagePortal')

    def all_activities_csv(self):
        """ Export all activities in the system 
        """

        csv_content = None
        activities_csv = StringIO()

        # get all activities in the system
        catalog = getToolByName(self.context, 'portal_catalog')
        activities = catalog(portal_type=\
                                'upfront.assessmentitem.content.assessmentitem',
                                sort_on='id')

        # need to iterate over list of topictrees
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        for x in brains:
            if x.getObject().use_with_activities:
                topictree_list.append(x.getObject())

        fieldnames = ['ItemID'] + [x.title for x in topictree_list]

        # use numbers 1 .. x as the titles
        fieldindexes = [str(x) for x in range(1,len(fieldnames)+1)]

        if activities is not None and len(activities) > 0:
            writer = csv.DictWriter(activities_csv,
                                fieldindexes,
                                restval='',
                                extrasaction='ignore',
                                dialect='excel',
                                quoting=csv.QUOTE_ALL
                               )

            for activity in activities:
                ldict={}
                # start indexing at '1' to keep dictionary entries in correct 
                # order, for some reason 0 comes after 1 when used as index
                # in a python dict.
                ldict['1'] = activity.getObject().id
                for tree_index in range(len(topictree_list)):
                    ldict[str(tree_index+2)] = ''
                    # if activity has topics, use the topics else ''
                    if hasattr(activity.getObject(), 'topics'):
                        topics = activity.getObject().topics
                        for tag_index in range(len(topics)):
                            if topics[tag_index].to_object.aq_parent.id ==\
                                                 topictree_list[tree_index].id:
                                ldict[str(tree_index+2)] =\
                                              topics[tag_index].to_object.title
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
                                            "attachment; filename=%s.xls" % 
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


class ExportActivitiesXlsView(grok.View):
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
                                'upfront.assessmentitem.content.assessmentitem',
                                sort_on='id')

        # need to iterate over list of topictrees
        brains = catalog(portal_type='collective.topictree.topictree')
        topictree_list = []
        for x in brains:
            if x.getObject().use_with_activities:
                topictree_list.append(x.getObject())

        fieldnames = ['ItemID'] + [x.title for x in topictree_list]

        # use numbers 1 .. x as the titles
        fieldindexes = [str(x) for x in range(1,len(fieldnames)+1)]

        ezxf = xlwt.easyxf
        headings = ['ID']
        kinds = ['text']
        for x in range(len(topictree_list)):
            headings.append(self.context.translate(_('Topic')) + ' ' +\
                str(x+1) + ': ' + topictree_list[x].title)
            kinds.append('text')

        if activities is not None and len(activities) > 0:

            data = []
            for activity in activities:
                ldict=range(len(topictree_list)+1)
                # start indexing at '1' to keep dictionary entries in correct 
                # order, for some reason 0 comes after 1 when used as index
                # in a python dict.
                ldict[0] = activity.getObject().id
                for tree_index in range(len(topictree_list)):
                    ldict[tree_index+1] = ''
                    # if activity has topics, use the topics else ''
                    if hasattr(activity.getObject(), 'topics'):
                        topics = activity.getObject().topics
                        for tag_index in range(len(topics)):
                            if topics[tag_index].to_object.aq_parent.id ==\
                                                 topictree_list[tree_index].id:
                                ldict[tree_index+1] =\
                                              topics[tag_index].to_object.title
                data.append(ldict)

            heading_xf = ezxf('font: bold on; align: wrap on, '
                              'vert centre, horiz center')
            kind_to_xf_map = {
                'text': ezxf(),
                }
            data_xfs = [kind_to_xf_map[k] for k in kinds]

            book = xlwt.Workbook()
            sheet = book.add_sheet(self.context.title) # XXX make sure it is 
                                                       # utf sanitized
            rowx = 0
            for colx, value in enumerate(headings):
                sheet.write(rowx, colx, value, heading_xf)
            sheet.set_panes_frozen(True) # frozen headings instead of 
                                         # split panes
            sheet.set_horz_split_pos(rowx+1) # in general, freeze after last 
                                             # heading row
            sheet.set_remove_splits(True) # if user does unfreeze, don't leave 
                                          # a split there
            for row in data:
                rowx += 1
                for colx, value in enumerate(row):
                    sheet.write(rowx, colx, value, data_xfs[colx])

            book.save(activities_csv)
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
                                            "attachment; filename=%s.xls" % 
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

