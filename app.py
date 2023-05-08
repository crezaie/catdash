#!/usr/bin/env python
# coding: utf-8

# In[1]:


import panel as pn
import param
pn.extension('tabulator', sizing_mode="stretch_width")
import hvplot.pandas
import pandas as pd
import holoviews as hv
import calendar
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models import LabelSet
from datetime import datetime, timedelta
from markupsafe import Markup
hv.extension('bokeh')


pd.set_option('display.float_format', str)
pd.options.display.float_format = '{:.1f}'.format

PALETTE = ["#88d8b0", "#b39cd0", "#ffa500", "#1e90ff", "#00CED1"]

# df = pd.read_csv('C:/Users/crezaie/Desktop/ExcelFile/CAT_data_randomized.csv')
# df = pd.read_csv('C:/Users/crezaie/Desktop/ExcelFile/sample424.csv')
# df = pd.read_csv('https://raw.githubusercontent.com/crezaie/pleasework/main/data/sample427.csv')


df = pd.read_csv('https://raw.githubusercontent.com/crezaie/catdash/main/data/sample51.csv')
pmdf = pd.read_csv('https://raw.githubusercontent.com/crezaie/catdash/main/data/PM_Status.csv')

result = df.reset_index(drop=True)

result_dict = {'Response': [8,16,24],
        'Time_to_Complete': [16,24,56],
        'Hours_to_Submit': [16,24,48]}

score_dict = {'Response': [30,20,10],
        'Time_to_Complete': [40,30,10],
        'Hours_to_Submit': [10,5,2]}

score_total = sum([score_dict[key][0] for key in score_dict])


df['Equipment'] = 'All'
union_df = pd.concat([df, result], ignore_index=True)
union_df = union_df.sort_values(by=['Branch', 'InvoiceMonth', 'InvoiceYear','Equipment']).reset_index(drop=True)


# In[2]:


# result['Critical'] = result['Critical'].fillna(0).astype(int).map({0: 'Non-Emergency', 1: 'Emergency'})

result = result.sort_values(by=['Branch', 'InvoiceMonth', 'InvoiceYear']).reset_index(drop=True)

# pd.set_option('display.max_rows', None)


# In[3]:


idf = union_df.interactive()


# In[4]:


# import panel as pn

# style = '<style>table{border-collapse:collapse;width:40%;margin: 0 auto;font-size:20px}th,td{text-align:center;font-weight:bold;font-size:48px}th{background-color:lightgray;height:60px}tr:last-child th{border-top:2px solid black}tr:nth-child(2) td{font-size:28px;font-weight:bold}tr:last-child td{font-size:24px}tr:nth-child(3){border:4px solid #FFD600}td{font-family:Helvetica}tr:first-child th{font-size:24px}tr:last-child th,tr:last-child td{font-size:18px}</style>'

# html = f'<head><meta charset="UTF-8"><title>Morton Monthly PM Progress</title>{style}</head><body><table><tr><td colspan="5"></td></tr><tr><td colspan="5" style="font-size: 28px; font-weight: bold;">Morton Monthly PM Progress</td></tr><tr><td style="background-color: #f2f2f2; height: 60px;">{morton_due}</td><td style="background-color: #f2f2f2; height: 60px;">{morton_complete}</td><td style="background-color: #f2f2f2; height: 60px;">{morton_remaining}</td><td style="background-color: #f2f2f2; height: 60px;">{morton_percent}</td></tr><tr><td style="font-weight: bold;">Due</td><td style="font-weight: bold;">Complete</td><td style="font-weight: bold;">Remain</td><td style="font-weight: bold;">%</td></tr></table></body>'

# html_pane = pn.pane.HTML(html)

# flex_box = pn.FlexBox(html_pane, sizing_mode='stretch_width')

# flex_box




