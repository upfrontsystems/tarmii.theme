from StringIO import StringIO
from reportlab.graphics import renderPM

from five import grok
from zope.interface import Interface
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

from tarmii.theme.browser.reports.charts import ClassPerformanceForActivityChart

grok.templatedir('templates')

class ClassPerformanceForActivityChartView(grok.View):
    """ Class performance for a given activity
    """
    grok.context(Interface)
    grok.name('classperformance-for-activity-chart')
    grok.require('zope2.View')

    def data(self):
        return { 
            'title' : 'Class performance for activity',
            'value_labels'   : (
                ('excellent', 'Excellent'),
                ('good', 'Good'),
                ('satisfactory', 'Satisfactory'),
                ('needsimprovement', 'Needs improvement')),
            'value_data' : (88, 6, 5, 1)
            }

    def render(self):
        request = self.request
        response = request.response

        drawing = ClassPerformanceForActivityChart(self.data())
        out = StringIO(renderPM.drawToString(drawing, 'PNG'))
        response.setHeader('expires', 0)
        response['content-type']='image/png'
        response['Content-Length'] = out.len
        response.write(out.getvalue())
        out.close()


class ClassPerformanceForActivityView(grok.View):
    """ Class performance for a given activity
    """
    grok.context(Interface)
    grok.name('classperformance-for-activity')
    grok.template('classperformance-for-activity')
    grok.require('zope2.View')

    def assessments(self):
        """ return all of the assessments of the current user
        """
        pm = getSite().portal_membership
        members_folder = pm.getHomeFolder()
        return members_folder.assessments.getFolderContents()

    def activities(self):
        """ return all of the activities of a specific assessment
        """
        assessment_uid = self.request.get('assessment_uid_selected', '')
        if assessment_uid == '':
            pm = getSite().portal_membership
            members_folder = pm.getHomeFolder()
            if len(members_folder.assessments.getFolderContents()) == 0:
                # assessments contains no activities
                return []
            else:                
                # no assessment selected so pick first one in list
                assessment = members_folder.assessments.getFolderContents()[0]\
                                                                    .getObject()
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            brain = catalog.searchResults(
                    portal_type='upfront.assessment.content.assessment',
                    UID=assessment_uid)
            assessment = brain[0].getObject()

        return assessment.assessment_items





    

