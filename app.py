import panel as pn
pn.extension('tabulator', sizing_mode="stretch_width")
import hvplot.pandas
import pandas as pd
import holoviews as hv
import calendar
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from datetime import datetime, timedelta
from markupsafe import Markup
hv.extension('bokeh')

pd.set_option('display.float_format', str)


PALETTE = ["#88d8b0", "#ff6f69", "#b39cd0" ]


#df = pd.read_csv('C:/Users/crezaie/Desktop/ExcelFile/sample.csv')
df = pd.read_csv('https://raw.githubusercontent.com/crezaie/catdash/main/data/sample.csv')
#df = pd.read_csv('C:/Users/crezaie/Desktop/WieseScoreCard/CAT.csv')
full = df.reset_index(drop=True)

df["FirstContact"] = pd.to_datetime(df["FirstContact"], format="%m/%d/%y %H:%M")
df["ResponseTime"] = pd.to_datetime(df["ResponseTime"], format="%m/%d/%y %H:%M")
df["LastWorkTime"] = pd.to_datetime(df["LastWorkTime"], format="%m/%d/%y %H:%M")
df["ArrivalTime"] = pd.to_datetime(df["ArrivalTime"], format="%m/%d/%y %H:%M")
df["ProposalTime"] = pd.to_datetime(df["ProposalTime"], format="%m/%d/%y %H:%M")
df["InvoiceTime"] = pd.to_datetime(df["InvoiceTime"], format="%m/%d/%y %H:%M")


result_dict = {'Response': [1, 25],
        'Arrival': [8, 10],
        'Complete': [20, 40],
        'Proposal': [12, 10],
        'Invoice': [15, 10]}


result = df.groupby(["Branch", "InvoiceMonth", "ServiceType"], as_index=False, sort=False).apply(lambda x: pd.Series({
    "Response": round((x["ResponseTime"] - x["FirstContact"]).mean()/np.timedelta64(1, 'h'), 2),
    "Arrival": round((x["ArrivalTime"] - x["FirstContact"]).mean()/np.timedelta64(1, 'h'), 2),
    "Complete": round((x["LastWorkTime"] - x["FirstContact"]).mean()/np.timedelta64(1, 'h'), 2),
    "Proposal": round((x["ProposalTime"] - x["ArrivalTime"]).mean()/np.timedelta64(1, 'h'), 2),
    "Invoice": round((x["InvoiceTime"] - x["LastWorkTime"]).mean()/np.timedelta64(1, 'D'), 2),
    "Cost": round(x["TotalCost"].sum(),2),
    "Labor Hours": round(x["LaborHours"].sum(),2)
}))#.reset_index().sort_values(by=['Branch','InvoiceMonth'])


result['response_score'] = result.apply(lambda row: result_dict['Response'][1] if row['Response'] <= result_dict['Response'][0] else 0, axis=1)

result['arrival_score'] = result.apply(lambda row: result_dict['Arrival'][1] if row['Arrival'] <= result_dict['Arrival'][0] else 0, axis=1)

result['complete_score'] = result.apply(lambda row: result_dict['Complete'][1] if row['Complete'] <= result_dict['Complete'][0] else 0, axis=1)

result['proposal_score'] = result.apply(lambda row: result_dict['Proposal'][1] if row['Proposal'] <= result_dict['Proposal'][0] else 0, axis=1)

result['invoice_score'] = result.apply(lambda row: result_dict['Invoice'][1] if row['Invoice'] <= result_dict['Invoice'][0] else 0, axis=1)

result['Score'] = round(result[['response_score', 'arrival_score', 'complete_score', 'proposal_score', 'invoice_score']].sum(axis=1),2)

result = result.sort_values(by=['Branch', 'InvoiceMonth']).reset_index(drop=True)



# drop original columns
scoretable = result.drop(['Response', 'Arrival', 'Complete', 'Proposal', 'Invoice', 'ServiceType', 'Cost', 'Labor Hours'], axis=1)

# rename score columns
scoretable = scoretable.rename(columns={'response_score': 'Response', 
                                'arrival_score': 'Arrival', 
                                'complete_score': 'Complete', 
                                'proposal_score': 'Proposal', 
                                'invoice_score': 'Invoice'})




idf = result.interactive()
ifull=full.interactive()
iscore = scoretable.interactive()

# Get the unique values in the 'branch' column
branch_values = df['Branch'].unique().tolist()
Branches = pn.widgets.ToggleGroup(options=branch_values, value=branch_values, name='Branches',button_type='success')

month_values = full['InvoiceMonth'].unique().tolist()
month_dict = {month_name: i+1 for i, month_name in enumerate(calendar.month_name[1:])}
sorted_months = sorted(month_values, key=lambda x: month_dict[x])

Month = pn.widgets.Select(
    name='Month', 
    options=sorted_months,
    value=sorted_months[-1], # set default value to the highest available month
)