morton_due = pmdf.loc[pmdf['location']=='Morton', 'due'].values[0]
morton_complete = pmdf.loc[pmdf['location']=='Morton', 'complete'].values[0]
morton_remaining = pmdf.loc[pmdf['location']=='Morton', 'remaining'].values[0]
morton_percent = pmdf.loc[pmdf['location']=='Morton', 'percent'].values[0]

mossville_due = pmdf.loc[pmdf['location']=='Mossville', 'due'].values[0]
mossville_complete = pmdf.loc[pmdf['location']=='Mossville', 'complete'].values[0]
mossville_remaining = pmdf.loc[pmdf['location']=='Mossville', 'remaining'].values[0]
mossville_percent = pmdf.loc[pmdf['location']=='Mossville', 'percent'].values[0]

peoria_due = pmdf.loc[pmdf['location']=='East Peoria', 'due'].values[0]
peoria_complete = pmdf.loc[pmdf['location']=='East Peoria', 'complete'].values[0]
peoria_remaining = pmdf.loc[pmdf['location']=='East Peoria', 'remaining'].values[0]
peoria_percent = pmdf.loc[pmdf['location']=='East Peoria', 'percent'].values[0]


Morton_html = pn.pane.HTML(f'<head><meta charset="UTF-8"><title>Morton Monthly PM Progress</title><style>table{{border-collapse:collapse;width:40%;margin: 0 auto;font-size:20px}}th,td{{text-align:center;font-weight:bold;font-size:48px}}th{{background-color:lightgray;height:60px}}tr:last-child th{{border-top:2px solid black}}tr:nth-child(2) td{{font-size:28px;font-weight:bold}}tr:last-child td{{font-size:24px}}tr:nth-child(3){{border:4px solid #FFD600}}td{{font-family:Helvetica}}tr:first-child th{{font-size:24px}}tr:last-child th,tr:last-child td{{font-size:18px}}</style></head><body><table><tr><td colspan="5"></td></tr><tr><td colspan="5" style="font-size: 28px; font-weight: bold;">Morton Monthly PM Progress</td></tr><tr><td style="background-color: #f2f2f2; height: 60px;">{morton_due}</td><td style="background-color: #f2f2f2; height: 60px;">{morton_complete}</td><td style="background-color: #f2f2f2; height: 60px;">{morton_remaining}</td><td style="background-color: #f2f2f2; height: 60px;">{morton_percent}</td></tr><tr><td style="font-weight: bold;">Due</td><td style="font-weight: bold;">Complete</td><td style="font-weight: bold;">Remain</td><td style="font-weight: bold;">%</td></tr></table></body>')
Mossville_html = pn.pane.HTML(f'<head><meta charset="UTF-8"><title>Mossville Monthly PM Progress</title><style>table{{border-collapse:collapse;width:40%;margin: 0 auto;font-size:20px}}th,td{{text-align:center;font-weight:bold;font-size:48px}}th{{background-color:lightgray;height:60px}}tr:last-child th{{border-top:2px solid black}}tr:nth-child(2) td{{font-size:28px;font-weight:bold}}tr:last-child td{{font-size:24px}}tr:nth-child(3){{border:4px solid #FFD600}}td{{font-family:Helvetica}}tr:first-child th{{font-size:24px}}tr:last-child th,tr:last-child td{{font-size:18px}}</style></head><body><table><tr><td colspan="5"></td></tr><tr><td colspan="5" style="font-size: 28px; font-weight: bold;">Mossville Monthly PM Progress</td></tr><tr><td style="background-color: #f2f2f2; height: 60px;">{mossville_due}</td><td style="background-color: #f2f2f2; height: 60px;">{mossville_complete}</td><td style="background-color: #f2f2f2; height: 60px;">{mossville_remaining}</td><td style="background-color: #f2f2f2; height: 60px;">{morton_percent}</td></tr><tr><td style="font-weight: bold;">Due</td><td style="font-weight: bold;">Complete</td><td style="font-weight: bold;">Remain</td><td style="font-weight: bold;">%</td></tr></table></body>')
Peoria_html = pn.pane.HTML(f'<head><meta charset="UTF-8"><title>East Peoria Monthly PM Progress</title><style>table{{border-collapse:collapse;width:40%;margin: 0 auto;font-size:20px}}th,td{{text-align:center;font-weight:bold;font-size:48px}}th{{background-color:lightgray;height:60px}}tr:last-child th{{border-top:2px solid black}}tr:nth-child(2) td{{font-size:28px;font-weight:bold}}tr:last-child td{{font-size:24px}}tr:nth-child(3){{border:4px solid #FFD600}}td{{font-family:Helvetica}}tr:first-child th{{font-size:24px}}tr:last-child th,tr:last-child td{{font-size:18px}}</style></head><body><table><tr><td colspan="5"></td></tr><tr><td colspan="5" style="font-size: 28px; font-weight: bold;">East Peoria Monthly PM Progress</td></tr><tr><td style="background-color: #f2f2f2; height: 60px;">{peoria_due}</td><td style="background-color: #f2f2f2; height: 60px;">{peoria_complete}</td><td style="background-color: #f2f2f2; height: 60px;">{peoria_remaining}</td><td style="background-color: #f2f2f2; height: 60px;">{peoria_percent}</td></tr><tr><td style="font-weight: bold;">Due</td><td style="font-weight: bold;">Complete</td><td style="font-weight: bold;">Remain</td><td style="font-weight: bold;">%</td></tr></table></body>')


