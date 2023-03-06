import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from PIL import Image
from streamlit_player import st_player
from plotly.subplots import make_subplots

###pandas set options in cases when large dataframe needs to be displayed
pd.set_option("styler.render.max_elements", 999_999_999_999) #To avoid display error on large tables
######################################################################################################################

### SET UP OVERALL PAGE
st.set_page_config(
    page_title="Consumer Cube",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

### HIDE FIRST RADIO BUTTON SO NO DEFAULT SELECTION
st.markdown(
    """ <style>
            div[role="radiogroup"] >  :first-child{
                display: none !important;
            }
        </style>
        """,
    unsafe_allow_html=True
)

# HIDE TABLE ROW INDEX
st.markdown(
    """ <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
        """,
    unsafe_allow_html=True
)

### SET UP SIDEBAR
with st.sidebar:
    logo = Image.open("C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\logo.png")
    st.image(logo, width=200)
    st.text("")
    st.text("")
    choose = option_menu("",
                            ["Welcome","About", "Definitions", "Consumer Cube", "Feedback"],
                         icons=['file-play','info-circle','card-list','box','envelope'],
                         default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#0F1014"},
        "icon": {"color": "#FFFFFF", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#333540"},
        "nav-link-selected": {"background-color": "#333540"},
    }
    )
##121214 dark grey
#8b0107 red

######################################################################################################################

### PULL THE DATA
@st.cache_resource
def pull_data():   
    dfc = pd.read_pickle('C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\zip_to_cluster.pkl') 
    #dfp = pd.read_pickle('C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\product_to_zip_mapping.pkl')
    #dfp = pd.read_pickle('C:/CodeShare/DataPull2022/df_swire_sales_2022.pkl')
    dfp = pd.read_pickle('C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\slim_sales2.pkl')
    dfs = pd.read_pickle('C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\stores_with_volumes.pkl')
    dfi = pd.read_pickle('C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\df_spectra2_indices.pkl')

    dfi.rename(columns = {'ZIP_CRITERIA_COUNT': 'Count'}, inplace=True)
    dfp.rename(columns = {'MATERIAL_DESCRIPTION':'MATERIAL','BRAND_DESC':'BRAND','CALORIE_CAT_DESC':'CALORIE','IC_FC_ATTRIBUTE':'IC_FC','FLAVOUR_DESC':'FLAVOUR','PACK_TYPE_DESC':'PACK_TYPE','PACK_SIZE_SALES_UNIT_DESCRIPTION':'PACK_SIZE','BEV_PRODUCT_DESC':'BEV_PRODUCT'}, inplace = True)

    return dfc, dfp, dfs, dfi

dfc0, dfp0, dfs0, dfi0 = pull_data()

### Helper functions for visualizing and downloading dataframes
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')
def indexplot(x,y1,y2,data):
    fig = px.bar(data, x=x, y=y1)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=data[x], y=data[y2], name=y2, mode="lines"),secondary_y=True)
    fig.add_trace(go.Bar(x=data[x], y=data[y1], name=y1),secondary_y=False)
    fig.update_xaxes(title_text=x)
    fig.update_yaxes(title_text=y1, secondary_y=False)
    fig.update_yaxes(title_text=y2, secondary_y=True)
    return fig
def storeplot(x,y,data,title):
    fig = px.bar(data, x=x, y=y, title=title)
    fig.update_xaxes(title_text=x)
    fig.update_yaxes(title_text=y)
    return fig
def consumerplot(data):
    fig = px.bar(data, x='Consumer_Criteria', y='CONSUMER_INDEX')
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=data['Consumer_Criteria'], y=data['CONSUMER_INDEX'], name="CONSUMER_INDEX", mode="lines"),secondary_y=True)
    fig.add_trace(go.Bar(x=data['Consumer_Criteria'], y=data['Count'], name="Count"),secondary_y=False)
    fig.update_xaxes(title_text="Consumer_Criteria")
    fig.update_yaxes(title_text="Count", secondary_y=False)
    fig.update_yaxes(title_text="Index", secondary_y=True)
    return fig

def stacked_barplot(data):
    columns= list(data.columns)
    columns.remove('VOLUME_QUARTILE')
    columns.remove('Total')
    fig = px.bar(data, x ='VOLUME_QUARTILE', y = columns, labels= {'VOLUME_QUARTILE': 'Volume quartile',
            'value': '#Stores', 'variable':'Cluster'})
    return fig

def show_cluster_quantile (cluster_type):
    tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
    dfcx = dfc[['Zip',cluster_type]]
    dfcx.rename(columns={cluster_type : 'CLUSTER'}, inplace=True)
    dfs_ct = dfs.merge(dfcx, on='Zip', how='inner')
    vqc_ct = pd.crosstab(dfs_ct['VOLUME_QUARTILE'],dfs_ct['CLUSTER'],margins=True, margins_name='Total').reset_index()
    columns = list(vqc_ct.columns)
    columns.remove('VOLUME_QUARTILE')
    tab1.table(vqc_ct.style.format('{:,.0f}',subset = columns))
    columns.remove('Total')
    fig = px.bar(vqc_ct.head(4), x ='VOLUME_QUARTILE', y = columns, labels= {'VOLUME_QUARTILE': 'Volume quartile',
    'value': '#Stores', 'variable':'Cluster'})
    tab2.plotly_chart(fig, use_container_width=True)
    csv = convert_df(vqc_ct)
    dlname = 'WHERE_WHO_' + cluster_type +'.csv'
    tab3.download_button(label = '_Download CSV_', data =csv, file_name = dlname,mime ='text/csv')