yaxis = pn.widgets.Select(
    name='KPI', 
    options=['Response','Arrival','Complete','Proposal','Invoice']
)

ifullpipe = (  
    ifull[
        (ifull.InvoiceMonth == Month) & 
        (ifull.Branch.isin(Branches))
    ]    
    [['Branch', 'WieseID', 'ServiceType','TotalCost','LaborHours']] 
    # .rename(columns={'WieseID': 'EquipID'})
    # rename(columns={'WieseID': 'Equip ID'})
    .reset_index()
    .sort_values(by='Branch')  
    .reset_index(drop=True)
)




ipipeline = (  
    idf[
        (idf.InvoiceMonth == Month) & 
        (idf.Branch.isin(Branches))
    ]    
    .groupby(['InvoiceMonth','Branch', 'ServiceType', yaxis.value]) # pass a list of column names to groupby
    .sum()
    .reset_index()
    .sort_values(by='Branch')  
    .reset_index(drop=True)
)


   
   
itable = ifullpipe.pipe(pn.widgets.Tabulator, pagination='remote', page_size=15, show_index=False)
   
ihvplot = ipipeline.hvplot.bar(x='Branch', y=yaxis, by='ServiceType', color=PALETTE, bar_width=.1, width=200, line_width=3, height=300, stacked=True, yformatter='%.0f', use_index=False)
   
   
   

# create a sample dataframe
df2 = pd.DataFrame({
    'Target': [4150],
    'Actual': [3275],
    'Score': [79]
})

yo = pd.DataFrame({
    'Target': [35],
    'Actual': [33],
    'Score': [94]
})

def format_table(df):
    formatted_table = (
        df2.style
        .hide(axis="index")
        .set_table_styles([{'selector': 'thead', 'props': [('display', 'none')]}])
        .set_properties(**{'text-align': 'center', 'border-collapse': 'collapse'})
        .set_table_attributes('style="border-collapse: collapse;"')
        .set_table_styles([
            {'selector': 'th', 'props': [('border', 'none'), ('padding', '5px 10px'), ('text-align', 'center'), ('font-size', '16px'), ('color', 'black'), ('background-color', '#FFD600')]},
            {'selector': 'td', 'props': [('border', '1px solid black'), ('padding', '5px 10px'), ('text-align', 'center')]}
        ])
        .format({"%": "{:.0%}"})
    )
    return formatted_table

table = format_table(df)
table2 = format_table(yo)

# define the card layout
def format_card(title, table):
    formatted_card = pn.Card(
        pn.pane.HTML(f'<div style="text-align: center; font-size: 24px; font-weight: bold; color: black;">{title}</div>', style={'margin-bottom': '10px'}),
        pn.pane.HTML('<div style="font-size: 72px; color: green; text-align: center;">A</div>', style={'margin-bottom': '20px'}),
        table,
        sizing_mode='stretch_width',
        collapsible=False
    )
    return formatted_card


card = format_card('Overall Score',table)
card2 = format_card('Test',table2)

# define multiple cards with border
cardrow = pn.Row(card2, card2, card2)

cardfull = pn.Column(card,cardrow,cardrow)

# cardfull



line_break = pn.pane.HTML('<br>')
font_pane = pn.pane.HTML("<span style=font-size: 24px>")
span = pn.pane.HTML("</span>")




tab1 = pn.Column(
    ihvplot.panel(),
    itable.panel()
)

tabs = pn.Tabs(
    ('Insights', tab1),
    ('Score Card', cardfull),  
    dynamic=True
)
tabs

main = pn.Column(
    tabs
)


template = pn.template.FastListTemplate(
    title='Wiese Report Card', 
    site='<a class="navbar-brand app-logo" href="/"><img src="https://wieseusa.com/img/logo-Wiese2.png" class="app-logo"></a>',
    site_url="https://www.wieseusa.com",
    sidebar=[Month,line_break,line_break,yaxis,font_pane,Branches],
    main=[main],
    accent_base_color="#FFD600",
    header_background="#FFFFFF",
    main_max_width='100%',
    sidebar_width=300,
    logo='https://s7d2.scene7.com/is/image/Caterpillar/CM20220222-5c3c2-280a8?fmt=png-alpha',
    header_color="#FFFFFF",
    background_color ="#f2f2f2",
    favicon = "https://wieseusa.com/img/logo-Wiese2.png",
    theme_toggle = False
)

pn.panel(template).servable(title='test')

# from flask import (Flask, redirect, render_template, request,
#                    send_from_directory, url_for)

# flask_app = Flask(__name__)


# @flask_app.route('/')
# def display_template():
#     return 'Hello!'

# def panel_app():
#     return template #"# This Panel app runs alongside flask, access the flask app at [here](./flask/app)"

# pn.serve({'panel': panel_app}, port=80)

# if __name__ == '__main__':
#     flask_app.run(host='0.0.0.0', port=80, debug=True)
