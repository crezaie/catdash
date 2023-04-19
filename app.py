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
pd.options.display.float_format = '{:.3f}'.format

PALETTE = ["#88d8b0", "#b39cd0", "#ffa500", "#1e90ff", "#00CED1"]

df = pd.read_csv('https://raw.githubusercontent.com/crezaie/catdash/main/data/CAT_data_randomized.csv')
# df = pd.read_csv('C:/Users/crezaie/Desktop/ExcelFile/sample417.csv')
result = df.reset_index(drop=True)

result_dict = {'Response': [1, 25],
        'Time_to_Complete': [12, 40],
        'PM_Completion': [90, 10],
        'Days_to_Submit': [15, 10]}



result['response_score'] = result.apply(lambda row: result_dict['Response'][1] if row['Response'] <= result_dict['Response'][0] and row['Response'] != 0 else 0, axis=1)

result['response_max'] = 0

result.loc[~result['ServiceType'].str.contains('PM'), 'response_max'] = result_dict['Response'][1]


result['complete_score'] = result.apply(lambda row: result_dict['Time_to_Complete'][1] if row['Time_to_Complete'] <= result_dict['Time_to_Complete'][0] and row['Time_to_Complete'] != 0 else 0, axis=1)

result['complete_max'] = 0

result.loc[~result['ServiceType'].str.contains('PM'), 'complete_max'] = result_dict['Time_to_Complete'][1]

result['invoice_score'] = result.apply(lambda row: result_dict['Days_to_Submit'][1] if row['Days_to_Submit'] <= result_dict['Days_to_Submit'][0] and row['Days_to_Submit'] != 0 else 0, axis=1)

result['invoice_max'] = 0

result.loc[~result['ServiceType'].str.contains('PM'), 'invoice_max'] = result_dict['Days_to_Submit'][1]


result['score_max'] = result.apply(lambda row: row['response_max'] + row['complete_max'] + row['invoice_max'] if 'PM' not in row['ServiceType'] else 10, axis=1)


result['PM_Score'] = 0

result.loc[result['ServiceType'] == 'PM', 'PM_Score'] = result_dict['PM_Completion'][1]

result['Score'] = round(result[['response_score', 'complete_score', 'invoice_score']].sum(axis=1),2)

result = result.sort_values(by=['Branch', 'InvoiceMonth', 'InvoiceYear']).reset_index(drop=True)

pd.set_option('display.max_rows', None)


idf = result.interactive()


branch_values = df['Branch'].unique().tolist()
Branches = pn.widgets.Select(
    name='Branches', 
    options=branch_values,
)




month_values = result['InvoiceMonth'].unique().tolist()
month_dict = {month_name: i+1 for i, month_name in enumerate(calendar.month_name[1:])}
sorted_months = sorted(month_values, key=lambda x: month_dict[x])

Month = pn.widgets.Select(
    name='Month', 
    options=sorted_months,
    value=sorted_months[-1], # set default value to the highest available month
)

year_values = result['InvoiceYear'].unique().tolist()
Year = pn.widgets.Select(
    name='Year', 
    options=year_values,
)



grade_scale = {
    'A': (90, 100),
    'B': (80, 89.99999999),
    'C': (70, 79.99999999),
    'D': (60, 69.99999999),
    'F': (0, 59.99999999)
}

# Define function to get grade based on percentage
def get_grade(percentage, grade_scale):
    for grade, range_ in grade_scale.items():
        if percentage >= range_[0] and percentage <= range_[1]:
            return grade
    return None

