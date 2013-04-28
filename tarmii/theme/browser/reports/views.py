from StringIO import StringIO
from reportlab.graphics import renderPM

from five import grok
from zope.interface import Interface
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

        drawing = ClassPerformanceForActivityChart(self.data)
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

