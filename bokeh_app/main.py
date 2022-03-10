# Pandas for data management
import pandas as pd

# os methods for manipulating paths
from os.path import dirname, join

# Bokeh basics 
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

# Each tab is drawn by one script
from item import item
from swiftdashboard import summary
from taptool import inv_plot
from tes import inv_plot2

# Create each of the tabs
tab1 = summary()
tab2 = item()
tab3=inv_plot()
tab4=inv_plot2()

# Put all the tabs into one application
tabs = Tabs(tabs = [tab1, tab2,tab3,tab4])

# Put the tabs in the current document for display
curdoc().add_root(tabs)