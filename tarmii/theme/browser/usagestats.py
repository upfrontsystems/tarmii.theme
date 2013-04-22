from cStringIO import StringIO
from datetime import datetime
from five import grok
from zope.interface import Interface

from zope.component import getUtility
from plone.directives import dexterity
from Products.CMFCore.utils import getToolByName

from tarmii.theme.interfaces import ISiteData
from tarmii.theme import MessageFactory as _

grok.templatedir('templates')

class UsageStatsView(grok.View):
    """ View to display usage stats from the log
    """
    grok.context(Interface)
    grok.name('usage-stats')
    grok.template('usagestats')
    grok.require('cmf.ManagePortal')

    def update(self, **kwargs):
        """ get log data from utility each time the template is rendered """
        sitedata = getUtility(ISiteData)
#        self.user_stats = sitedata.extract_logs()

        # XXX debug - currently calling directly
        view = self.context.restrictedTraverse('@@upload-to-server')
        test_data = StringIO()
        test_data.write(view.zip_csv())
        self.user_stats, self.stat_dates = sitedata.extract_logs_test(test_data)

        self.month = self.request.get('month-select')
        self.year = self.request.get('year-select')

        # set defaults to current month and year
        if self.month is None:
            self.month = str(datetime.now().month)
            if len(self.month) == 1:
                self.month = '0' + self.month
            self.request.set('month-select', self.month)
        if self.year is None:
            self.year = str(datetime.now().year)
            self.request.set('year-select', self.year)

    def stats(self):
        """ return all the site usage stats
        """
        new_activity = '++add++upfront.assessmentitem.content.assessmentitem'
        new_assessment = '++add++upfront.assessment.content.assessment'
        new_classlist = '++add++upfront.classlist.content.classlist'
        new_evaluationsheet= '++add++upfront.assessment.content.evaluationsheet'

        # reverse the dates, latest first
        self.stat_dates.reverse()

        stats = []
        for date in self.stat_dates:

            # filter via month and year
            # date format is: 19/04/2013
            if self.month in date[3:5] and self.year in date[6:10]:
                date_data = self.user_stats[date]
                stat_entry = { 'day' : date[0:2],
                               'activities_viewed' : 0,
                               'howto_clips_viewed' : 0,
                               'pedagogical_clips_viewed' : 0,                  
                               'teacher_resources_viewed' : 0,
                               'activities_created' : 0,
                               'assessments_created' : 0,
                               'classlists_created' : 0,
                               'evaluationsheets_created' : 0,
                             }

                # parse all the url paths from a specific date
                for entry in date_data:
                    if entry[-10:] == 'activities':
                        stat_entry['activities_viewed'] += 1
                    if entry.find('howto') != -1 and entry[-7:] == '@@video':
                        stat_entry['howto_clips_viewed'] += 1
                    if entry.find('pedagogic') != -1 and entry[-7:] == '@@video':
                        stat_entry['pedagogical_clips_viewed'] += 1
                    if entry[-9:] == 'resources':
                        stat_entry['teacher_resources_viewed'] += 1
    
                    if entry.find(new_activity) != -1:
                        stat_entry['activities_created'] += 1
                    if entry.find(new_assessment) != -1:
                        stat_entry['assessments_created'] += 1
                    if entry.find(new_classlist) != -1:
                        stat_entry['classlists_created'] += 1
                    if entry.find(new_evaluationsheet) != -1:
                        stat_entry['evaluationsheets_created'] += 1

                stats.append(stat_entry)

        return stats