# Helper function for displaying results by cluster
def show_cluster_by_type(cluster_type):
    dfcx = dfc[['Zip',cluster_type]]
    dfcx.rename(columns={cluster_type : 'CLUSTER'}, inplace=True)
    ccols = ['TOT_VOLUME','TOT_GROSSPROFITDEADNET']
    tmp = dfp.groupby('Zip')[ccols].sum().reset_index()
    tmp['TOT_VOLUME'] = tmp['TOT_VOLUME'].astype(float)
    tmp['TOT_GROSSPROFITDEADNET'] = tmp['TOT_GROSSPROFITDEADNET'].astype(float)
    dfcg_sel = tmp.merge(dfcx, on='Zip', how='inner')
    tmp_au = dfp_au.groupby('Zip')[ccols].sum().reset_index()
    tmp_au['TOT_VOLUME'] = tmp_au['TOT_VOLUME'].astype(float)
    tmp_au['TOT_GROSSPROFITDEADNET'] = tmp_au['TOT_GROSSPROFITDEADNET'].astype(float)
    dfcg_sel_au = tmp_au.merge(dfcx, on='Zip', how='inner')

    dfcg = dfcg_sel.groupby('CLUSTER')[ccols].sum().reset_index()
    dfcg['TOT_VOLUME'] = dfcg['TOT_VOLUME'].astype(float)
    dfcg['TOT_GROSSPROFITDEADNET'] = dfcg['TOT_GROSSPROFITDEADNET'].astype(float)
    dfcg_au = dfcg_sel_au.groupby('CLUSTER')['TOT_VOLUME'].sum().reset_index()
    dfcg_au['TOT_VOLUME'] = dfcg_au['TOT_VOLUME'].astype(float)
    dfcg['per'] = dfcg['TOT_VOLUME']/np.sum(dfcg['TOT_VOLUME'])
    dfcg_au['per'] = dfcg_au['TOT_VOLUME']/np.sum(dfcg_au['TOT_VOLUME'])
    dfcg = dfcg.merge(dfcg_au, on='CLUSTER', how='inner', suffixes=('_filt','_AU'))
    dfcg['PRODUCT_INDEX'] = 100*(dfcg['per_filt'] - dfcg['per_AU'])+100
    dfcg = dfcg.sort_values(by='PRODUCT_INDEX', ascending=False)
    dfcg['OPPORTUNITY_VOLUME'] = dfcg['PRODUCT_INDEX']*dfcg['TOT_VOLUME_filt']/100
    dfcg['OPPORTUNITY_GROSSPROFITDEADNET'] = dfcg['PRODUCT_INDEX']*dfcg['TOT_GROSSPROFITDEADNET']/100
    kcols = ['CLUSTER','TOT_VOLUME_filt','TOT_GROSSPROFITDEADNET',
                     'PRODUCT_INDEX', 'OPPORTUNITY_VOLUME', 'OPPORTUNITY_GROSSPROFITDEADNET']
    dfcg = dfcg[kcols]
    dfcg.rename(columns = {'TOT_VOLUME_filt':'VOLUME','TOT_GROSSPROFITDEADNET':'GROSSPROFITDEADNET'}, inplace = True)

    tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
    tab1.table(dfcg.style.format(format_mapping))
    fig = indexplot('CLUSTER','OPPORTUNITY_GROSSPROFITDEADNET','PRODUCT_INDEX',dfcg)
    tab2.plotly_chart(fig, use_container_width=True)
    csv = convert_df(dfcg)
    dlname = cluster_type + '.csv'
    tab3.download_button(label="_Download CSV_",data=csv,file_name=dlname,mime='text/csv')

# Helper function for displaying demographics
def show_demographics(dfi, dfi_au, demographic):
    dfi0 = dfi_au[dfi_au['Consumer_Criteria_Group'] == demographic]
    dfiz0 = dfi[dfi['Consumer_Criteria_Group'] == demographic]
    dfig0 = calculate_index(dfiz0, dfi0, 'Consumer_Criteria', 'Count')
    dfig = dfig0.sort_values(by='INDEX', ascending=False)
    dfig = dfig.rename(columns={'INDEX': 'CONSUMER_INDEX', 'adder_group_filt': 'Count'})
    dfig = dfig.drop(columns=['adder_group_au','percentage_filt','percentage_au'])

    tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
    cons_format_mapping={'Count': '{:,.0f}','CONSUMER_INDEX':'{:.2f}'}
    dfig['Save Selection'] = False
    dfige=dfig.set_index('Consumer_Criteria')
    edited_dfig=tab1.experimental_data_editor(dfige.style.format(cons_format_mapping),use_container_width=True)
    edited_dfig=edited_dfig.reset_index()
    fig = consumerplot(edited_dfig)
    tab2.plotly_chart(fig, use_container_width=True)
    csv = convert_df(edited_dfig)
    dlname = demographic + '.csv'
    tab3.download_button(label="_Download CSV_",data=csv,file_name=dlname,mime='text/csv')
    return edited_dfig

# Helper function for displaying top 10 and bottom 10 by index
def show_best_worst(df0, dfau0, grouper, adder, pcols, volume_limit):
    dfpg = dfp.groupby(grouper)[pcols].sum().reset_index()
    dfinx = calculate_index(df0, dfau0, grouper, adder)
    dfpg = dfpg.merge(dfinx, on=grouper, how='inner')
    dfpg.rename(columns={'INDEX':'PRODUCT_INDEX'}, inplace=True)
    dfpg = dfpg.sort_values(by='PRODUCT_INDEX', ascending=False)

    dfpg['OPPORTUNITY_VOLUME'] = dfpg['PRODUCT_INDEX']*dfpg['SUM_VOLUME']/100
    dfpg['OPPORTUNITY_PROFIT'] = dfpg['PRODUCT_INDEX']*dfpg['SUM_GROSSPROFITDEADNET']/100
    dfpg.rename(columns = {'SUM_VOLUME':'VOLUME','SUM_GROSSPROFITDEADNET':'PROFIT'}, inplace = True)
    dfpg.drop(columns=['adder_group_filt','adder_group_au'], inplace=True)
    format_mapping={'VOLUME': '{:,.0f}', 'PROFIT': '${:,.2f}', 'PRODUCT_INDEX':'{:.2f}', 'OPPORTUNITY_VOLUME':'{:,.0f}', 'OPPORTUNITY_PROFIT':'${:,.2f}'}
    
    if(volume_limit > 0):
        dfpg = dfpg[dfpg['VOLUME'] > volume_limit]

    st.write('TO prioritize:')
    df_top10 = dfpg.head(10)
    tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
    tab1.table(df_top10.style.format(format_mapping))
    fig = indexplot(grouper,'OPPORTUNITY_PROFIT','PRODUCT_INDEX',df_top10)
    tab2.plotly_chart(fig, use_container_width=True)
    csv = convert_df(df_top10)
    tab3.download_button(label="_Download CSV_",data=csv,file_name='df_top10.csv',mime='text/csv')

    st.write('NOT to prioritize:')
    df_bot10 = dfpg.tail(10).sort_values(by='PRODUCT_INDEX')
    tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
    tab1.table(df_bot10.style.format(format_mapping))
    fig = indexplot(grouper,'OPPORTUNITY_PROFIT','PRODUCT_INDEX',df_bot10)
    tab2.plotly_chart(fig, use_container_width=True)
    csv = convert_df(df_bot10)
    tab3.download_button(label="_Download CSV_",data=csv,file_name='df_bot10.csv',mime='text/csv')