iresponse = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.Branch == Branches) &
        (idf.InvoiceYear == Year) &
        #(idf.Location.isin(Locations.options)) &
        (~idf.ServiceType.str.contains('PM'))
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location'])  
    .agg(Avg_Response_Time=('Response', 'mean'), Score=('response_score', 'sum'), Target_Score=('response_max', 'sum'))
    .reset_index()
   # .sort_values(by=['Branch'])
    .assign(Percent=lambda x: x['Score'] / x['Target_Score'] * 100)
    .round({'Avg_Response_Time': 3, 'Score': 3, 'Target_Score': 3, 'Percent': 3})
    .assign(Grade=lambda x: x['Percent'].apply(lambda pct: get_grade(pct, grade_scale)))
    .reset_index(drop=True) 
)

icomplete = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.Branch == Branches) &
        (idf.InvoiceYear == Year) &        
        (~idf.ServiceType.str.contains('PM'))
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location'])
    .agg(Avg_Complete_Time=('Time_to_Complete', 'mean'), Score=('complete_score', 'sum'), Target_Score=('complete_max', 'sum'))
    .reset_index()
   # .sort_values(by=['Branch', 'Location'])
    .assign(Percent=lambda x: x['Score'] / x['Target_Score'] * 100)
    .round({'Avg_Complete_Time': 3, 'Score': 3, 'Target_Score': 3, 'Percent': 3})
    .assign(Grade=lambda x: x['Percent'].apply(lambda pct: get_grade(pct, grade_scale)))
    .reset_index(drop=True)   
)

iinvoice = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.Branch == Branches) &
        (idf.InvoiceYear == Year) &        
        (~idf.ServiceType.str.contains('PM'))
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location'])
    .agg(Avg_Invoice_Time=('Days_to_Submit', 'mean'), Score=('invoice_score', 'sum'), Target_Score=('invoice_max', 'sum'))
    .reset_index()
   # .sort_values(by=['Branch', 'Location'])
    .assign(Percent=lambda x: x['Score'] / x['Target_Score'] * 100)
    .round({'Avg_Invoice_Time': 3, 'Score': 3, 'Target_Score': 3, 'Percent': 3})
    .assign(Grade=lambda x: x['Percent'].apply(lambda pct: get_grade(pct, grade_scale)))
    .reset_index(drop=True)    
)

ipm = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.Branch == Branches) &
        (idf.ServiceType.str.contains('PM'))
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location'])
    .agg(
        Completed=('ServiceType', lambda x: (x == 'PM').sum()),
        Due=('PM_Score', 'size'),
        Score=('PM_Score', 'mean'),
    )
    .assign(Target_Score='10')
    .reset_index()
    #.sort_values(by=['Branch', 'Location'])
    .round({'Score': 3})
    .assign(Percent=lambda x: x['Score'] / 10 * 100)
    .round({'Percent': 3})
    .assign(Grade=lambda x: x['Percent'].apply(lambda pct: get_grade(pct, grade_scale)))
    #.rename(columns={'PM_Score': 'Avg_PM_Score'})
    .reset_index(drop=True) 
)

ioverall = (
    idf[
        (idf.InvoiceMonth == Month) &
        (idf.Branch == Branches)
    ]
    .groupby(['InvoiceYear','InvoiceMonth','Branch','Location'])
    .agg(
        Score1=('response_score', 'sum'), 
        Score2=('complete_score', 'sum'), 
        Score3=('invoice_score', 'sum'),
        Target_Score1=('response_max', 'sum'),
        Target_Score2=('complete_max', 'sum'),
        Target_Score3=('invoice_max', 'sum'),
        Tmax_score=('Score', 'sum'),
        Completed=('ServiceType', lambda x: (x == 'PM').sum()),
        Incomplete=('ServiceType', lambda x: (x == 'PM Incomplete').sum()),
        PM_Score=('PM_Score', 'sum'),
    )
    .reset_index()
    .assign(PM_Total=lambda x: (x['Completed'] + x['Incomplete']) * 10)
    .assign(Actual_Score=lambda x: x['PM_Score'] + x['Score1'] + x['Score2'] + x['Score3'])
    .assign(Target_Score=lambda x: x['PM_Total'] + x['Target_Score1'] + x['Target_Score2'] + x['Target_Score3'])
    .assign(Percent=lambda x: x['Actual_Score'] / x['Target_Score'] * 100)
    .sort_values(by=['Branch', 'Location'])
    .reset_index(drop=True) 
    .drop(columns=['Score1','Score2','Score3','Target_Score1','Target_Score2','Target_Score3','Tmax_score','Completed','Incomplete','PM_Score','PM_Total'])
    .round({'Percent': 3})
    .assign(Grade=lambda x: x['Percent'].apply(lambda pct: get_grade(pct, grade_scale))) 
)

