from turtle import window_width
import requests
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource,DatetimeTickFormatter,Select,FactorRange,DataTable,TableColumn,Div, HoverTool,DateFormatter,TapTool,LabelSet
from bokeh.layouts import layout
from bokeh.plotting import figure,show
from datetime import datetime
from math import radians # Rotate axis ticks
import numpy as np
from bokeh.layouts import gridplot,row,column
import pandas as pd
from bokeh.models.widgets import Tabs, Panel
import numpy as np
from bokeh.palettes import Spectral10,PuOr10,Spectral3,Category10_3,Spectral5
from bokeh.transform import factor_cmap,cumsum
from math import pi
from bokeh.events import Tap
from bokeh.models.annotations import Title


def inv_plot():
    data=pd.read_csv('sample_data.csv')
    data=data.fillna(0)
    data['date']=pd.to_datetime(data['date'])
    data['category']=data['category'].astype(str)

    #List of product for Dropdown
    listproduct=[]
    list=data['sku'].unique()
    list=list.sort()
    for item in data['sku'].unique():
        listproduct.append((item,item))
    data=data.sort_values(by='date')
    def top_sold(item):
        databar=data.groupby(item).sum()['sold']
        databar=databar.sort_values(ascending=False)
        databar=databar.reset_index()
        databar['sold']=pd.to_numeric(databar['sold'])
        databar=ColumnDataSource(data=dict(x=np.array(databar[item][:10]),y=np.array(databar['sold'][:10])))
        category=databar.data['x']
        cyl_cmap = factor_cmap('x', palette=Spectral10*320, factors=data[item].unique())

        p2=figure(
            width=750,height=500,
            x_range=category,
            title='Top 10 Most Sold Items by {}'.format(item),
            y_axis_label='Sold Items',
            tools='hover',
            tooltips=[('{}'.format(item),'@x'),('sold items','@y')],
            toolbar_location=None)
        p2.vbar(x='x',top='y',source=databar, line_color=cyl_cmap, fill_color=cyl_cmap,width=0.7)
        p2.x_range.range_padding = 0.1
        p2.xaxis.major_label_orientation = 1
        labels = LabelSet(x='x', y='y', text='y',text_color="#0000FF",text_font='Robotic',text_font_size='10pt',text_align='center', level='glyph',x_offset=0, y_offset=0, source=databar, render_mode='canvas')

        p2.add_layout(labels)
        # Level 1 graph
        p3=figure(
            width=750,height=500,x_range=FactorRange(),
            y_axis_label='Sold Items',
            tools='hover',
            tooltips=[('{}'.format('category'),'@x'),('sold items','@y')],
            toolbar_location=None)
        p3.outline_line_color=None
        p3.axis.visible=False
        p3.grid.visible=False

        # Data Table
        datefmt = DateFormatter(format="%Y-%m-%d")
        columns = [
                    TableColumn(field="date", title="DATE",formatter=datefmt),
                    TableColumn(field="sku", title="SKU"),
                    TableColumn(field="category", title="Category"),
                    TableColumn(field="stock", title="Stock"),
                    TableColumn(field="sold", title="Sold")
                ]
        source=ColumnDataSource()
        p4=DataTable(source=source, columns=columns, width=750, height=500)
        p4.visible=False

        #Taptool
        def tapfunc():
            tab_index=databar.selected.indices[0]
            # bar_level_one(databar.data['x'][tab_index])
            # print(databar.data['x'][tab_index])
        def sourcefunc(attr, old, new):
            line_data1=data[data['category']==databar.data['x'][new[0]]].groupby('sku').sum()['sold'].sort_values(ascending=False).reset_index()['sku'][:10]
            line_data2=data[data['category']==databar.data['x'][new[0]]].groupby('sku').sum()['sold'].sort_values(ascending=True).reset_index()['sku'][:10]
            value=[]
            print(new[0])
            for item_1 in line_data1:
                value.append(data[data['sku']==item_1]['sold'].sum())
            databar2=ColumnDataSource(data=dict(x=line_data1,y=value))
            category_data=databar2.data['x'].to_list()
            print(databar2.data['x'].to_list())
            cyl_cmap = factor_cmap('x', palette=Spectral10*320, factors=data['sku'].unique())
            p3.x_range.factors=category_data
            p3.vbar(x='x',top='y',source=databar2, line_color='white', fill_color=cyl_cmap,width=0.7)
            p3.x_range.range_padding = 0.1
            p3.xaxis.major_label_orientation = 1
            p3.outline_line_color='black'
            p3.axis.visible=True
            p3.grid.visible=True
            p3.title.text = 'Top 10 Most Sold Items in {}'.format(databar.data['x'][new[0]])
            labels2 = LabelSet(x='x', y='y', text='y',text_color="#0000FF",text_font='Robotic',text_font_size='10pt',text_align='center', level='glyph',x_offset=0, y_offset=0, source=databar2, render_mode='canvas')
            p3.add_layout(labels2)
            def sourcefunc2(attr, old, new):
                source.data=data[data['sku']==databar2.data['x'][new[0]]]
                p4.visible=True
            databar2.selected.on_change('indices', sourcefunc2)
            p4.visible=False

    
            
        databar.selected.on_change('indices', sourcefunc)

        p2.add_tools(TapTool())
        p2.on_event(Tap, tapfunc)
        p3.add_tools(TapTool())
        p3.on_event(Tap, tapfunc)
    
        return p2,p3,p4

    top_sold_sku=top_sold('category')
    text_title="""
        <html>
        <head>
        <style>
        h1 {text-align: center;}
        p {text-align: center;}
        div {text-align: center;}
        </style>
        </head>
        <body>
        <h1>Drilldown Example</h1>
        </body>
        </html>
        """

    lay_out=layout([
        [Div(text=text_title,width=11000)],
        [top_sold_sku[0],top_sold_sku[1]],
        [top_sold_sku[2]]
        ],sizing_mode='fixed')


        # Tab Cofig
    tab1=Panel(child=lay_out,title='Invisible plot')
    return tab1