# In[13]:


# location_options = {
#     'East Peoria': ['Morton', 'NotMorton'],
#     'Springfield': ['OtherPlace']
# }

br = result['Branch'].unique()
lc = result['Location'].unique()
equ = union_df['Equipment'].unique().tolist()

Equip = pn.widgets.Select(
    name='Equipment', 
    options=equ,
    value='All',
)

location_options = {}
for branch in br:
    location_options[branch] = [Location for Location in lc if result[(result['Branch'] == branch) & (result['Location'] == Location)].shape[0] > 0]

def update_location_options(event):
    location_widget.options = location_options[event.new]
    location_widget.value = location_options[event.new][0] # set default value
    
branch_values = df['Branch'].unique().tolist()

Branches = pn.widgets.Select(
    name='Branch', 
    options=branch_values,
    value='East Peoria',
)

location_widget = pn.widgets.Select(
    name='Location', 
    options=location_options[branch_values[0]], 
    value=location_options[branch_values[0]][0],
)


Branches.param.watch(update_location_options, 'value')

widget_panel = pn.Column(Branches, location_widget, Equip)

month_values = result['InvoiceMonth'].unique().tolist()
month_dict = {month_name: i+1 for i, month_name in enumerate(calendar.month_name[1:])}
sorted_months = sorted(month_values, key=lambda x: month_dict[x])

Month = pn.widgets.Select(
    name='Month', 
    options=sorted_months,
    value=sorted_months[-1], # sets default value to the highest available month
)

year_values = result['InvoiceYear'].unique().tolist()
Year = pn.widgets.Select(
    name='Year', 
    options=year_values,
    value=year_values[-1], # sets default value to the highest available year
)


# update_content = Morton_html

# @pn.depends(location_widget.param.value)
# def update_content(location):
#     if location == 'Morton':
#         return Morton_html
#     elif location == 'Mossville':
#         return Mossville_html
#     elif location == 'Peoria':
#         return Peoria_html



# @pn.depends(location_widget.param.value)
def get_location_html(location):
    if location == 'East Peoria':
        return Peoria_html
    elif location == 'Morton':
        return Morton_html
    elif location == 'Mossville':
        return Mossville_html
    else:
        return None
    
pn.state.location_html = get_location_html

# @pn.depends(location_widget.param.value)
# def update_location_html(location):
#     location_html = pn.state.location_html(location)
#     if location_html is None:
#         return None
#     else:
#         return location_html
    
