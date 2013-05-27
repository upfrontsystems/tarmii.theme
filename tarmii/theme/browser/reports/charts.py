from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Group, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
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

    def setDescription(self):
        desc = Label()        
        desc.fontName = 'Helvetica'
        desc.fontSize = 12
        desc.x = 230
        desc.y = 10
        desc._text = self._data_dict.get('description', '')
        desc.maxWidth = 280
        desc.height = 20
        desc.textAnchor ='middle'
        self.add(desc, name='Description')

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

    color_array = [colors.green, colors.red, colors.orange, colors.deepskyblue,
                   colors.olive, colors.gold, colors.blueviolet, colors.peru,
                   colors.grey, colors.honeydew, colors.pink, colors.lavender,
                   colors.indianred, colors.khaki, colors.black, colors.ivory,
                   colors.salmon, colors.seashell, colors.teal, colors.maroon ]
                  # 20 colors specified, rating scales over 20 will use color 20
                  # for colors 20+

    def __init__(self, data_dict, width=750, height=400, colorscheme='color'):
        chart = Pie()
        BaseChart.__init__(self,
                chart, data_dict, width, height, colorscheme=colorscheme)

        self._chart.width = 350
        self._chart.height = 300
        self._chart.slices.strokeWidth = 1.0
        self.setChartColors()
        self.setLabels()
        self.setLegend()
        self.setDescription()

    def setTitle(self):
        BaseChart.setTitle(self)
        self.Title.x = 230
        self.Title.y = 380

    def setDescription(self):
        BaseChart.setDescription(self)

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
        self._chart.slices.fontSize = 12
        self._chart.slices.fontName = 'Helvetica-Bold'
        self._chart.slices.fontColor = colors.black
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


class BaseLineChart(Drawing):

    def __init__(self, chart, data_dict, width=600, height=450,
                 colorscheme='color'):
        """ Initialize the basic graphing class.
            Set the chart, data, width, height and color scheme.
        """
        self._data_dict = data_dict
        Drawing.__init__(self, width, height)
        self.add(chart, name='_linechart')
        self._linechart.width = 900
        self._linechart.height = 240
        self._linechart.x = 50
        self._linechart.y = 80

        self._linechart.joinedLines = 1
        self._linechart.categoryAxis.categoryNames = self.getCategories()
        self._linechart.categoryAxis.labels.boxAnchor = 'n'
        self._linechart.valueAxis.valueMin = 0
        self._linechart.valueAxis.valueMax = self.getHighestScore()
        self._linechart.valueAxis.valueStep = 1
        self._linechart.lines[0].strokeWidth = 2
        self._linechart.lines[1].strokeWidth = 1.5
        self._linechart.lines[0].strokeColor = colors.green
        self._linechart.lines[1].strokeColor = colors.red

        self.setTitle()
        self._linechart.data = self.getChartData()

    def getChartData(self):
        return self._data_dict['value_data']

    def getCategories(self):
        return self._data_dict['category_data']

    def getHighestScore(self):
        return self._data_dict['highest_score']

    def setTitle(self):
        title = Label()        
        title.fontName = 'Helvetica-Bold'
        title.fontSize = 12
        title.x = 450
        title.y = 380
        title._text = self._data_dict.get('title', '')
        title.maxWidth = 180
        title.height = 20
        title.textAnchor ='middle'
        self.add(title, name='Title')

    def setAxesLabels(self):
        xlabel = Label()
        xlabel.fontName = 'Helvetica'
        xlabel.fontSize = 12
        xlabel.x = 450
        xlabel.y = 40
        xlabel._text = self._data_dict.get('xlabel', '')
        xlabel.maxWidth = 180
        xlabel.height = 20
        xlabel.textAnchor ='middle'
        self.add(xlabel, name='xlabel')

        ylabel = Label()
        ylabel.fontName = 'Helvetica'
        ylabel.fontSize = 12
        ylabel.x = 30
        ylabel.y = 210
        ylabel.angle = 90
        ylabel._text = self._data_dict.get('ylabel', '')
        ylabel.maxWidth = 180
        ylabel.height = 20
        ylabel.textAnchor ='middle'
        self.add(ylabel, name='ylabel')

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
        legend.x = 60
        legend.y = 50
        legend.columnMaximum = 2
        legend.colorNamePairs = []
        legend.colorNamePairs.append((colors.green,
                                           self._data_dict['max_score_legend']))
        legend.colorNamePairs.append((colors.red,
                                               self._data_dict['score_legend']))
        self.add(legend, name='Legend')

    
class ClassProgressChart(BaseLineChart):

    def __init__(self, data_dict, width=920, height=400, colorscheme='color'):
        chart = HorizontalLineChart()
        BaseLineChart.__init__(self,
                chart, data_dict, width, height, colorscheme=colorscheme)

        self._linechart.width = 860
        self._linechart.height = 270
        self.setLegend()
        self.setAxesLabels()

    def setTitle(self):
        BaseLineChart.setTitle(self)

    def setLegend(self):
        BaseLineChart.setLegend(self)

    def setAxesLabels(self):
        BaseLineChart.setAxesLabels(self)


class LearnerProgressChart(BaseLineChart):

    def __init__(self, data_dict, width=920, height=400, colorscheme='color'):
        chart = HorizontalLineChart()
        BaseLineChart.__init__(self,
                chart, data_dict, width, height, colorscheme=colorscheme)

        self._linechart.width = 860
        self._linechart.height = 270
        self.setLegend()
        self.setAxesLabels()

    def setTitle(self):
        BaseLineChart.setTitle(self)
 
    def setLegend(self):
        BaseLineChart.setLegend(self)

    def setAxesLabels(self):
        BaseLineChart.setAxesLabels(self)

