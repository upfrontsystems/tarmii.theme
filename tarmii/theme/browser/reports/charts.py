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
        self.setTitle()

        # Add some data to the chart
        self._chart.data = self.getChartData()

    def getChartData(self):
        return self._data_dict['value_data']

    def setTitle(self):
        title = Label()        
        title.fontName = 'Helvetica-Bold'
        title.fontSize = 12
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
        legend.fontName = 'Helvetica-Bold'
        legend.fontSize = 12
        legend.x = 100
        legend.y = 110
        legend.dxTextSpace = 5
        legend.dy = 20
        legend.dx = 20
        legend.deltay = 5
        legend.deltax = 7
        legend.columnMaximum = 1
        legend.alignment ='right'
        self.add(legend, name='Legend')


class ClassPerformanceForActivityChart(BaseChart):

    color_array = [colors.green, colors.red, colors.gold, colors.deepskyblue,
                   colors.olive, colors.orange, colors.blueviolet, colors.peru,
                   colors.grey, colors.honeydew, colors.pink, colors.lavender,
                   colors.indianred, colors.khaki, colors.black, colors.ivory,
                   colors.salmon, colors.seashell, colors.teal, colors.maroon ]
                  # 20 colors specified, rating scales over 20 will use color 20
                  # for colors 20+

    def __init__(self, data_dict, width=600, height=400, colorscheme='color'):
        chart = Pie()
        BaseChart.__init__(self,
                chart, data_dict, width, height, colorscheme=colorscheme)

        self._chart.width = 350
        self._chart.height = 300
        self._chart.slices.strokeWidth = 1.0
        self.setChartColors()
        self.setLabels()
        self.setLegend()

    def setTitle(self):
        BaseChart.setTitle(self)
        self.Title.x = 230
        self.Title.y = 380 

    def setLegend(self):
        BaseChart.setLegend(self)
        self.Legend.x = 450
        self.Legend.y = 200
        self.Legend.columnMaximum = len(self._data_dict['value_labels'])
        self.Legend.colorNamePairs = []
        for x in range(len(self._data_dict['value_labels'])):
            if x < 20:
                self.Legend.colorNamePairs.append((self.color_array[x],
                                            self._data_dict['value_labels'][x]))
            else:
            # prevent crash due to running out of colors if rating scale > 20
                self.Legend.colorNamePairs.append((self.color_array[19],
                                            self._data_dict['value_labels'][x]))

    def setChartColors(self):
        self._chart.slices.fontSize = 20
        self._chart.slices.fontName = 'Helvetica-Bold'
        self._chart.slices.fontColor = colors.white
        for x in range(len(self._data_dict['value_labels'])):
            if x < 20:
                self._chart.slices[x].fillColor = self.color_array[x]
            else:
            # prevent crash due to running out of colors if rating scale > 20
                self._chart.slices[x].fillColor = self.color_array[19]

    def setLabels(self):
        self._chart.labels = self._data_dict['category_labels']
        for idx in range(len(self._data_dict['value_data'])):
            self._chart.slices[idx].labelRadius = 0.8