# Helper function for on-the-fly volume quartiling

def add_volume_quartile(dfs):
    dfsx = dfs.sort_values(by='SUM_TOT_VOLUME')
    dfsx['RUNNING_SUM_VOL'] = dfsx['SUM_TOT_VOLUME'].cumsum()
    quartiles = np.max(dfsx['RUNNING_SUM_VOL'])/4
    dfsx['VOLUME_QUARTILE'] = np.where(dfsx['RUNNING_SUM_VOL'] <= quartiles*1, 4, 
                                    np.where(dfsx['RUNNING_SUM_VOL'] <= quartiles*2, 3,
                                            np.where(dfsx['RUNNING_SUM_VOL'] <= quartiles*3, 2,
                                                    np.where(dfsx['RUNNING_SUM_VOL'] <= quartiles*4, 1, 0))))
    return dfsx

# Helper function for percentiles
def calculate_percentiles(df0, grouper, adder):
    df = df0[[grouper, adder]]
    dfg = df.groupby(grouper)[adder].sum().reset_index(name='adder_group')
    dfg['percentage'] = dfg['adder_group']/np.sum(dfg['adder_group'])
    return dfg

# Helper function for calculating index by col
def calculate_index(df0, dfau0, grouper, adder):
    df = calculate_percentiles(df0, grouper, adder)
    dfau = calculate_percentiles(dfau0, grouper, adder)
    df = df.merge(dfau, on=grouper, how='inner', suffixes=('_filt','_au'))
    df['INDEX'] =100*(df['percentage_filt']-df['percentage_au'])+100
    return df


######################################################################################################################

