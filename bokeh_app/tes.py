from google.cloud import bigquery
from google.cloud.exceptions import NotFound
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


project_id = 'swift-solutions'

def run_query(sql):
    return query_parameterized(sql, {})

def query_parameterized(sql, params, client = None, project = project_id):
    import time
    print("Setting up")
    start = time.time()
    if client is None:
        client = bigquery.Client(project = project)

    config = []
    for item in params.items():
        config.append(bigquery.ScalarQueryParameter(item[0], *item[1]),)

    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = config
    job_config.use_legacy_sql = False
    
    print("Starting to query")
    sql_result = client.query(sql, job_config = job_config)
    print("Querying is finished. Converting the result to DataFrame..")
    df = sql_result.to_dataframe()
    print("The time taken is {} seconds\n".format(time.time() - start))
    return df

sql='''select * from derived.ddi_daily_sales_and_inventory a
left join (select * from ibp.denny_category) b
on a.sku_variant = cast(b.product_id as string)'''
df=run_query(sql)
print(df)
df=df[['dates','sku','category','qty','daily_sales']]
df=df.dropna()
df['dates']=pd.to_datetime(df['dates'])

def inv_plot2():
    def graph_overall():
        overall=df.groupby('dates').sum()
        overall.index=pd.to_datetime(overall.index)
        source=ColumnDataSource(dict(x=overall.index,y=overall['qty'],z=overall['daily_sales']))
        hover = HoverTool(tooltips=[('dates', '@x{%F}'),('Stock','@y'),('Sold','@z')],
                  formatters={'@x': 'datetime'})
        
        p=figure(width=1500,height=350,x_axis_type='datetime',title='History of all Stock/Sold Items',tools=[hover])
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


    def top_sold(item):
        databar=df.groupby(item).sum()['daily_sales']
        databar=databar.sort_values(ascending=False)
        databar=databar.reset_index()
        databar['daily_sales']=pd.to_numeric(databar['daily_sales'])
        databar=ColumnDataSource(data=dict(x=np.array(databar[item][:10]),y=np.array(databar['daily_sales'][:10])))
        category=databar.data['x']
        cyl_cmap = factor_cmap('x', palette=Spectral10*320, factors=df[item].unique())

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
                    TableColumn(field="dates", title="DATE",formatter=datefmt),
                    TableColumn(field="sku", title="SKU"),
                    TableColumn(field="category", title="Category"),
                    TableColumn(field="qty", title="Stock"),
                    TableColumn(field="daily_sales", title="Sold")
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
            line_data1=df[df['category']==databar.data['x'][new[0]]].groupby('sku').sum()['daily_sales'].sort_values(ascending=False).reset_index()['sku'][:10]
            line_data2=df[df['category']==databar.data['x'][new[0]]].groupby('sku').sum()['daily_sales'].sort_values(ascending=True).reset_index()['sku'][:10]
            value=[]
            print(new[0])
            for item_1 in line_data1:
                value.append(df[df['sku']==item_1]['daily_sales'].sum())
            databar2=ColumnDataSource(data=dict(x=line_data1,y=value))
            category_data=databar2.data['x'].to_list()
            print(databar2.data['x'].to_list())
            cyl_cmap = factor_cmap('x', palette=Spectral10*320, factors=df['sku'].unique())
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
                source.data=df[df['sku']==databar2.data['x'][new[0]]]
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
        [graph_overall()],
        [top_sold_sku[0],top_sold_sku[1]],
        [top_sold_sku[2]]
        ],sizing_mode='fixed')


        # Tab Cofig
    tab1=Panel(child=lay_out,title='Data From Brian')
    return tab1