@pn.depends(location_widget.param.value, Month.param.value)
def update_location_html(location, month):
    if month != sorted_months[-1]:  # if the current month selection is not the highest available month
        return None
    location_html = pn.state.location_html(location)
    if location_html is None:
        return None
    else:
        return location_html
# Create a Pane for the updated HTML
location_pane = pn.Row(update_location_html)




def get_equipment_options(branch, location, year, month):
    options = union_df.loc[
        (union_df['Branch'] == branch) & 
        (union_df['Location'] == location) & 
        (union_df['InvoiceYear'] == year) &
        (union_df['InvoiceMonth'] == month), 
        'Equipment'
    ].unique().tolist()
    if 'All' in options:
        options.remove('All')
    options.insert(0, 'All')
    return options

def update_options(event):
    equip_options = get_equipment_options(
        Branches.value, 
        location_widget.value, 
        Year.value, 
        Month.value
    )
    Equip.options = equip_options
    Equip.value = equip_options[0] # set default value

Branches.param.watch(update_options, 'value')
location_widget.param.watch(update_options, 'value')
Year.param.watch(update_options, 'value')
Month.param.watch(update_options, 'value')


# In[ ]:





# In[14]:


# # idf[idf.Location=='NotMorton']['WorkOrder']


# # br = result['Branch'].unique()
# # lc = result['Location'].unique()
# # location_options = {}
# # for branch in br:
# #     location_options[branch] = [Location for Location in lc if result[(result['Branch'] == branch) & (result['Location'] == Location)].shape[0] > 0]

# # Branches.param.watch(update_location_options, 'value')

# agg_df = df[df['Critical'] == 1].groupby('Location').size().reset_index(name='Count')
# all_locs_df = pd.DataFrame({'Location': df['Location'].unique()})
# result_df = all_locs_df.merge(agg_df, on='Location', how='left').fillna({'Count': 0})
# result_df

iresponse = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.Branch == Branches) &
        (idf.InvoiceYear == Year) &
        (idf.Location == location_widget) &
        # (~idf.ServiceType.str.contains('PM')) &
        (idf.Equipment == Equip)
        # (idf['Critical'] == 'Non-Emergency')
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location','Equipment'])  
    .agg(Avg_Response_Time2=('Response_Ratio', 'sum'), Total_Work_Orders=('Total_Work_Orders','sum'))
    .assign(Avg_Response_Time=lambda x: (x['Avg_Response_Time2'] / x['Total_Work_Orders']))
    .reset_index()
    .round({'Avg_Response_Time': 1})
    .reset_index(drop=True) 
    .drop(columns=['Avg_Response_Time2'])
)

# ieresponse = (
#     idf[
#         (idf.InvoiceMonth == Month) &
#         (idf.Branch == Branches) &
#         (idf.InvoiceYear == Year) &
#         (idf.Location == location_widget) &
#         (~idf.ServiceType.str.contains('PM')) &
#         (idf.Equipment == Equip)
#         # (idf['Critical'] == 'Emergency')
#     ]
#     .groupby(['InvoiceYear','InvoiceMonth','Branch','Location','Equipment'])  
#     .agg(Avg_Response_Time=('Response', 'mean'), Total_Work_Orders=('Total_Work_Orders','sum'))
#     .reset_index()
#     .round({'Avg_Response_Time': 1})
#     .reset_index(drop=True) 
# )

icomplete = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.Branch == Branches) &
        (idf.InvoiceYear == Year) &
        (idf.Location == location_widget) &
        (idf.Equipment == Equip)
        # (~idf.ServiceType.str.contains('PM'))
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location','Equipment'])
    .agg(Avg_Complete_Time2=('Complete_Ratio', 'sum'), Total_Work_Orders=('Total_Work_Orders','sum')) 
    .assign(Avg_Complete_Time=lambda x: (x['Avg_Complete_Time2'] / x['Total_Work_Orders']))
    .reset_index()
    .round({'Avg_Complete_Time': 1})
    .reset_index(drop=True)   
    .drop(columns=['Avg_Complete_Time2'])
)

