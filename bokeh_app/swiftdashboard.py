from turtle import window_width
import requests
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource,DatetimeTickFormatter,Select,FactorRange,DataTable,TableColumn,Div, HoverTool
from bokeh.layouts import layout
from bokeh.plotting import figure,show
from datetime import datetime
from math import radians # Rotate axis ticks
import numpy as np
from bokeh.layouts import gridplot,row,column
import pandas as pd
from bokeh.models.widgets import Tabs, Panel
import numpy as np
from bokeh.palettes import Spectral10,PuOr10,Spectral3,Category10_3
from bokeh.transform import factor_cmap,cumsum
from math import pi


def summary():
    # Read Data
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


    # Current Stock Status
    out_of_stock=data[(data['date']==data['date'].max()) & (data['stock']==0)].count()[0]
    running_out=data[(data['date']==data['date'].max()) & (data['stock']<20) & (data['stock']>0)].count()[0]
    in_stock=data[(data['date']==data['date'].max()) & (data['stock']>=20)].count()[0]

    #Pie Chart
    def graph_current_stock():
        x=['out_of_stock','running_out','in_stock']
        y=[out_of_stock,running_out,in_stock]
        source=ColumnDataSource(dict(x=x,y=y))
        source.data['angle'] = source.data['y']/sum(source.data['y']) * 2*pi
        source.data['color'] = Category10_3[:len(x)]
        p = figure(width=500,height=350, title="Pie Chart", toolbar_location=None,
                tools="hover", tooltips="@x: @y", x_range=(-0.5, 1.0))

        p.wedge(x=0, y=1, radius=0.3,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', legend_field='x', source=source)

        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None
        return p

    # History Overall sold Items
    def graph_overall():
        overall=data.groupby('date').sum()
        overall.index=pd.to_datetime(overall.index)
        source=ColumnDataSource(dict(x=overall.index,y=overall['stock'],z=overall['sold']))
        hover = HoverTool(tooltips=[('date', '@x{%F}'),('Stock','@y'),('Sold','@z')],
                  formatters={'@x': 'datetime'})
        
        p=figure(width=1100,height=350,x_axis_type='datetime',title='History of all Stock/Sold Items',tools=[hover])
        p.line(x='x',y='y',source=source,legend_label='Stock')
        p.line(x='x',y='z',source=source,color='green',legend_label='Sold')
        p.legend.click_policy="hide"
        date_pattern=['%Y-%m-%d']
        p.xaxis.formatter=DatetimeTickFormatter(
                days=date_pattern,
                months=date_pattern,
                years=date_pattern,
            )

        p.xaxis.major_label_orientation=radians(0)
        p.xaxis.axis_label='Date'
        p.yaxis.axis_label='Stock/Sold'
        return p

    # Graph Top 5 Sold Items/category
    def top_sold(item):
        databar=data.groupby(item).sum()['sold']
        databar=databar.sort_values(ascending=False)
        databar=databar.reset_index()
        databar['sold']=pd.to_numeric(databar['sold'])
        databar=ColumnDataSource(data=dict(x=np.array(databar[item][:10]),y=np.array(databar['sold'][:10])))
        category=databar.data['x']
        cyl_cmap = factor_cmap('x', palette=Spectral10*320, factors=data[item].unique())
        p2=figure(width=800,height=350,x_range=category,title='Top 10 Most Sold Items by {}'.format(item),y_axis_label='Sold Items',tools='hover',tooltips=[('{}'.format(item),'@x'),('sold items','@y')])
        p2.vbar(x='x',top='y',source=databar, line_color=cyl_cmap, fill_color=cyl_cmap,width=0.7)
        p2.x_range.range_padding = 0.1
        p2.xaxis.major_label_orientation = 1
        return p2

    def lowest_sold(item):
        databar=data.groupby(item).sum()['sold']
        databar=databar.sort_values(ascending=True)
        databar=databar.reset_index()
        databar['sold']=pd.to_numeric(databar['sold'])
        databar=ColumnDataSource(data=dict(x=np.array(databar[item][:10]),y=np.array(databar['sold'][:10])))
        category=databar.data['x']
        cyl_cmap = factor_cmap('x', palette=Spectral10*320, factors=data[item].unique())
        p2=figure(width=760,height=375,x_range=category,title='10 Lowest Sold Items by {}'.format(item),y_axis_label='Sold Items',tools='hover',tooltips=[('{}'.format(item),'@x'),('sold items','@y')])
        p2.vbar(x='x',top='y',source=databar, line_color=cyl_cmap, fill_color=cyl_cmap,width=0.7)
        p2.x_range.range_padding = 0.1
        p2.xaxis.major_label_orientation = 1
        return p2

    # Mean Difference Data
    meandiff=pd.read_csv('meandiff.csv')
    meandiff=meandiff.drop('Unnamed: 0',axis=1)
    meandiff[['stock_mean','mean_diff']]=round(meandiff[['stock_mean','mean_diff']])

    ## Overstock and Understock Graph
    #Graph
    overstock=meandiff.sort_values(by='mean_diff',ascending=False)[:8]
    understock=meandiff.sort_values(by='mean_diff',ascending=True)[:8]
    understock['mean_diff']=understock['mean_diff']*-1

    def stock_data_table(item,item2):
        if item2=='understock':
            columns = [
                    TableColumn(field="sku", title="SKU"),
                    TableColumn(field="stock", title="Current Stock"),
                    TableColumn(field="mean_diff", title="Restock Recommendation")
                ]
        else:
            columns = [
                    TableColumn(field="sku", title="SKU"),
                    TableColumn(field="stock", title="Current Stock"),
                    TableColumn(field="mean_diff", title="Overstock Quantity")
                ]
        source=ColumnDataSource(item)
        data_table = DataTable(source=source, columns=columns, width=410, height=275)
        return data_table

    #Graph and Div
    data_table1=stock_data_table(understock,'understock')
    data_table2=stock_data_table(overstock,'overstock')
    status=graph_current_stock()
    top_sold_sku=top_sold('sku')
    top_sold_category=top_sold('category')
    lowest_sold_category=lowest_sold('category')
    divunder = Div(text="""<b>8 Most Understock items<b>""", width=400, height=100)
    divover=Div(text="""<b>8 Most Overstock items<b>""", width=400, height=100)
    graph3=graph_overall()
    text="""
        <html>
        <head>
        <style>
        h1 {text-align: center;}
        p {text-align: center;}
        div {text-align: center;}
        </style>
        </head>
        <body>
        <h1>Inventory Stock Summary</h1>
        </body>
        </html>
        """

    #Lay out Config
    lay_out=layout([
        [Div(text=text,width=11000,height=50)],
        [status,graph3],
        [column(divunder,data_table1),column(divover, data_table2),lowest_sold_category],
        [top_sold_sku,top_sold_category],
        ],sizing_mode='fixed')


    # Tab Cofig
    tab1=Panel(child=lay_out,title='Summary')
    return tab1
    # tab2=Panel(child=lay_out2,title="Item's Detail")
    # tabs=Tabs(tabs=[tab1,tab2])
    # curdoc().add_root(tabs)

