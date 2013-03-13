from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Group, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.legends import Legend

class BaseChart(Drawing):

    def __init__(self, chart, data_dict, width=600, height=450,
                 colorscheme='color'):
        """ Initialize the basic graphing class.
            Set the chart, data, width, height and color scheme.
        """
        self._data_dict = data_dict

        Drawing.__init__(self, width, height)
        self.add(chart, name='_chart')

        self._chart.width = 500
        self._chart.height = 240
        self._chart.x = 50
        self._chart.y = 40
        self._chart.fillColor = colors.white
        self.fontname = 'Helvetica-Bold'
        self.fontsize = 12
        self.setTitle()

        # Add some data to the chart
        self._chart.data = self.getChartData()

    def getChartData(self):
        return self._data_dict['value_data']

    def setTitle(self):
        title = Label()        
        title.fontName = self.fontname
        title.fontSize = self.fontsize
        title.x = 300
        title.y = 335
        title._text = self._data_dict.get('title', '')
        title.maxWidth = 180
        title.height = 20
        title.textAnchor ='middle'
        self.add(title, name='Title')

    def setLegend(self):
        legend = Legend()
        legend.colorNamePairs = []
        legend.fontName = self.fontname
        legend.fontSize = self.fontsize
        legend.x = 100
        legend.y = 310
        legend.dxTextSpace = 5
        legend.dy = 20
        legend.dx = 20
        # legend.deltay = 5
        legend.deltax = 7
        legend.columnMaximum = 1
        legend.alignment ='right'
        self.add(legend, name='Legend')


class ClassPerformanceForActivity(BaseChart):
    def __init__(self, data_dict, width=300, height=325, colorscheme='color'):
        chart = Pie()
        GraphAssessmentBank.__init__(self,
                chart, data_dict, width, height, colorscheme=colorscheme)

        self._chart.width = 500
        self._chart.height = 240
        self._chart.slices.strokeWidth = 0.5
        self.setChartColors()
        self.setLabels()

    def setTitle(self):
        GraphAssessmentBank.setTitle(self)
        self.Title.x = 150
        self.Title.y = 300 

    def setLegend(self):
        GraphAssessmentBank.setLegend(self)
        self.Legend.x = 400
        self.Legend.y = 200
        self.Legend.columnMaximum = len(self._data_dict['value_labels'])
        color0 = colors.green
        color1 = colors.red
        self.Legend.colorNamePairs = \
                [
                (color0, self._data_dict['value_labels'][0]),
                (color1, self._data_dict['value_labels'][1])
                ]

    def setChartColors(self):
        self._chart.slices.fontSize = 30
        self._chart.slices.fontColor = colors.white
        self._chart.slices[0].fillColor = colors.green
        self._chart.slices[1].fillColor = colors.red

    def setLabels(self):
        self._chart.labels = self._data_dict['category_labels']
        for idx in range(len(self._data_dict['value_data'])):
            self._chart.slices[idx].labelRadius = 0.5