iinvoice = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.Branch == Branches) &
        (idf.InvoiceYear == Year) &
        (idf.Location == location_widget) &
        (idf.Equipment == Equip)
        # (~idf.ServiceType.str.contains('PM'))
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location','Equipment'])
    .agg(Avg_Invoice_Time2=('Submit_Ratio', 'sum'), Total_Work_Orders=('Total_Work_Orders','sum'))   
    .assign(Avg_Invoice_Time=lambda x: (x['Avg_Invoice_Time2'] / x['Total_Work_Orders']))
    .reset_index()
    .round({'Avg_Invoice_Time': 1})
    .reset_index(drop=True)    
    .drop(columns=['Avg_Invoice_Time2'])
)


ioverall = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.InvoiceYear == Year) &        
        (idf.Location == location_widget) &
        (idf.Branch == Branches) &
        (idf.Equipment == Equip)
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location','Equipment'])
    .agg(
        Avg_Response_Time2=('Response_Ratio', 'sum'),
        Avg_Complete_Time2=('Complete_Ratio', 'sum'),
        Avg_Invoice_Time2=('Submit_Ratio', 'sum'),
        Total_Work_Orders=('Total_Work_Orders','sum')
    )
    .reset_index()
    .assign(Avg_Complete_Time=lambda x: (x['Avg_Complete_Time2'] / x['Total_Work_Orders']))
    .assign(Avg_Invoice_Time=lambda x: (x['Avg_Invoice_Time2'] / x['Total_Work_Orders']))
    .assign(Avg_Response_Time=lambda x: (x['Avg_Response_Time2'] / x['Total_Work_Orders']))
    .assign(Response_Score=lambda x: np.select(
            [
                (x['Avg_Response_Time'] <= result_dict['Response'][0]),
                (x['Avg_Response_Time'] <= result_dict['Response'][1]),
                (x['Avg_Response_Time'] <= result_dict['Response'][2])
            ],
            [
                score_dict['Response'][0],
                score_dict['Response'][1],
                score_dict['Response'][2]
            ],
            default=0))
            
    .assign(Complete_Score=lambda x: np.select(
            [
                (x['Avg_Complete_Time'] <= result_dict['Time_to_Complete'][0]),
                (x['Avg_Complete_Time'] <= result_dict['Time_to_Complete'][1]), 
                (x['Avg_Complete_Time'] <= result_dict['Time_to_Complete'][2]) 
            ],
            [
                score_dict['Time_to_Complete'][0],
                score_dict['Time_to_Complete'][1],
                score_dict['Time_to_Complete'][2]
            ],
            default=0))            

     .assign(Invoice_Score=lambda x: np.select(
            [
                (x['Avg_Invoice_Time'] <= result_dict['Hours_to_Submit'][0]),
                (x['Avg_Invoice_Time'] <= result_dict['Hours_to_Submit'][1]), 
                (x['Avg_Invoice_Time'] <= result_dict['Hours_to_Submit'][2]) 
            ],
            [
                score_dict['Hours_to_Submit'][0],
                score_dict['Hours_to_Submit'][1],
                score_dict['Hours_to_Submit'][2]
            ],
            default=0))
    .assign(Compliance=lambda x: (x['Invoice_Score'] + x['Complete_Score'] + x['Response_Score']))
    .sort_values(by=['Branch', 'Location'])
    .reset_index(drop=True) 
    .drop(columns=['Avg_Response_Time','Avg_Complete_Time','Avg_Invoice_Time','Invoice_Score','Complete_Score','Response_Score', 'Avg_Complete_Time2', 'Avg_Invoice_Time2', 'Avg_Response_Time2'])
    # .assign(Counter=lambda x: x['Critical'].apply(lambda y: -2 if y == 'Emergency' else 2))
)