iresponset = (
    iresponse[
        (iresponse.InvoiceMonth == Month) &
        (iresponse.Branch == Branches) &
        (iresponse.InvoiceYear == Year)
    ]    
    .groupby(['Branch','InvoiceYear','InvoiceMonth'])
    .agg(Actual_Score=('Score', 'sum'), Total_Score=('Target_Score', 'sum'))
    .reset_index()
    .assign(Percent=lambda x: x['Actual_Score'] / x['Total_Score'] * 100)
    .assign(Overall_Score=lambda x: x['Percent'].apply(lambda pct: get_grade(pct, grade_scale)))
    .drop(columns=['Actual_Score','Total_Score','Percent'])
    .reset_index(drop=True) 
)


tabulator_settings = {
    'show_index': False,
    'hidden_columns': ['InvoiceYear', 'InvoiceMonth', 'Branch'],
    #'layout': 'fit_data_stretch',
    'layout': 'fit_columns',
#    'width': 608,
    'configuration': {'columnDefaults': {'headerSort': False}},
    'header_align': 'center',
    'text_align': 'center'
}

iresponse = iresponse.rename(columns={'Location': 'Location_r'})
icomplete = icomplete.rename(columns={'Location': 'Location_c'})
ioverall = ioverall.rename(columns={'Location': 'Location_o'})
ipm = ipm.rename(columns={'Location': 'Location_p'})
iinvoice = iinvoice.rename(columns={'Location': 'Location_i'})

itable1 = iresponse.pipe(pn.widgets.Tabulator, **tabulator_settings)
itable2 = icomplete.pipe(pn.widgets.Tabulator, **tabulator_settings)
itable3 = iinvoice.pipe(pn.widgets.Tabulator, **tabulator_settings)
itable4 = ipm.pipe(pn.widgets.Tabulator, **tabulator_settings)
itable5 = ioverall.pipe(pn.widgets.Tabulator, **tabulator_settings)

top1 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black;">Response</div>')
top2 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black;">Time to Complete</div>')
top3 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black;">Days to Invoice</div>')
top4 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black;">PM Completion</div>')
top5 = pn.pane.HTML('<div style="text-align: center; font-size: 48px; font-weight: bold; color: black; background-color: #FFD600; border: 3px solid black;">Overall Score</div>')


line_break = pn.pane.HTML('<br>')
font_pane = pn.pane.HTML("<span style=font-size: 24px>")
span = pn.pane.HTML("</span>")
spacer = pn.layout.Spacer(width=20)

responsetarget = result_dict['Response'][0]
completetarget = result_dict['Time_to_Complete'][0]
invoicetarget = result_dict['Days_to_Submit'][0]
pmtarget = result_dict['PM_Completion'][1]
overalltarget = 100

ihvplot = iresponse.hvplot.bar(
        x='Location_r', 
        y='Avg_Response_Time', 
        color=PALETTE[0], 
        bar_width=.3, 
        width=1000, 
        line_width=3, 
        height=300, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,3),
        dynamic=True,
    ).opts(xlabel="",ylabel="Hours to Respond",active_tools=['box_select', 'lasso_select'])