### WELCOME PAGE
if choose == "Welcome":
    video_file = open('C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\IntroVid3.mp4','rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

### ABOUT PAGE
if choose == "About":
    cube = Image.open("C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\CubeImage.png")
    st.header(':red[About]')
    col1, col2 = st.columns(2)
    col1.markdown('Welcome to the **Consumer Cube** application! The primary purpose of this tool is for designing sales and marketing campaigns by assisting the user in deciding **who to target** (consumer demographic), **where to target** (geography, store) and **what to target** (brand, material, category).  This application combines consumer demographic data, live sales data, and advanced analytics to help users make better data-driven decisions.')
    col2.image(cube, width=300)
    st.subheader(':blue[How to Use the Consumer Cube]')
    with st.expander('Instructions: WHAT to sell to WHO'):
        st.markdown('1. Click **Consumer Cube** on the left')
        st.markdown('2. Select **WHAT to sell to WHO**')
        st.markdown('3. Select product attributes you are interested in. Once product attributes are selected, you will see tables for Channel and Clusters dynamically changing below.  Note: see the definitions page and/or video tutorial for help interpreting the data for decision-making.')
        st.markdown('4. Select cluster(s) you want to drill into to see various consumer attributes for your selected clusters. When you select cluster(s), Consumer attribute tables will automatically populate.')
        st.markdown('5. On the right side of consumer attribute tables you can optionally select groups within each consumer attribute which will be saved for you to export later as a consumer profile that relates to the product attributes you selevted at the start of the workflow.')
        st.markdown('6. At the bottom of the worflow you can see all user selections and optionally download a csv of your selections.')
        st.markdown('')
        st.markdown('TIP:  All tables have three tabs (**Data**, **Plot**, **CSV**).  The **Data** tab shows the data in a table format.  The **Plot** tab shows a bar and line chart and can be downloaded as .png by clicking the icon in top right.  The **CSV** tab has a button to download the table as a CSV.')
    with st.expander('Instructions: WHAT to sell WHERE'):
        st.markdown('1. Click **Consumer Cube** on the left')
        st.markdown('2. Select **WHAT to sell WHERE**')
        st.markdown('3. Select channel and clusters you are interested in. These selections will filter the data for the rest of the workflow. Note: see the definitions page and/or video tutorial for help interpreting the data for decision-making.')
        st.markdown('4. Select product characteristics of interest. When you make a selection, tables will populate showing the top 10 products to prioritize (highest index) or not prioritize (lowest index), for your selected channel and cluster.')
        st.markdown('5. Select volume quartile of interest where quartile 1 = highest volume, and quartile 4 = lowest volume.  This quartile selection will filter the list of stores shown.')
        st.markdown('6. The table of stores shown is the top 20 volume stores within the selected channel, cluster, and volume quartile.  The plot shows the Account name distribution of the top 20 volume stores.  The full customer list can be downloaded with the CSV tab.')
        st.markdown('7. At the bottom of the worflow you can see all user selections and optionally download a CSV of your selections.')
        st.markdown('')
        st.markdown('TIP:  All tables have three tabs (**Data**, **Plot**, **CSV**).  The **Data** tab shows the data in a table format.  The **Plot** tab shows a bar and line chart and can be downloaded as .png by clicking the icon in top right.  The **CSV** tab has a button to download the table as a CSV.')
    with st.expander('Instructions: WHERE to sell to WHO'):
        st.markdown('1. Click **Consumer Cube** on the left')
        st.markdown('2. Select **WHERE to sell to WHO**')
        st.markdown('3. Select channel, geography and key account information, if no selection is made then entire consumer universe is considered. The tables presented would change dynamically based on your selections. Note: see the definitions page and/or video tutorial for help interpreting the data for decision-making.')
        st.markdown('4. Select cluster(s) and Volume quartile you want to drill into to see a list of stores and their attributes for your selected cluster/Volume quartile combination.')
        st.markdown('5. Next you can select consumer criteria and the table will present number of stores based on your selection. You can then further select groups within each consumer criteria to look at the list of stores falling in your selection criteria.')
        st.markdown('6. At the bottom of the worflow you can see all user selections and optionally download a csv of your selections.')
        st.markdown('')
        st.markdown('TIP:  All tables have three tabs (**Data**, **Plot**, **CSV**).  The **Data** tab shows the data in a table format.  The **Plot** tab shows a bar and line chart and can be downloaded as .png by clicking the icon in top right.  The **CSV** tab has a button to download the table as a CSV.')     
    st.subheader(':blue[Tutorial Videos]')
    st.markdown('WHAT to sell to WHO')
    video_file1 = open('C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\WhatToSellToWho_Tutorial4.mp4','rb')
    video_bytes1 = video_file1.read()
    st.video(video_bytes1)
    st.markdown('WHAT to sell WHERE')
    video_file2 = open('C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\WHatToSellWhere_Tutorial1.mp4','rb')
    video_bytes2 = video_file2.read()
    st.video(video_bytes2)

### DEFINITIONS PAGE
if choose == "Definitions":
    st.header(':red[Definitions]')
    st.markdown(':blue[**Clustering**]')
    st.markdown('Nielsen Spectra data is used to group consumers into clusters based on their common socioeconomic and demographic attributes.  Four different clustering methods are used in this application (SEL, AVG-3, AVG-4, and AVG-5). The graphic below shows the underlying data used to differentiate between clusters within each method.')
    clusters = Image.open("C:\\Users\\ddeming\\OneDrive - Swire Coca-Cola, USA\\Documents\\Projects\\streamlit\\NLI_Streamlit\\Customer_Cube_App\\accessories\\clusters.png")
    st.image(clusters)
    #st.markdown('AVG-3, AVG-4, and AVG-5 are similar with the main difference being the number of clusters in each group. Their relationship can be seen in the graphic below')
    #aclusters = Image.open("C:\CodeShare\aclusters.png")
    #st.image(aclusters)
    st.markdown('Check out the link below for an in-depth analysis of the four clustering methods.')
    st.markdown("""<a href="https://swirecocacola.sharepoint.com/:p:/r/sites/ERA/_layouts/15/doc2.aspx?sourcedoc=%7B66537056-DAE2-4D7C-861B-A4B573F916BD%7D&file=Consumer%20Segmentation%20Cube.pptx&action=edit&mobileredirect=true&cid=0054c645-0773-4ac0-a285-c82199d87fba/">Segmentation Cube</a>""", unsafe_allow_html=True,)
    
    st.markdown(':blue[**Indexing**]')
    st.markdown('Indexing is used in this app to compare a user selected universe to the unfiltered Swire footprint.  When a user makes a filter selection, an index may be dynamically calculated to quantify this comparison. An index value > 100 indicates the attribute group is more prominent in the user selected universe compared to the overall Swire footrpint.')

    st.markdown(':blue[**Column Definitions**]')
    st.markdown('OPPORTUNITY_VOLUME = Volume X Index')
    st.markdown('OPPORTUNITY_PROFIT = GrossProfitDeadNet X Index')

### FEEDBACK PAGE
if choose == "Feedback":
    st.header(':red[Feedback]')
    st.markdown('**We want your feedback!** This application is in a testing phase and we are open to suggestions.')
    st.markdown('To comment on the functionality or usage of this app, please send an email to DataScience@swirecc.com')
    st.markdown('To report a technical issue with this application or the underlying data, please send an email to IT@swirecc.com')
    st.markdown('Thank You!')
    #dtw = Image.open("C:\CodeShare\DTW.gif")
    #st.image(dtw, width=400)

######################################################################################################################

### CONSUMER CUBE PAGE
if choose == "Consumer Cube":
    st.header(':red[Consumer Cube]')


    ## SELECT CONTEXT
    with st.expander('What would you like to investigate?'): 
        context = st.radio('label',
            ['Hide first option',
            'WHAT to sell to WHO',
            'WHAT to sell WHERE',
            'WHERE to sell to WHO'],
        label_visibility='collapsed', horizontal=True)

######################################################################################################################

        # WHAT to sell WHERE

    if (context == 'WHAT to sell WHERE'):
            
        # Reset dataframes
            dfc = dfc0.copy()
            dfp = dfp0.copy()
            dfs = dfs0.copy()
            dfi = dfi0.copy()

        # Filters for analysis universe
            st.markdown(':blue[Select analysis universe for volume quartiling]')
            col1, col2, col3 = st.columns(3)
            channel_select = col1.multiselect('Channel', sorted(dfp['SUPER_CHANNEL_DEFINITION'].unique()))
            if(len(channel_select)>0):
               dfp = dfp[dfp['SUPER_CHANNEL_DEFINITION'].isin(channel_select)]
            keyaccount_select = col2.multiselect('Key Account Plan', sorted(dfp['KEY_ACCOUNT_PLAN_DESCRIPTION_CP3'].unique()))
            if(len(keyaccount_select)>0):
                dfp = dfp[dfp['KEY_ACCOUNT_PLAN_DESCRIPTION_CP3'].isin(keyaccount_select)]
            brand_select = col3.multiselect('Brand', sorted(dfp['BRAND'].unique()))
            if(len(brand_select)>0):
                dfp = dfp[dfp['BRAND'].isin(brand_select)]

            dfp['SUM_VOLUME'] = dfp['TOT_VOLUME'].astype(float)
            dfp['SUM_GROSSPROFITDEADNET'] = dfp['TOT_GROSSPROFITDEADNET'].astype(float)
            dfp_au = dfp.copy() # preserve product AU for on-the-fly indexes

        # Define stores including volume after optional filtering by brand
            dfs.drop(columns=['SUM_TOT_VOLUME', 'RUNNING_SUM_VOL', 'VOLUME_QUARTILE'], inplace=True)
            tmp = dfp.groupby(['CUSTOMER_NUMBER'])['TOT_VOLUME'].sum().reset_index(name='SUM_TOT_VOLUME')
            dfs = dfs.merge(tmp, on=['CUSTOMER_NUMBER'], how='inner')
            dfs['SUM_TOT_VOLUME'] = dfs['SUM_TOT_VOLUME'].astype(float)
            dfs = add_volume_quartile(dfs) # calculate on-the-fly volume quartiles

        # Filters for cluster, apply based on zip codes
            st.markdown(':blue[Select cluster filters]')
            col1, col2 = st.columns(2)
            cluster_types = [i for i in list(dfc.columns) if i != 'Zip'] 
            vec = [dfc[col_name].unique() for col_name in cluster_types] # initially allow all clusters
            show_clusters = [num for elem in vec for num in elem]
            cluster_type = col1.multiselect('Cluster Type', cluster_types)
            if(len(cluster_type)>0):
                vec = [dfc[col_name].unique() for col_name in cluster_type]  # filter by cluster type
                show_clusters = [num for elem in vec for num in elem]
            cluster_select = col2.multiselect('Cluster', show_clusters)
            if(len(cluster_select)>0):
                zips = list(dfc[dfc.isin(cluster_select).sum(axis=1) > 0]['Zip'].values)  # zips for filtered clusters
                dfc = dfc[dfc['Zip'].isin(zips)]
                dfp = dfp[dfp['Zip'].isin(zips)]                    # filter products and stores by zip
                dfs = dfs[dfs['Zip'].isin(zips)]

        # Show best products within this AU and cluster 
            st.subheader(':blue[**What products to prioritize, or to NOT prioritize?**]')
            product_type = st.selectbox('Select product characteristics of interest', 
                                ['None','Product','Brand','Calorie','Consumption','Flavor','Package','Pack size'])
            pcols = ['SUM_VOLUME','SUM_GROSSPROFITDEADNET']
            volume_limit = st.number_input(label='Optional: specify minimum volume filter for product table', min_value=0)

            if(product_type == 'None'):
                st.markdown('_(waiting to display results)_')
            elif(product_type == 'Product'):
                show_best_worst(dfp, dfp_au, 'MATERIAL', 'SUM_VOLUME', pcols, volume_limit)   # on-the-fly indexes
            elif(product_type == 'Brand'):
                show_best_worst(dfp, dfp_au, 'BRAND', 'SUM_VOLUME', pcols, volume_limit)
            elif(product_type == 'Calorie'):
                show_best_worst(dfp, dfp_au, 'CALORIE', 'SUM_VOLUME', pcols, volume_limit)
            elif(product_type == 'Consumption'):
                show_best_worst(dfp, dfp_au, 'IC_FC', 'SUM_VOLUME', pcols, volume_limit)
            elif(product_type == 'Flavor'):
                show_best_worst(dfp, dfp_au, 'FLAVOUR', 'SUM_VOLUME', pcols, volume_limit)
            elif(product_type == 'Package'):
                show_best_worst(dfp, dfp_au, 'PACK_TYPE', 'SUM_VOLUME', pcols, volume_limit)
            elif(product_type == 'Pack size'):
                show_best_worst(dfp, dfp_au, 'PACK_SIZE', 'SUM_VOLUME', pcols, volume_limit)

        # Show stores within this AU and cluster and geography and volume quartile
            st.subheader(':blue[**Where are these stores?**]')

            st.markdown(':blue[What volume quartile stores would you like to consider? (1=high, 4=low)]')
            volume_select = st.multiselect('Volume quartile', list(dfs['VOLUME_QUARTILE'].unique()))
            if(len(volume_select)>0):
                dfs = dfs[dfs['VOLUME_QUARTILE'].isin(volume_select)]

        # Filters for geography
            st.markdown(':blue[**After quartile selection, would you like to also limit the geography?**]')

            col1, col2, col3 = st.columns(3)
            division_select = col1.multiselect('Division', sorted(dfs['DIVISION'].unique()))
            if(len(division_select)>0):
                dfs = dfs[dfs['DIVISION'].isin(division_select)]
            state_select = col2.multiselect('Address State', sorted(dfs['ADDRESS_STATE'].unique()))
            if(len(state_select)>0):
                dfs = dfs[dfs['ADDRESS_STATE'].isin(state_select)]
            city_select = col3.multiselect('Address City', sorted(dfs['ADDRESS_CITY'].unique()))
            if(len(city_select)>0):
                dfs = dfs[dfs['ADDRESS_CITY'].isin(city_select)]

            scol = ['CUSTOMER_NUMBER','KEY_ACCOUNT_PLAN_DESCRIPTION_CP3', 'CUSTOMER_NAME',
                    'ADDRESS_STATE','ADDRESS_CITY','Zip','SUM_TOT_VOLUME']
            df_display = dfs[scol].sort_values(by='SUM_TOT_VOLUME', ascending=False)
            df_display = df_display.drop_duplicates().reset_index(drop=True)

            tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
            tab1.markdown('**Note:** _Table below displays maximum 20 stores; Please use **_CSV_** tab to download the entire list_')
            df_display_20 = df_display.head(20)
            df_display_20.rename(columns = {'KEY_ACCOUNT_PLAN_DESCRIPTION_CP3':'KEY_ACCOUNT_PLAN','Zip':'ZIP','SUM_TOT_VOLUME':'VOLUME'}, inplace = True)
            format_mapping={'VOLUME': '{:,.0f}'}
            tab1.table(df_display_20.style.format(format_mapping))
            df_plot2 = df_display_20.groupby('KEY_ACCOUNT_PLAN')['VOLUME'].sum().reset_index()
            fig2 = storeplot('KEY_ACCOUNT_PLAN','VOLUME',df_plot2,"KAP Distribution: Top 20 Stores by Volume within Selected Channel and Cluster")
            tab2.plotly_chart(fig2, use_container_width=True)
            csv = convert_df(df_display)
            tab3.download_button(label = '_Download CSV_', data =csv, file_name = 'WHAT_WHERE_KAP20.csv',mime ='text/csv')

        # Save selections 
            st.markdown('**Save Selections**')
            dfss = pd.DataFrame({"Parameter" : ["Channel","Key Account Plan","Brand","Cluster type","Cluster","Volume quartile","Division","State","City"], 
                     "Selection" : pd.Series([channel_select,keyaccount_select,brand_select,cluster_type,cluster_select,volume_select,division_select,state_select,city_select], 
                                             dtype='str')})
            
            st.table(dfss)
            csv = convert_df(dfss)
            st.download_button(label="Download Selections as CSV", data=csv, file_name='WHAT_WHERE_SELECTIONS.csv', mime='text/csv')


######################################################################################################################
   
        # WHERE to sell to WHO
    if (context == 'WHERE to sell to WHO'):
            
        # Reset dataframes
            dfc = dfc0.copy()
            dfp = dfp0.copy()
            dfs = dfs0.copy()
            dfi = dfi0.copy()

        # Filters for analysis universe
            st.markdown(':blue[Select analysis universe for volume quartiling]')
            col1, col2 = st.columns(2)
            channel_select = col1.multiselect('Channel', sorted(dfp['SUPER_CHANNEL_DEFINITION'].unique()))
            if(len(channel_select)>0):
               dfp = dfp[dfp['SUPER_CHANNEL_DEFINITION'].isin(channel_select)]
            keyaccount_select = col2.multiselect('Key Account Plan', sorted(dfp['KEY_ACCOUNT_PLAN_DESCRIPTION_CP3'].unique()))
            if(len(keyaccount_select)>0):
                dfp = dfp[dfp['KEY_ACCOUNT_PLAN_DESCRIPTION_CP3'].isin(keyaccount_select)]
            dfi = dfi[dfi['Zip'].isin(dfp['Zip'].unique())] # also filter down demographics to zips within AU

        # Define stores 
            dfs.drop(columns=['SUM_TOT_VOLUME', 'RUNNING_SUM_VOL', 'VOLUME_QUARTILE'], inplace=True)
            tmp = dfp.groupby(['CUSTOMER_NUMBER'])['TOT_VOLUME'].sum().reset_index(name='SUM_TOT_VOLUME')
            dfs = dfs.merge(tmp, on=['CUSTOMER_NUMBER'], how='inner')
            dfs['SUM_TOT_VOLUME'] = dfs['SUM_TOT_VOLUME'].astype(float)
            dfs = add_volume_quartile(dfs) # calculate on-the-fly volume quartiles

        # Filters for geography
            st.markdown(':blue[Select geographic filters]')
            col1, col2, col3 = st.columns(3)
            division_select = col1.multiselect('Division', sorted(dfs['DIVISION'].unique()))
            if(len(division_select)>0):
                dfs = dfs[dfs['DIVISION'].isin(division_select)]
            state_select = col2.multiselect('Address State', sorted(dfs['ADDRESS_STATE'].unique()))
            if(len(state_select)>0):
                dfs = dfs[dfs['ADDRESS_STATE'].isin(state_select)]
            city_select = col3.multiselect('Address City', sorted(dfs['ADDRESS_CITY'].unique()))
            if(len(city_select)>0):
                dfs = dfs[dfs['ADDRESS_CITY'].isin(city_select)]
           
        # Workflow once user selects channel 
            st.subheader(':blue[**How many stores fall in a given volume quartile and cluster?**]')

            cluster_types = [i for i in list(dfc.columns) if i != 'Zip'] 
            cluster_type = st.selectbox('Select cluster type', cluster_types)
            show_cluster_quantile (cluster_type)
 
        # Take volume quartile and cluster input for further drill down
            st.subheader(":blue[**What are those stores?**]")
            st.markdown(':blue[Select volume quartile (1=high, 4=low) and cluster to drill down]')
            
            col3, col4 = st.columns(2)
            tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
            volume_quartile_select = col3.multiselect('Volume Quartile', list(dfs['VOLUME_QUARTILE'].unique()))
            if(len(volume_quartile_select)>0):
               dfs = dfs[dfs['VOLUME_QUARTILE'].isin(volume_quartile_select)]
            
            vec = [dfc[col_name].unique() for col_name in cluster_types]  # drop down allows all cluster types
            show_clusters = [num for elem in vec for num in elem]
            cluster_select = col4.multiselect('Select Cluster',show_clusters)
            if(len(cluster_select)>0):
                zips = list(dfc[dfc.isin(cluster_select).sum(axis=1) > 0]['Zip'].values)  # zips for filtered clusters
                dfc = dfc[dfc['Zip'].isin(zips)]
                dfs = dfs[dfs['Zip'].isin(zips)]                    # filter stores by zip

            dfs_vqc = dfs[['CUSTOMER_NUMBER', 'KEY_ACCOUNT_PLAN_DESCRIPTION_CP3', 'CUSTOMER_NAME', 'ADDRESS_STATE', 'DIVISION','ADDRESS_CITY', 'Zip', 'SUM_TOT_VOLUME']].drop_duplicates()
            dfs_vqc.rename(columns = {'KEY_ACCOUNT_PLAN_DESCRIPTION_CP3':'KEY_ACCOUNT_PLAN','Zip':'ZIP','SUM_TOT_VOLUME':'VOLUME'}, inplace = True)

            tab1.markdown('**Note:** _Table below displays top 20 stores based on volume; Please use **_CSV_** tab to download the entire list_')
            dfs_vqc_20=dfs_vqc.sort_values('VOLUME',ascending=False).head(20)
            tab1.table(dfs_vqc_20.style.format('{:,.0f}', subset = ['VOLUME']))
            dfs_vqc_plot = dfs_vqc_20.groupby('KEY_ACCOUNT_PLAN')['VOLUME'].sum().reset_index()
            fig2 = storeplot('KEY_ACCOUNT_PLAN','VOLUME',dfs_vqc_plot,"KAP Distribution: Top 20 Stores by Volume within Selected Volume Quartile and Cluster")
            tab2.plotly_chart(fig2, use_container_width=True)
            csv = convert_df(dfs_vqc)
            tab3.download_button(label = '_Download CSV_', data =csv, file_name = 'WHERE_WHO_KAP20_VOL.csv',mime ='text/csv')
  
            my_zips = dfs['Zip'].unique()

        # What does my customer base look like?
            st.subheader(":blue[**What does my consumer base look like?**]")
            consumer_group_select = st.selectbox('Consumer Criteria Group', list(dfi['Consumer_Criteria_Group'].unique()))
            tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
            dfi = dfi[dfi['Consumer_Criteria_Group'] == consumer_group_select]
            dfiz = dfi[dfi['Zip'].isin(my_zips)]

            dfig = calculate_index(dfiz, dfi, 'Consumer_Criteria', 'Count')
            dfig.rename(columns={'INDEX':'CONSUMER_INDEX', 'adder_group_filt':'Count'}, inplace=True)
            dfig = dfig[['Consumer_Criteria','Count','percentage_filt','percentage_au','CONSUMER_INDEX']]
            dfig = dfig.sort_values('CONSUMER_INDEX',ascending=False)

            format_mapping_cb={'CONSUMER_INDEX': '{:,.2f}', 'Count': '{:,.0f}'}
            tab1.table(dfig.style.format(format_mapping_cb))
            fig = consumerplot(dfig[['Consumer_Criteria','CONSUMER_INDEX', 'Count']])
            tab2.plotly_chart(fig, use_container_width=True)
            csv = convert_df(dfig[['Consumer_Criteria','CONSUMER_INDEX', 'Count']])
            tab3.download_button(label = '_Download CSV_', data =csv, file_name = 'WHERE_WHO_DEMOGRAPHICS.csv',mime ='text/csv')

            
        #What stores should I sell in to target consumers of a specific demographics or socioeconomic attribute?
                     
            st.subheader(":blue[**What stores to target to cover a specific Consumer segment?**]")
            st.markdown(":blue[Select demographic of interest]")

            #Calculate the index based on consumer attribute index at zip level
            consumer_criteria_select = st.multiselect('Consumer Criteria', list(dfi['Consumer_Criteria'].unique()))
            if(len(consumer_criteria_select) == 0): # not selected yet, default to all
                consumer_criteria_select = list(dfi['Consumer_Criteria'].unique())
            per_au = np.sum(dfi[dfi['Consumer_Criteria'].isin(consumer_criteria_select)]['Count'])/np.sum(dfi['Count'])

            tmp1 = dfiz[dfiz['Consumer_Criteria'].isin(consumer_criteria_select)].groupby('Zip')['Count'].sum()
            tmp2 = dfiz.groupby('Zip')['Count'].sum()
            tmp3 = tmp1/tmp2
            tmp3 = tmp3.reset_index(name='per')
            tmp3['CONSUMER_INDEX'] = 100*(tmp3['per']-per_au)+100

            volume_limit = st.number_input(label='Optional: specify minimum volume filter for store table', min_value=0)
            if(volume_limit > 0):
                dfs = dfs[dfs['SUM_TOT_VOLUME'] >= volume_limit]
            
            tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
            tab1.markdown('**Note:** _Table below displays top 20 stores based on index; Please use **_CSV_** tab to download the entire list_')
            dfs_dfig=pd.merge(dfs,tmp3, on='Zip', how= 'inner')[['CUSTOMER_NUMBER','KEY_ACCOUNT_PLAN_DESCRIPTION_CP3', 'CUSTOMER_NAME', 'ADDRESS_STATE', 'DIVISION', 'ADDRESS_CITY', 'Zip', 'SUM_TOT_VOLUME', 'CONSUMER_INDEX']].drop_duplicates()
            dfs_dfig.rename(columns = {'KEY_ACCOUNT_PLAN_DESCRIPTION_CP3':'KEY_ACCOUNT_PLAN','Zip':'ZIP','SUM_TOT_VOLUME':'VOLUME'}, inplace = True)
            format_mapping_zl={'VOLUME': '{:,.0f}', 'VOLUME_RANK': '{:,.0f}', 'CONSUMER_INDEX':'{:.2f}'}

            dfs_dfig_20=dfs_dfig.sort_values('CONSUMER_INDEX',ascending=False).head(20)
            tab1.table(dfs_dfig_20.style.format(format_mapping_zl))
            dfs_dfig_plot = dfs_dfig_20.groupby('KEY_ACCOUNT_PLAN')['VOLUME'].sum().reset_index()
            fig2 = storeplot('KEY_ACCOUNT_PLAN','VOLUME',dfs_dfig_plot,"KAP Distribution: Top 20 Stores by Index within Selected Consumer Criteria")
            tab2.plotly_chart(fig2, use_container_width=True)
            csv = convert_df(dfs_dfig)
            tab3.download_button(label = '_Download CSV_', data =csv, file_name = 'WHERE_WHO_KAP20_INDEX.csv',mime ='text/csv')

            st.markdown('**Save Selections**')
            dfss = pd.DataFrame({"Parameter" : ["Channel","Key Account Plan","Division","State","City","Volume Quartile","Cluster","Consumer Criteria"], 
                     "Selection" : pd.Series([channel_select,keyaccount_select,division_select,state_select,city_select,volume_quartile_select,cluster_select,consumer_criteria_select],
                                    dtype='str')})
            
            st.table(dfss)
            csv = convert_df(dfss)
            st.download_button(label="Download Selections as CSV", data=csv, file_name='WHERE_WHO_SELECTIONS.csv', mime='text/csv')
       
 
 ######################################################################################################################
   
          # WHAT to sell to WHO

    if (context == 'WHAT to sell to WHO'):
            
        # Reset dataframes
            dfc = dfc0.copy()
            dfp = dfp0.copy()
            dfs = dfs0.copy()
            dfi = dfi0.copy()

            dfp_au = dfp.copy()
            dfi_au = dfi.copy()

            st.subheader(':blue[**What product attributes are likely to succeed in what channel and what cluster?**]')
            st.markdown(':blue[Product Attributes]')
            col1, col2, col3 = st.columns(3)
            mat_desc_select = col1.multiselect('Material Description', ['All']+list(dfp['MATERIAL'].unique()))
            if(len(mat_desc_select)>0):
                dfp = dfp[dfp['MATERIAL'].isin(mat_desc_select)]
            ic_fc_select = col1.multiselect('IC or FC', ['All']+list(dfp['IC_FC'].unique()))
            if(len(ic_fc_select)>0):
                dfp = dfp[dfp['IC_FC'].isin(ic_fc_select)]
            cal_cat_select = col1.multiselect('Regular or Low Calorie', ['All']+list(dfp['CALORIE'].unique()),)
            if(len(cal_cat_select)>0):
                dfp = dfp[dfp['CALORIE'].isin(cal_cat_select)]
            pkg_size_select = col2.multiselect('Package Size', ['All']+list(dfp['PACK_SIZE'].unique()))
            if(len(pkg_size_select)>0):
                dfp = dfp[dfp['PACK_SIZE'].isin(pkg_size_select)]
            pkg_type_select = col2.multiselect('Package Type', ['All']+list(dfp['PACK_TYPE'].unique()))
            if(len(pkg_type_select)>0):
                dfp = dfp[dfp['PACK_TYPE'].isin(pkg_type_select)]
            brand_desc_select = col3.multiselect('Brand', ['All']+list(dfp['BRAND'].unique()))
            if(len(brand_desc_select)>0):
                dfp = dfp[dfp['BRAND'].isin(brand_desc_select)]
            bev_desc_select = col3.multiselect('Product Description', ['All']+list(dfp['BEV_PRODUCT'].unique()))
            if(len(bev_desc_select)>0):
                dfp = dfp[dfp['BEV_PRODUCT'].isin(bev_desc_select)]
            
            pcols = ['TOT_VOLUME','TOT_GROSSPROFITDEADNET']
            dfpg = dfp.groupby('SUPER_CHANNEL_DEFINITION')[pcols].sum().reset_index()
            dfpg_au = dfp_au.groupby('SUPER_CHANNEL_DEFINITION')['TOT_VOLUME'].sum().reset_index()
            dfpg['per'] = dfpg['TOT_VOLUME']/np.sum(dfpg['TOT_VOLUME'])
            dfpg_au['per'] = dfpg_au['TOT_VOLUME']/np.sum(dfpg_au['TOT_VOLUME'])
            dfpg = dfpg.merge(dfpg_au, on='SUPER_CHANNEL_DEFINITION', how='inner', suffixes=('_filt','_AU'))
            dfpg['PRODUCT_INDEX'] = 100*(dfpg['per_filt'] - dfpg['per_AU'])+100
            dfpg = dfpg.sort_values(by='PRODUCT_INDEX', ascending=False)
            dfpg['OPPORTUNITY_VOLUME'] = dfpg['PRODUCT_INDEX']*dfpg['TOT_VOLUME_filt']/100
            dfpg['OPPORTUNITY_GROSSPROFITDEADNET'] = dfpg['PRODUCT_INDEX']*dfpg['TOT_GROSSPROFITDEADNET']/100
            kcols = ['SUPER_CHANNEL_DEFINITION','TOT_VOLUME_filt','TOT_GROSSPROFITDEADNET',
                     'PRODUCT_INDEX', 'OPPORTUNITY_VOLUME', 'OPPORTUNITY_GROSSPROFITDEADNET']
            dfpg = dfpg[kcols]
            dfpg.rename(columns = {'SUPER_CHANNEL_DEFINITION':'SUPER_CHANNEL','TOT_VOLUME_filt':'VOLUME','TOT_GROSSPROFITDEADNET':'GROSSPROFITDEADNET'}, inplace = True)

            st.markdown(':blue[Channel]')
            tab1, tab2, tab3 = st.tabs(["Data","Plot","CSV"])
            format_mapping={'VOLUME': '{:,.0f}', 'GROSSPROFITDEADNET': '${:,.2f}', 'PRODUCT_INDEX':'{:.2f}', 'OPPORTUNITY_VOLUME':'{:,.0f}', 'OPPORTUNITY_GROSSPROFITDEADNET':'${:,.2f}'}
            tab1.table(dfpg.style.format(format_mapping))
            fig = indexplot('SUPER_CHANNEL','OPPORTUNITY_GROSSPROFITDEADNET','PRODUCT_INDEX',dfpg)
            tab2.plotly_chart(fig, use_container_width=True)
            csv = convert_df(dfpg)
            tab3.download_button(label="_Download CSV_",data=csv,file_name='WHAT_WHO_CHANNEL.csv',mime='text/csv')

            st.markdown(':blue[Clusters]')
            cluster_types = [i for i in list(dfc.columns) if i != 'Zip'] 
            cluster_type = st.selectbox('Select cluster type', cluster_types)
            show_cluster_by_type(cluster_type)
 
            st.subheader(':blue[**What are the key consumer attributes in a given cluster?**]')
            col1, col2 = st.columns(2)
            vec = [dfc[col_name].unique() for col_name in cluster_types]  # filter by cluster type
            show_clusters = [num for elem in vec for num in elem]
            cluster_select = col1.multiselect('Select Cluster', show_clusters)
            col2.markdown('**NOTE:** _You may want to select cluster(s) where your selected products are over-indexed(>100) and/or have larger opportunity from above_')

            if(len(cluster_select)>0):
                zips = list(dfc[dfc.isin(cluster_select).sum(axis=1) > 0]['Zip'].values)  # zips for filtered clusters
                dfi = dfi[dfi['Zip'].isin(zips)]

            st.markdown(':blue[Income]')
            #col1, col2 = st.columns([3,1])
            #with col1:
            dfiginc = show_demographics(dfi, dfi_au, 'Income')
            #with col2:
            #inc_select = st.multiselect('_Optional: Save Income Group_',['All']+list(dfiginc['Consumer_Criteria'].unique()))
            inc_select = dfiginc.loc[dfiginc['Save Selection']==True]['Consumer_Criteria'].tolist()

            st.markdown(':blue[Lifestyle]')
            dfiglif = show_demographics(dfi, dfi_au, 'Lifestyle')
            lif_select = dfiglif.loc[dfiglif['Save Selection']==True]['Consumer_Criteria'].tolist()

            st.markdown(':blue[Employment]')
            dfigemp = show_demographics(dfi, dfi_au, 'Employment')
            emp_select = dfigemp.loc[dfigemp['Save Selection']==True]['Consumer_Criteria'].tolist()

            st.markdown(':blue[Age]')
            dfigage = show_demographics(dfi, dfi_au, 'Age')
            age_select = dfigage.loc[dfigage['Save Selection']==True]['Consumer_Criteria'].tolist()

            st.markdown(':blue[Ethnicity]')
            dfigeth = show_demographics(dfi, dfi_au, 'Ethnicity')
            eth_select = dfigeth.loc[dfigeth['Save Selection']==True]['Consumer_Criteria'].tolist()

            st.markdown(':blue[Size of HH]')
            dfighhs = show_demographics(dfi, dfi_au, 'Size of HH')
            hhs_select = dfighhs.loc[dfighhs['Save Selection']==True]['Consumer_Criteria'].tolist()

            st.markdown(':blue[Marital Status]')
            dfigmar = show_demographics(dfi, dfi_au, 'Marital Status')
            mar_select = dfigmar.loc[dfigmar['Save Selection']==True]['Consumer_Criteria'].tolist()

            st.markdown(':blue[Gender]')
            dfiggen = show_demographics(dfi, dfi_au, 'Gender')
            gen_select = dfiggen.loc[dfiggen['Save Selection']==True]['Consumer_Criteria'].tolist()
            
            st.markdown('**Save Selections**')
            dfss = pd.DataFrame({"Parameter" : ["Material Description","IC of FC","Regular or Low Calorie","Package Size","Package Type","Brand Description","Product Description","Clusters","Income","Lifestyle","Employment","Age","Ethnicity","Size of HH","Marital Status","Gender"], 
                     "Selection" : pd.Series([mat_desc_select,ic_fc_select,cal_cat_select,pkg_size_select,pkg_type_select,brand_desc_select,bev_desc_select,cluster_select,inc_select,lif_select,emp_select,age_select,eth_select,hhs_select,mar_select,gen_select],
                                             dtype='str')})
            
            st.table(dfss)
            #use_container_width=True
            @st.cache_data
            def convert_df(df):
                return df.to_csv().encode('utf-8')

            csv = convert_df(dfss)

            st.download_button(
            label="Download Selections as CSV",
            data=csv,
            file_name='WHAT_WHO_SELECTIONS.csv',
            mime='text/csv',
            )
            
 ######################################################################################################################
           
 