# ioverall2 = (
#     ioverall[
#             (ioverall.InvoiceMonth == Month) &
#             (ioverall.InvoiceYear == Year) &        
#             (ioverall.Location == location_widget) &
#             (ioverall.Branch == Branches) &
#             (ioverall.Equipment == Equip)
#     ]
#     .groupby(['InvoiceYear','InvoiceMonth','Branch','Location','Equipment'])
#     .agg(
#         Response_Score2=('Response_Score', 'sum'),
#         compAg2=('compAg', 'sum'),
#         invAg2=('invAg', 'sum'),
#         Total_Work_Orders=('Total_Work_Orders','sum'),
#         Counter=('Counter','sum')
#     )
    
#     .reset_index()
#     .assign(Counter=lambda x: x['Counter'].fillna(0).replace(0,1)) 
#     .assign(Complete_Score=lambda x: np.select(
#             [
#                 (x['compAg2']/x['Total_Work_Orders'] <= result_dict['Time_to_Complete'][0]),
#                 (x['compAg2']/x['Total_Work_Orders'] <= result_dict['Time_to_Complete'][1]), 
#                 (x['compAg2']/x['Total_Work_Orders'] <= result_dict['Time_to_Complete'][2]) 
#             ],
#             [
#                 score_dict['Time_to_Complete'][0],
#                 score_dict['Time_to_Complete'][1],
#                 score_dict['Time_to_Complete'][2]
#             ],
#             default=0
#         )
#     )
 
#     .assign(Invoice_Score=lambda x: np.select(
#             [
#                 (x['invAg2']/x['Total_Work_Orders'] <= result_dict['Hours_to_Submit'][0]),
#                 (x['invAg2']/x['Total_Work_Orders'] <= result_dict['Hours_to_Submit'][1]), 
#                 (x['invAg2']/x['Total_Work_Orders'] <= result_dict['Hours_to_Submit'][2]) 
#             ],
#             [
#                 score_dict['Hours_to_Submit'][0],
#                 score_dict['Hours_to_Submit'][1],
#                 score_dict['Hours_to_Submit'][2]
#             ],
#             default=0
#         )
#     )    
#     .assign(Response_Score2=lambda x: (x['Response_Score2'] * x['Counter']))
#     .assign(Compliance=lambda x: (x['Invoice_Score'] + x['Complete_Score'] + x['Response_Score2']))
#     .reset_index(drop=True)
#     .drop(columns=['compAg2','invAg2','Response_Score2','Invoice_Score','Complete_Score','Counter'])
# )


# ioverall2
            


# In[16]:


# def row_color(row):
#     if row.getData()['Compliance'] < 70:
#         return {'css': {'background-color': 'lightcoral'}}
#     else:
#         return {}

tabulator_settings = {
    'show_index': False,
    'hidden_columns': ['InvoiceYear', 'InvoiceMonth', 'Branch', 'Critical'],
    'layout': 'fit_columns',
    'configuration': {'columnDefaults': {'headerSort': False}},
    'header_align': 'center',
    'text_align': 'center'
}

iresponse = iresponse.rename(columns={'Avg_Response_Time': 'Avg Hours to Respond', 'Total_Work_Orders': 'Total Work Orders'})
# ieresponse = ieresponse.rename(columns={'Location': 'Location ', 'Avg_Response_Time': 'Avg Hours to Respond', 'Total_Work_Orders': 'Total Work Orders'})
icomplete = icomplete.rename(columns={'Location': 'Location  ', 'Total_Work_Orders': 'Total Work Orders', 'Avg_Complete_Time': 'Avg Hours to Complete'})
ioverall2 = ioverall.rename(columns={'Location': 'Location   ', 'Total_Work_Orders': 'Total Work Orders', 'Compliance': 'Total Score out of 80'})
# ipm = ipm.rename(columns={'Location': 'Location_p'})
iinvoice = iinvoice.rename(columns={'Location': 'Location    ', 'Total_Work_Orders': 'Total Work Orders', 'Avg_Invoice_Time': 'Avg Hours to Invoice'})

