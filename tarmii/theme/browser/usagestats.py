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
        """ get log data from utility each time the template is rendered
        """
        sitedata = getUtility(ISiteData)
        self.user_stats = sitedata.log_data

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

    def show_provinces(self):
        """ show teachers if both province and school are NOT on the request
        """
        province = bool(self.request.has_key('province'))
        school = bool(self.request.has_key('school'))
        return not province and not school

    def show_schools(self):
        """ show schools if province is on and school is NOT on the request
        """
        province = bool(self.request.has_key('province'))
        school = bool(self.request.has_key('school'))
        return province and not school

    def show_stats(self):
        """ show stats if both province and school are on the request 
        """
        province = bool(self.request.has_key('province'))
        school = bool(self.request.has_key('school'))
        return province and school

    def context_path(self):
        """ return context url 
        """
        return self.context.absolute_url()

    def province_request(self):
        """ return the province from the request 
        """
        return self.request.get('province')

    def school_request(self):
        """ return the school from the request
        """
        return self.request.get('school')

    def provinces(self):
        """ return all provinces from teacher_data object
        """
        province_list = []
        for province in range(len(self.user_stats.keys())):
            province_list.append(self.user_stats.keys()[province])
        province_list.sort()
        return province_list

    def schools(self):
        """ return all schools in current province from teacher_data object 
        """
        school_list = []
        province = self.request.get('province')
        for school in range(len(self.user_stats[province].items())):
            school_list.append(self.user_stats[province].items()[school][0])
        school_list.sort()
        return school_list

    def stats(self):
        """ return all the site usage stats
        """
        new_activity = '++add++upfront.assessmentitem.content.assessmentitem'
        new_assessment = '++add++upfront.assessment.content.assessment'
        new_classlist = '++add++upfront.classlist.content.classlist'
        new_evaluationsheet= '++add++upfront.assessment.content.evaluationsheet'

        stats = []
 
        province = self.request.get('province')
        school = self.request.get('school')
        stat_subset = self.user_stats.get(province)[school]

        # return data for currently selected month and year
        for day in reversed(range(1,32)):
            day_str = str(day)
            if len(day_str) == 1:
                # prepend 1..9 with a zero
                day_str = '0' + str(day)

            # date format is: 19/04/2013
            date_uuid = day_str + '/' + self.month + '/' + self.year

            if date_uuid in self.user_stats[province][school]:
                date_data = stat_subset[date_uuid]
                # create a blank entry template
                stat_entry = { 'day' : day_str,
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
                    if entry.find('pedagogic') != -1 and entry[-7:] =='@@video':
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
