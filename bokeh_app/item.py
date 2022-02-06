from turtle import window_width
import requests
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource,DatetimeTickFormatter,Select,FactorRange,DataTable,TableColumn,Div, HoverTool,DateFormatter
from bokeh.layouts import layout
from bokeh.plotting import figure,show
from datetime import datetime
from math import radians # Rotate axis ticks
import numpy as np
import finnhub
from bokeh.layouts import gridplot,row,column
import pandas as pd
from bokeh.models.widgets import Tabs, Panel
import numpy as np
from bokeh.palettes import Spectral10,PuOr10,Spectral3,Category10_3,Spectral5
from bokeh.transform import factor_cmap,cumsum
from math import pi


def item():
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

    def graph(item):
        #Get Data
        def get_data(item):
            a=data[data['sku']==item]
            return a

        #Graph History
        source=ColumnDataSource(dict(x=get_data(item)['date'],y=get_data(item)['stock'],z=get_data(item)['sold']))
        hover = HoverTool(tooltips=[('date', '@x{%F}'),('Stock','@y'),('Sold','@z')],
                  formatters={'@x': 'datetime'})
        
        p=figure(width=1300,height=425,x_range=(data['date'].min(),data['date'].max()),title='Stock and Sold History',tools='tap,pan,box_zoom,wheel_zoom,box_select')
        p.line(x='x',y='y',source=source,legend_label='Stock')
        p.line(x='x',y='z',source=source,color='green',legend_label='Sold')
        p.circle(source=source, x="x", y="y", size=2, color="navy", alpha=0.5)
        p.circle(source=source, x="x", y="z", size=2, color="red", alpha=0.5)
        p.add_tools(hover)
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

        # Data Table History
        datefmt = DateFormatter(format="%Y-%m-%d")
        columns2 = [
                    TableColumn(field="x", title="Date",formatter=datefmt),
                    TableColumn(field="y", title="Stock"),
                    TableColumn(field="z", title="Sold")
                ]
        data_table_history = DataTable(source=source, columns=columns2, width=300, height=350)
        div_data_table_history=Div(text='<b>{} Item Stock and Sold History<b>'.format(item))

        # Current Stock ,total Sold items,status and category
        out_of_stock_item=data[(data['date']==data['date'].max()) & (data['stock']==0)]
        running_out_item=data[(data['date']==data['date'].max()) & (data['stock']<20) & (data['stock']>0)]
        in_stock_item=data[(data['date']==data['date'].max()) & (data['stock']>=20)]
        list_status=[out_of_stock_item,running_out_item,in_stock_item]
        status=''
        if np.isin(item,out_of_stock_item['sku']):
            status='Out of Stock'
        elif np.isin(item,running_out_item['sku']):
            status='Running Out'
        elif np.isin(item,in_stock_item['sku']):
            status='In Stock'

        current_stock=data[data['date']==data['date'].max()].iloc[0][3]
        total_sold=int(data[data['sku']==item]['sold'].sum())
        category=data[data['sku']=='sku_955']['category'].iloc[1]
        Text1='''<b><h2>SKU = {}    .'''.format(item)
        Text2='''<b><h2>Current Stock = {} <b><h2>'''.format(int(current_stock))
        Text3='''<h2><b>Total Sold = {} <h2><b>'''.format(total_sold)
        Text4='''<h2><b>Category:{}<h2><b>'''.format(category)
        Text5='''<h2><b>Stock Status = {} <h2><b>'''.format(status)
        
        div1=Div(text=Text1,style={
            'padding-left': '5px','padding-right': '5px','font-size':'10px',
            'font-family':'courier','color':'black','text-align':'left','background-color':'powderblue',
            'border':'5px solid black'},max_width=500,max_height=200,min_width=200,min_height=60,height_policy='fit',width_policy='fixed')
        
        div2=Div(text=Text2,style={
            'padding-left': '5px','padding-right': '5px','font-size':'10px',
            'font-family':'courier','color':'black','text-align':'left','background-color':'powderblue',
            'border':'5px solid black'},max_width=500,max_height=200,min_width=200,min_height=60,height_policy='fit',width_policy='fit')
        
        div3=Div(text=Text3,style={
            'padding-left': '5px','padding-right': '5px','font-size':'10px',
            'font-family':'courier','color':'black','text-align':'left','background-color':'powderblue',
            'border':'5px solid black'},max_width=500,max_height=200,min_width=200,min_height=60,height_policy='fit',width_policy='fit')
        
        div4=Div(text=Text4,style={
            'padding-left': '5px','padding-right': '5px','font-size':'10px',
            'font-family':'courier','color':'black','text-align':'left','background-color':'powderblue',
            'border':'5px solid black'},width=400,height=80,height_policy='fixed',width_policy='fixed')
        
        div5=Div(text=Text5,style={
            'padding-left': '5px','padding-right': '5px','font-size':'10px',
            'font-family':'courier','color':'black','text-align':'left','background-color':'powderblue',
            'border':'5px solid black'},max_width=500,max_height=200,min_width=300,min_height=60,height_policy='fit',width_policy='fit')
        
        #Data Table Sold Item in category sort by most sold
        columns = [
                    TableColumn(field="sku", title="SKU"),
                    TableColumn(field="sold", title="Total Item Sold")
                ]
        source2=ColumnDataSource(data[data['category']==category].groupby('sku').sum()['sold'].sort_values(ascending=False).reset_index())
        data_table = DataTable(source=source2, columns=columns, width=300, height=350)
        div_data_table=Div(text='<b>{} Category Items Sold<b>'.format(category))

        #Graph Performance top 5 lowest and most sold item in category
        line_data1=data[data['category']==category].groupby('sku').sum()['sold'].sort_values(ascending=False).reset_index()['sku'][:10]
        line_data2=data[data['category']==category].groupby('sku').sum()['sold'].sort_values(ascending=True).reset_index()['sku'][:10]
        
        #Graph top 5
        value=[]
        for item_1 in line_data1:
            value.append(data[data['sku']==item_1]['sold'].sum())
        databar=ColumnDataSource(data=dict(x=line_data1,y=value))
        category_data=databar.data['x']
        cyl_cmap = factor_cmap('x', palette=Spectral10*320, factors=data['sku'].unique())
        p2=figure(width=650,height=450,x_range=category_data,title='Top 10 Most Sold Items in category',y_axis_label='Sold Items',tools='hover',tooltips=[('{}'.format('category'),'@x'),('sold items','@y')])
        p2.vbar(x='x',top='y',source=databar, line_color='white', fill_color=cyl_cmap,width=0.7)
        p2.x_range.range_padding = 0.1
        p2.xaxis.major_label_orientation = 1
        
        #Graph Lowest 5
        value2=[]
        for item_2 in line_data2:
            value2.append(data[data['sku']==item_2]['sold'].sum())
        databar2=ColumnDataSource(data=dict(x=line_data2,y=value2))
        category_data2=databar2.data['x']
        p3=figure(width=650,height=450,x_range=category_data2,title='10 Lowest Sold Items in category',y_axis_label='Sold Items',tools='hover',tooltips=[('{}'.format('category'),'@x'),('sold items','@y')])
        p3.vbar(x='x',top='y',source=databar2, line_color='white', fill_color=cyl_cmap,width=0.7)
        p3.x_range.range_padding = 0.1
        p3.xaxis.major_label_orientation = 1

        #Update Value from Dropdown
        def update():
            new_data=dict(x=get_data(select.value)['date'],y=get_data(select.value)['stock'],z=get_data(select.value)['sold'])
            new_current_stock=data[(data['date']==data['date'].max()) & (data['sku']==select.value)].iloc[0][3]
            new_total_sold=int(data[data['sku']==select.value]['sold'].sum())
            new_category=data[data['sku']==select.value]['category'].iloc[1]
            new_status=''
            if np.isin(select.value,out_of_stock_item['sku']):
                new_status='out of Stock'
            elif np.isin(select.value,running_out_item['sku']):
                new_status='Running Out'
            elif np.isin(select.value,in_stock_item['sku']):
                new_status='In Stock'
            div1.text='''<b><h2>SKU = {}   <h2><b>'''.format(select.value)
            div2.text='''<b><h2>Current Stock = {} <b><h2>'''.format(int(new_current_stock))
            div3.text='''<h2><b>Total Sold = {} <h2><b>'''.format(new_total_sold)
            div4.text='''<h2><b>Category:{}<h2><b>'''.format(new_category)
            div5.text='''<h2><b>Stock Status = {} <h2><b>'''.format(new_status)
            
            div_data_table_history.text='<b>{} Item Stock and Sold History<b>'.format(select.value)
            div_data_table.text='<b>{} Item Sold<b>'.format(new_category)
            new_data2=data[data['category']==new_category].groupby('sku').sum()['sold'].sort_values(ascending=False).reset_index()
            source.data=new_data
            source2.data=new_data2
            p.title='{} Stock and Sold History'.format(select.value)

            new_line_data1=data[data['category']==new_category].groupby('sku').sum()['sold'].sort_values(ascending=False).reset_index()['sku'][:10]
            new_line_data2=data[data['category']==new_category].groupby('sku').sum()['sold'].sort_values(ascending=True).reset_index()['sku'][:10]
            new_value1=[]
            for item_1 in new_line_data1:
                new_value1.append(data[data['sku']==item_1]['sold'].sum())
            databar.data=dict(x=new_line_data1,y=new_value1)
            p2.x_range.factors=databar.data['x'].to_list()
            new_value2=[]
            for item_2 in new_line_data2:
                new_value2.append(data[data['sku']==item_2]['sold'].sum())
            databar2.data=dict(x=new_line_data2,y=new_value2)
            p3.x_range.factors=databar2.data['x'].to_list()
            
        options=listproduct
        select=Select(title='Please Select SKU',value=item,options=options,width=250)
        select.on_change('value',lambda attr, old, new: update())
        return select,p,data_table,div_data_table,div1,div2,div3,div4,div5,p2,p3,data_table_history,div_data_table_history

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
        <h1>Item & Category Summary</h1>
        </body>
        </html>
        """
        
    #Layout Config
    graph=graph('sku_955')
    lay_out2=layout([
        [Div(text=text_title,width=11000)],
        [graph[0]],
        [row(graph[7],graph[5],graph[6],graph[8],sizing_mode='stretch_width')],
        [graph[1],column(graph[12],graph[11])],
        [graph[9],graph[10],column(graph[3],graph[2])]
    ]
    ,sizing_mode='fixed')
    tab2=Panel(child=lay_out2,title="Item & Category Detail")
    return tab2