ihvplot2 = icomplete.hvplot.bar(
        x='Location_c', 
        y='Avg_Complete_Time', 
        color=PALETTE[1], 
        bar_width=.3, 
        width=1000, 
        line_width=3, 
        height=300, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,20),
        dynamic=True
    ).opts(xlabel="",ylabel="Hours to Complete",active_tools=['box_select', 'lasso_select'])

ihvplot3 = iinvoice.hvplot.bar(
        x='Location_i', 
        y='Avg_Invoice_Time', 
        color=PALETTE[2], 
        bar_width=.3, 
        width=1000, 
        line_width=3, 
        height=300, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,25),
        dynamic=True
    ).opts(xlabel="",ylabel="Days to Invoice",active_tools=['box_select', 'lasso_select'])

ihvplot4 = ipm.hvplot.bar(
        x='Location_p',  
        y='Score', 
        color=PALETTE[3], 
        bar_width=.3, 
        width=1000, 
        line_width=3, 
        height=300, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,11),
        dynamic=True,
    ).opts(xlabel="",ylabel="PM Completion",active_tools=['box_select', 'lasso_select'])


ihvplot5 = ioverall.hvplot.bar(
        x='Location_o',
        y='Percent', 
        color=PALETTE[4], 
        bar_width=.3, 
        width=1000, 
        line_width=3, 
        height=300, 
        yformatter='%.2f', 
        use_index=True,
        ylim=(0,110),
        dynamic=True,
    ).opts(xlabel="",ylabel="Overall Performance",active_tools=['box_select', 'lasso_select'])

target_line = hv.HLine(responsetarget).opts(line_dash='dotted', color='red') #* hv.Text("",responsetarget+1,"Target")
ihvplot = ihvplot * target_line

target_line1 = hv.HLine(completetarget).opts(line_dash='dotted', color='red')
ihvplot2 = ihvplot2 * target_line1

target_line2 = hv.HLine(invoicetarget).opts(line_dash='dotted', color='red')
ihvplot3 = ihvplot3 * target_line2

target_line3 = hv.HLine(pmtarget).opts(line_dash='dotted', color='red')
ihvplot4 = ihvplot4 * target_line3

target_line4 = hv.HLine(overalltarget).opts(line_dash='dotted', color='red')
ihvplot5 = ihvplot5 * target_line4


main= pn.FlexBox(*[
    pn.Column(
        
        pn.Row(
            pn.Card(pn.Column(top5,itable5.panel(),ihvplot5.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
        ),
        
        pn.Row(
            pn.Card(pn.Column(top1,itable1.panel(),ihvplot.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
            #background='black'
        ),
 
        pn.Row(
            pn.Card(pn.Column(top2,itable2.panel(),ihvplot2.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
            #background='black'
        ),        
        
        pn.Row(
            pn.Card(pn.Column(top3,itable3.panel(),ihvplot3.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
            #background='black'
        ),
        
        pn.Row(
            pn.Card(pn.Column(top4,itable4.panel(),ihvplot4.panel(), ),collapsible=False,background='White',margin=(40,40,40,40),hide_header=True ),
            #background='black'
        )        
        
    )       
], align_content='space-evenly', justify_content="space-evenly")

template = pn.template.FastListTemplate(
    title='Wiese Report Card', 
    site='<a class="navbar-brand app-logo" href="/"><img src="https://wieseusa.com/img/logo-Wiese2.png" class="app-logo"></a>',
    site_url="https://www.wieseusa.com",
    sidebar=[Year,Month,Branches],
    main=[main],
    accent_base_color="#FFD600",
    header_background="#FFFFFF",
    main_max_width='85%',
    sidebar_width=300,
    logo='https://s7d2.scene7.com/is/image/Caterpillar/CM20220222-5c3c2-280a8?fmt=png-alpha',
    header_color="#FFFFFF",
    header_accent_base_color='#FFD600',
    background_color ="#f2f2f2",
    favicon = "https://wieseusa.com/img/logo-Wiese2.png",
    theme_toggle = False
)

pn.panel(template).servable(title='test')