itable1 = iresponse.pipe(pn.widgets.Tabulator, **tabulator_settings)
itable2 = icomplete.pipe(pn.widgets.Tabulator, **tabulator_settings)
itable3 = iinvoice.pipe(pn.widgets.Tabulator, **tabulator_settings)
# itable4 = ipm.pipe(pn.widgets.Tabulator, **tabulator_settings)
itable5 = ioverall2.pipe(pn.widgets.Tabulator, **tabulator_settings)

# itable6 = ieresponse.pipe(pn.widgets.Tabulator, **tabulator_settings)



# In[17]:


# ["#88d8b0", "#b39cd0", "#ffa500", "#1e90ff", "#00CED1"]

# top0 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black; font-family: Helvetica, Arial, sans-serif;">Hours to Respond (Emergency)</div>')
top1 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black; font-family: Helvetica, Arial, sans-serif;">Hours to Respond</div>')
top2 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black; font-family: Helvetica, Arial, sans-serif;">Hours to Complete</div>')
top3 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black; font-family: Helvetica, Arial, sans-serif;">Hours to Invoice</div>')
# top4 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black;">PM Completion</div>')
top5 = pn.pane.HTML('<div style="text-align: center; font-size: 64px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black; font-family: Helvetica, Arial, sans-serif;">Overall Score</div>')


bottom0 = pn.pane.HTML('<div style="text-align: center; font-size: 20px; font-weight: bold; color: black; background-color: #D9D9D9; border: 3px solid black; font-family: Helvetica, Arial, sans-serif;">Hours between initial service request and arrival by Wiese technician</div>')
bottom2 = pn.pane.HTML('<div style="text-align: center; font-size: 20px; font-weight: bold; color: black; background-color: #D9D9D9; border: 3px solid black; font-family: Helvetica, Arial, sans-serif;">Hours between initial service request and when Wiese has repaired/returned the unit to service</div>')
bottom3 = pn.pane.HTML('<div style="text-align: center; font-size: 20px; font-weight: bold; color: black; background-color: #D9D9D9; border: 3px solid black; font-family: Helvetica, Arial, sans-serif;">Hours between work order completion and invoice submittal</div>')


# In[18]:


line_break = pn.pane.HTML('<br>')
font_pane = pn.pane.HTML("<span style=font-size: 24px>")
span = pn.pane.HTML("</span>")
spacer = pn.layout.Spacer(width=20)

responsetarget = result_dict['Response'][0]
# eresponsetarget = responsetarget/2
completetarget = result_dict['Time_to_Complete'][0]
invoicetarget = result_dict['Hours_to_Submit'][0]
# pmtarget = result_dict['PM_Completion'][1]
overalltarget = 80

ihvplot = iresponse.hvplot.bar(
        # x='Location_r',
        x='Location', 
        y='Avg Hours to Respond', 
        # by='Equipment',
        color=PALETTE[4], 
        bar_width=.3, 
        line_width=3, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,responsetarget+3),
        dynamic=True,
    ).opts(xlabel="",ylabel="Hours to Respond",active_tools=['box_zoom'])

# iehvplot = ieresponse.hvplot.bar(
#         # x='Location_er', 
#         x='Location ', 
#         y='Avg Hours to Respond', 
#         by='Equipment',
#         color=PALETTE[3], 
#         bar_width=.3, 
#         line_width=3, 
#         yformatter='%.2f', 
#         use_index=True,
#         ylim=(0,eresponsetarget+3),
#         dynamic=True,
#     ).opts(xlabel="",ylabel="Hours to Respond",active_tools=['box_zoom'])

ihvplot2 = icomplete.hvplot.bar(
        # x='Location_c', 
        x='Location  ',
        y='Avg Hours to Complete', 
        # by='Equipment',
        color=PALETTE[1],
        bar_width=.3, 
        line_width=3, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,20),
        dynamic=True
    ).opts(xlabel="",ylabel="Hours to Complete",active_tools=['box_zoom'])

ihvplot3 = iinvoice.hvplot.bar(
        # x='Location_i', 
        x='Location    ',
        y='Avg Hours to Invoice', 
        # by='Equipment',
        color=PALETTE[2], 
        bar_width=.3, 
        line_width=3, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,18),
        dynamic=True
    ).opts(xlabel="",ylabel="Hours to Invoice",active_tools=['box_zoom'])

ihvplot5 = ioverall2.hvplot.bar(
        # x='Location_o',
        x='Location   ',
        y='Total Score out of 80', 
        # by='Equipment',
        color=PALETTE[0], 
        bar_width=.3, 
        line_width=3, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,110),
        dynamic=True,
    ).opts(xlabel="",ylabel="Overall Performance",active_tools=['box_zoom'])

# target_line0 = hv.HLine(eresponsetarget).opts(line_dash='dotted', color='red') #* hv.Text("",responsetarget+1,"Target")
# iehvplot = iehvplot * target_line0

target_line = hv.HLine(responsetarget).opts(line_dash='dotted', color='red') #* hv.Text("",responsetarget+1,"Target")
ihvplot = ihvplot * target_line

target_line1 = hv.HLine(completetarget).opts(line_dash='dotted', color='red')
ihvplot2 = ihvplot2 * target_line1

target_line2 = hv.HLine(invoicetarget).opts(line_dash='dotted', color='red')
ihvplot3 = ihvplot3 * target_line2

# target_line3 = hv.HLine(pmtarget).opts(line_dash='dotted', color='red')
# ihvplot4 = ihvplot4 * target_line3

target_line4 = hv.HLine(overalltarget).opts(line_dash='dotted', color='red')
ihvplot5 = ihvplot5 * target_line4
main= pn.FlexBox(*[
    pn.Column(
       
        pn.Row(
            pn.Card(pn.Column(top5,itable5.panel(),ihvplot5.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
        ),
        
        pn.Row(
            pn.Card(pn.Column(top1,bottom0,itable1.panel(),ihvplot.panel(),),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
            # pn.Card(pn.Column(top0,bottom0,itable6.panel(),iehvplot.panel(),),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
            #background='black'
        ),
  
        # pn.Row(
        #     pn.Card(pn.Column(top0,itable6.panel(),iehvplot.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
        #     #background='black'
        # ),        
 
        pn.Row(
            pn.Card(pn.Column(top2,bottom2,itable2.panel(),ihvplot2.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
            #background='black'
        ),        
        
        pn.Row(
            pn.Card(pn.Column(top3,bottom3,itable3.panel(),ihvplot3.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
            #background='black'
        ),
        
        # pn.Row(
        #     pn.Card(pn.Column(top4,itable4.panel(),ihvplot4.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
        #     #background='black'
        # )
        
        
        line_break,
        location_pane,
        line_break,
        line_break,
        line_break,            
    )       
], align_content='space-evenly', justify_content="space-evenly")


# In[19]:


template = pn.template.FastListTemplate(
    title='Wiese Report Card', 
    site='<a class="navbar-brand app-logo" href="/"><img src="https://wieseusa.com/img/logo-Wiese2.png" class="app-logo"></a>',
    site_url="https://www.wieseusa.com",
    sidebar=[Year,Month,widget_panel],
    main=[main],
    accent_base_color="#FFD600",
    header_background="#FFFFFF",
    main_max_width='90%',
    sidebar_width=250,
    logo='https://s7d2.scene7.com/is/image/Caterpillar/CM20220222-5c3c2-280a8?fmt=png-alpha',
    header_color="#FFFFFF",
    header_accent_base_color='#FFD600',
    background_color ="#f2f2f2",
    favicon = "https://wieseusa.com/img/logo-Wiese2.png",
    theme_toggle = False
)





pn.panel(template).servable(title='test')


