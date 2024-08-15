import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
import emoji
import json
import json
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import streamlit as st
import streamlit as st
import plotly.graph_objects as go
import base64
import streamlit as st
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt





# Preprocess data
def preprocess_data():
    df1 = pd.read_excel('combined_winners_2.xlsx', engine='openpyxl')
    df2 = pd.read_excel('regionMaster (1).xlsx', engine='openpyxl')
    party_hex_dict = {
        'Bharatiya Janata Party': ['NDA', '#f58345'],
        'Apna Dal (Soneylal)': ['NDA', '#f9a870'],
        'Rashtriya Lok Dal': ['NDA', '#f9a870'],
        'Suheldev Bharatiya Samaj Party': ['NDA', '#f9a870'],
        'Nirbal Indian Shoshit Hamara Aam Dal': ['NDA', '#f9a870'],
        'Shiv Sena': ['NDA', '#f9a870'],
        'Janata Dal (United)': ['NDA', '#f9a870'],
        'Amma Makkal Munnetra Kazhagam': ['NDA', '#f9a870'],
        'Janata Dal (Secular)': ['NDA', '#f9a870'],
        'Telugu Desam': ['NDA', '#f9a870'],
        'Indian National Congress': ['INDIA', '#00a2e0'],
        'Nationalist Congress Party (Sharadchandra Pawar)': ['INDIA', '#4ec9f5'],
        'Jharkhand Mukti Morcha': ['INDIA', '#4ec9f5'],
        'United Democratic Front': ['INDIA', '#4ec9f5'],
        'Samajwadi Party': ['INDIA', '#98d8e3'],
        'Shiv Sena (Uddhav Balasaheb Thackrey)': ['INDIA', '#98d8e3'],
        'Rashtriya Janata Dal': ['INDIA', '#98d8e3'],
        'All India Trinamool Congress': ['OTHERS', '#a6ce39'],
        'Aam Aadmi Party': ['OTHERS', '#6d3c97'],
        '(?)': ['(?)', 'lightgrey'],
        'Rest': ['OTHERS', 'lightgrey'],
    }
    data = [(party, values[0], values[1]) for party, values in party_hex_dict.items()]
    df = pd.DataFrame(data, columns=['Party Name', 'Alliance Name', 'Hex Code'])
    
    # Fix weird party names and merge data
    df1.loc[df1['Party Name'] == 'Nationalist Congress Party Ã¢â‚¬â€œ Sharadchandra Pawar', 'Party Name'] = 'Nationalist Congress Party (Sharadchandra Pawar)'
    df1.loc[df1['Party Name'] == 'United PeopleÃ¢â‚¬â„¢s Party, Liberal', 'Party Name'] = 'United People party'
    df1.loc[df1['Party Name'] == 'Zoram PeopleÃ¢â‚¬â„¢s Movement', 'Party Name'] = 'Zoram People Movement'
    merged_df = pd.merge(df1, df, on='Party Name', how='left')
    merged_df['Alliance Name'] = merged_df['Alliance Name'].fillna('OTHERS')
    merged_df['Total Assets'] = merged_df['Total Assets'].astype(str).str.replace('.', '', regex=False)
    merged_df['Total Assets'] = pd.to_numeric(merged_df['Total Assets'], errors='coerce')
    merged_df['Total Assets Cr'] = merged_df['Total Assets'] / 10000000
    return df1, df2, merged_df, df, party_hex_dict

df1, df2, merged_df, df, party_hex_dict = preprocess_data()

# Define each page function
def main_page(merged_df, df, party_color_dict):
    st.title("Main Page: Assets, Age, and Gender Distribution \U0001F680")
    
    # Assets visualization
    st.header('Treemap of Assets by Party and Alliance')
    treemap_data = merged_df[merged_df['Alliance Name'] != 'OTHERS'][['Candidate Name','Party Name', 'Alliance Name','Total Assets Cr']].copy()
    rest_total_assets = merged_df[merged_df['Alliance Name'] == 'OTHERS'][['Candidate Name','Party Name', 'Alliance Name','Total Assets Cr']].copy()
    treemap_data = pd.concat([treemap_data, rest_total_assets], ignore_index=True)
    color_map = {party: values[1] for party, values in party_hex_dict.items()}
    default_color = 'lightgrey'
    treemap_data['Color'] = treemap_data['Party Name'].apply(lambda x: color_map.get(x, default_color))
    party_color_dict = treemap_data.set_index('Party Name')['Color'].to_dict()
    fig = px.treemap(treemap_data, 
                     path=['Candidate Name'], 
                     values='Total Assets Cr',
                     color='Party Name',
                     color_discrete_map=party_color_dict,
                     title='Treemap of Assets by Party and Alliance')
    fig.update_layout(paper_bgcolor='white', width=1000, height=800)
    fig.update_traces(marker=dict(line=dict(color='black', width=1)), textinfo='label+value', textfont=dict(color='black'))
    # Generate SVG content
    svg_content = fig.to_image(format="svg")
    # Create a download button
    st.download_button(
        label="Download Treemap as SVG",
        data=svg_content,
        file_name="treemap.svg",
        mime="image/svg+xml"
    )

    st.plotly_chart(fig)

    
    # Gender distribution visualization
    st.header("Gender Distribution by Party")
    st.sidebar.header("Filter Options for Gender")
    st.sidebar.write("Use the options below to filter the data and visualize the gender distribution.")
    pie_chart_data = merged_df[merged_df['Alliance Name'] != 'OTHERS'][['Candidate Name','Party Name', 'Alliance Name','Gender']].copy()
    pie_chart_data = pie_chart_data.groupby(['Party Name','Alliance Name','Gender']).size().reset_index(name='Count')
    rest_data = merged_df[merged_df['Alliance Name'] == 'OTHERS'].groupby(['Party Name','Alliance Name', 'Gender']).size().reset_index(name='Count')
    combined_gender_counts = pd.concat([pie_chart_data, rest_data]).sort_values(by='Count', ascending=False)
    all_options = combined_gender_counts['Party Name'].unique().tolist()
    select_all_gender = st.sidebar.checkbox("Select All Parties", value=True, key='select_all_gender')
    remove_all_gender = st.sidebar.checkbox("Remove All Parties and Choose!", value=False, key='remove_all_gender')

    if select_all_gender and not remove_all_gender:
        selected_parties_gender = st.sidebar.multiselect("Select Parties", options=all_options, default=all_options, key='multiselect_gender')
    elif remove_all_gender:
        selected_parties_gender = st.sidebar.multiselect("Select Parties", options=all_options, default=[], key='multiselect_gender_empty')
    else:
        selected_parties_gender = st.sidebar.multiselect("Select Parties", options=all_options, default=all_options, key='multiselect_gender_normal')

    filtered_data_gender = combined_gender_counts[combined_gender_counts['Party Name'].isin(selected_parties_gender)]
    gender_distribution = filtered_data_gender.groupby('Gender')['Count'].sum().reset_index()
    fig = px.pie(gender_distribution, names='Gender', values='Count', color='Gender', title='Gender Distribution for Selected Parties', color_discrete_map={'M': 'lightcyan', 'F': 'pink'})
    svg_content = fig.to_image(format="svg")
    # Create a download button
    st.download_button(
        label="Download Piechart as SVG",
        data=svg_content,
        file_name="piechart.svg",
        mime="image/svg+xml"
    )
    st.plotly_chart(fig)
    st.write("Filtered Data:")
    st.dataframe(filtered_data_gender)
    
    # Age distribution visualization
    st.header("Age Distribution by Party")
    st.sidebar.header("Filter Options for Age")
    st.sidebar.write("Use the options below to filter the data and visualize the age distribution of winning parties.")
    bins = [0, 30, 35, 45, 50, float('inf')]
    labels = ['Below 30', '30-35', '35-45', '45-50', '50 and above']
    merged_df['Age Group'] = pd.cut(merged_df['Age'], bins=bins, labels=labels, right=False)
    rest_age_group = merged_df[merged_df['Alliance Name'] == 'OTHERS'][['Candidate Name', 'Party Name', 'Alliance Name', 'Age Group']].copy()
    bar_chart_data = merged_df[merged_df['Alliance Name'] != 'OTHERS'][['Candidate Name', 'Party Name', 'Alliance Name', 'Age Group']].copy()
    agegroup_merged = pd.concat([bar_chart_data, rest_age_group], ignore_index=True)
    combined_data = agegroup_merged.groupby(['Age Group','Party Name']).size().reset_index(name='Count')
    select_all_age = st.sidebar.checkbox("Select All Parties", value=True, key="select_all_age")
    remove_all_age = st.sidebar.checkbox("Remove All Parties and Choose!", value=False, key="remove_all_age")

    if select_all_age and not remove_all_age:
        selected_parties_age = st.sidebar.multiselect("Select Parties", options=combined_data['Party Name'].unique(), default=combined_data['Party Name'].unique(), key="multiselect_age")
    elif remove_all_age:
        selected_parties_age = st.sidebar.multiselect("Select Parties", options=combined_data['Party Name'].unique(), default=[], key="multiselect_age_empty")
    else:
        selected_parties_age = st.sidebar.multiselect("Select Parties", options=combined_data['Party Name'].unique(), default=combined_data['Party Name'].unique(), key="multiselect_age_normal")

    filtered_data_age = combined_data[combined_data['Party Name'].isin(selected_parties_age)]
    fig = px.bar(filtered_data_age, x='Age Group', y='Count', color='Party Name', color_discrete_map=party_color_dict, title='Age Distribution for Selected Parties', labels={'Age Group': 'Age Group', 'Count': 'Number of Candidates'}, barmode='group')
    fig.update_traces(hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>')
    fig.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
    svg_content = fig.to_image(format="svg")
    st.download_button(
        label="Download Barchart as SVG",
        data=svg_content,
        file_name="barchart.svg",
        mime="image/svg+xml"
    )
    st.plotly_chart(fig)
    st.write("Filtered Data:")
    st.dataframe(filtered_data_age)
 
def vote_share_page(df1, df2, merged_df, df, party_color_dict):
    st.title('Vote share and seat share') 
    st.header("Vote Share by Constituency")
    st.sidebar.header("Filter Options")
    st.sidebar.write("Use the options below to filter the data and visualize the voting share distribution.")

    df4 = pd.read_excel('EC_Result.xlsx')
    new_merged_df = pd.merge(df4, df, on='Party Name', how='left')
    new_merged_df['Alliance Name'] = new_merged_df['Alliance Name'].fillna('OTHERS')
    new_merged_df['Hex Code'] = new_merged_df['Hex Code'].fillna('lightgrey')
    votes_bar_chart = new_merged_df[['Candidate Name', 'Constituency Name', 'Party Name', 'Percent Votes','Hex Code']].copy()

    # Ensure 'Percent Votes' is numeric
    votes_bar_chart['Percent Votes'] = pd.to_numeric(votes_bar_chart['Percent Votes'], errors='coerce')

    select_all_constituencies = st.sidebar.checkbox("Select All Constituencies", value=True, key="select_all_constituencies")
    remove_all_constituencies = st.sidebar.checkbox("Remove All Constituencies and Choose!", value=False, key="remove_all_constituencies")

    if select_all_constituencies and not remove_all_constituencies:
        selected_constituencies = st.sidebar.multiselect("Select Constituencies", options=votes_bar_chart['Constituency Name'].unique(), default=votes_bar_chart['Constituency Name'].unique(), key="multiselect_constituencies_new")
    elif remove_all_constituencies:
        selected_constituencies = st.sidebar.multiselect("Select Constituencies", options=votes_bar_chart['Constituency Name'].unique(), default=[], key="multiselect_constituencies_empty")
    else:
        selected_constituencies = st.sidebar.multiselect("Select Constituencies", options=votes_bar_chart['Constituency Name'].unique(), default=votes_bar_chart['Constituency Name'].unique(), key="multiselect_constituencies_again")

    # Filter data based on selected constituencies
    filtered_data_constituencies = votes_bar_chart[votes_bar_chart['Constituency Name'].isin(selected_constituencies)]

    # Aggregate data by party
    aggregated_data = filtered_data_constituencies.groupby('Party Name').agg({
        'Percent Votes': 'sum',
        'Hex Code': 'first'  # Keep the color of the first occurrence
    }).reset_index()

    fig = px.pie(aggregated_data, 
             names='Party Name', 
             values='Percent Votes', 
             color='Party Name', 
             color_discrete_map=dict(zip(aggregated_data['Party Name'], aggregated_data['Hex Code'])),
             title='Vote share per constituency')

    fig.update_traces(
    textposition='inside',
    textinfo='percent',
    hovertemplate='<b>%{label}</b><br>Percentage: %{percent}<br>Votes: %{value}<extra></extra>'
    )
    fig.update_layout(
    uniformtext_minsize=8, 
    uniformtext_mode='hide'
    )
    svg_content = fig.to_image(format="svg")
    
    st.download_button(
        label="Download Piechart as SVG",
        data=svg_content,
        file_name="piechartforvoteshare.svg",
        mime="image/svg+xml"
    )
    st.plotly_chart(fig)

    st.write("Filtered Data:")
    st.dataframe(filtered_data_constituencies)

    # Seat Share
    pie_chart_data = merged_df[merged_df['Alliance Name'] != 'OTHERS'][['Party Name', 'Alliance Name']].copy()
    pie_chart_data = pie_chart_data.groupby(['Party Name', 'Alliance Name']).size().reset_index(name='Count')
    rest_data = merged_df[merged_df['Alliance Name'] == 'OTHERS'].groupby(['Party Name', 'Alliance Name']).size().reset_index(name='Count')

    combined_seat_counts = pd.concat([pie_chart_data, rest_data])
    combined_seat_counts = combined_seat_counts.sort_values(by='Count', ascending=False)

    threshold = 5.0
    significant_parties = combined_seat_counts[combined_seat_counts['Count'] >= threshold]
    less_significant_parties = combined_seat_counts[combined_seat_counts['Count'] < threshold]

    other_parties = pd.DataFrame({
        'Party Name': ['OTHERS'],
        'Alliance Name': ['OTHERS'],
        'Count': [less_significant_parties['Count'].sum()]
    })

    final_df = pd.concat([significant_parties, other_parties], ignore_index=True)
    final_df = pd.merge(final_df, df, on='Party Name', how='left')
    final_df['Hex Code'] = final_df['Hex Code'].fillna('lightgrey')
    final_df = final_df.drop('Alliance Name_y', axis=1)

    st.title("Seat Share")

    fig = px.pie(final_df, 
                 names='Party Name', 
                 values='Count', 
                 title='Seat share',
                 color='Party Name',
                 color_discrete_map=dict(zip(final_df['Party Name'], final_df['Hex Code']))
                 )
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Seat Share: %{value}<extra></extra>'
    )
    svg_content = fig.to_image(format="svg")
    st.download_button(
        label="Download Piechart as SVG",
        data=svg_content,
        file_name="seatsharebarchart.svg",
        mime="image/svg+xml"
    )

    # Display the pie chart in Streamlit
    st.plotly_chart(fig)

    # Vote Share Region Wise

    merged_final=pd.read_csv('merged_final.csv')

    st.title("Vote Share by Geographical Region, State, State Region, and Constituency")
    st.sidebar.header("Filter Options")
    st.sidebar.write("Use the options below to filter the data and visualize the voting share distribution.")

    # Step 1: Select Geographical Region
    all_regions = merged_final['Geographical region'].unique().tolist()
    select_all_regions = st.sidebar.checkbox("Select All Regions", value=True, key="select_all_regions")
    remove_all_regions = st.sidebar.checkbox("Remove All Regions and Choose!", value=False, key="remove_all_regions")

    if select_all_regions and not remove_all_regions:
        selected_regions = st.sidebar.multiselect("Select Geographical Region", options=all_regions, default=all_regions, key="multiselect_regions")
    elif remove_all_regions:
        selected_regions = st.sidebar.multiselect("Select Geographical Region", options=all_regions, default=[], key="multiselect_regions_empty")
    else:
        selected_regions = st.sidebar.multiselect("Select Geographical Region", options=all_regions, default=all_regions, key="multiselect_regions_normal")

    # Filter data based on selected regions
    filtered_data_region = merged_final[merged_final['Geographical region'].isin(selected_regions)] if selected_regions else merged_final
    merged_final=pd.merge(merged_final,df, on='Party Name',how='left')
    merged_final['Hex Code']=merged_final['Hex Code'].fillna('lightgrey')

    # Step 2: Select State within the selected regions
    all_states = filtered_data_region['State'].unique().tolist()
    select_all_states = st.sidebar.checkbox("Select All States", value=True, key="select_all_states")
    remove_all_states = st.sidebar.checkbox("Remove All States and Choose!", value=False, key="remove_all_states")

    if select_all_states and not remove_all_states:
        selected_states = st.sidebar.multiselect("Select State", options=all_states, default=all_states, key="multiselect_states")
    elif remove_all_states:
        selected_states = st.sidebar.multiselect("Select State", options=all_states, default=[], key="multiselect_states_empty")
    else:
        selected_states = st.sidebar.multiselect("Select State", options=all_states, default=all_states, key="multiselect_states_normal")

    # Filter data based on selected states
    filtered_data_state = filtered_data_region[filtered_data_region['State'].isin(selected_states)] if selected_states else filtered_data_region

    # Step 3: Select State Region within the selected states and regions
    all_state_regions = filtered_data_state['State REGION'].unique().tolist()
    select_all_state_regions = st.sidebar.checkbox("Select All State Regions", value=True, key="select_all_state_regions")
    remove_all_state_regions = st.sidebar.checkbox("Remove All State Regions and Choose!", value=False, key="remove_all_state_regions")

    if select_all_state_regions and not remove_all_state_regions:
        selected_state_regions = st.sidebar.multiselect("Select State Region", options=all_state_regions, default=all_state_regions, key="multiselect_state_regions")
    elif remove_all_state_regions:
        selected_state_regions = st.sidebar.multiselect("Select State Region", options=all_state_regions, default=[], key="multiselect_state_regions_empty")
    else:
        selected_state_regions = st.sidebar.multiselect("Select State Region", options=all_state_regions, default=all_state_regions, key="multiselect_state_regions_normal")

    # Filter data based on selected state regions
    filtered_data_state_region = filtered_data_state[filtered_data_state['State REGION'].isin(selected_state_regions)] if selected_state_regions else filtered_data_state

    # Step 4: Select Constituency within the selected state regions
    all_constituencies = filtered_data_state_region['Constituency Name'].unique().tolist()
    select_all_constituencies = st.sidebar.checkbox("Select All Constituencies", value=True, key="select_all_constituencies_1")
    remove_all_constituencies = st.sidebar.checkbox("Remove All Constituencies and Choose!", value=False, key="remove_all_constituencies_1")

    if select_all_constituencies and not remove_all_constituencies:
        selected_constituencies = st.sidebar.multiselect("Select Constituency", options=all_constituencies, default=all_constituencies, key="multiselect_constituencies_1")
    elif remove_all_constituencies:
        selected_constituencies = st.sidebar.multiselect("Select Constituency", options=all_constituencies, default=[], key="multiselect_constituencies_empty_1")
    else:
        selected_constituencies = st.sidebar.multiselect("Select Constituency", options=all_constituencies, default=all_constituencies, key="multiselect_constituencies_normal_1")

    # Filter data based on selected constituencies
    filtered_data_constituency = filtered_data_state_region[filtered_data_state_region['Constituency Name'].isin(selected_constituencies)] if selected_constituencies else filtered_data_state_region

    # Create a pie chart for vote share distribution
    fig = px.pie(filtered_data_constituency,
                 names='Party Name',
                 values='Percent Votes',
                 color='Party Name',
                 title='Vote Share for Selected Filters',
                 color_discrete_map=dict(zip(merged_final['Party Name'], merged_final['Hex Code'])))

    
    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    svg_content = fig.to_image(format="svg")
    st.download_button(
        label="Download Piechart as SVG",
        data=svg_content,
        file_name="numerousvoteshare.svg",
        mime="image/svg+xml"
    )
    st.plotly_chart(fig)
    

    st.write("Filtered Data:")
    st.dataframe(filtered_data_constituency)



def capitalize_properly(s):
    return ' '.join(word.capitalize() for word in s.split())



def map_visualisation():
    with open('india_pc_2019 (3).json',encoding='utf8') as f:
        geojson_data = json.load(f)
    for feature in geojson_data['features']:
        st_name = feature['properties']['st_name']
        pc_no = feature['properties']['pc_no']
        unique_id = f"{st_name}-{pc_no}"
        feature['properties']['unique_id'] = unique_id

    # Save the modified GeoJSON data back to a file
    with open('india_pc_2019 (3).json', 'w') as f:
        json.dump(geojson_data, f, indent=2)
    with open('india_pc_2019 (3).json') as f:
        geojson_data = json.load(f)
    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
    election_results = pd.read_csv('Indiamap_merged.csv')

    replacements = {
        'NCT Of Delhi': 'Delhi',
        'Odisha': 'Orissa'
    }

    # Iterate over the DataFrame using iloc and apply the replacements
    for i in range(len(election_results)):
        state_name = election_results.iloc[i]['STATE NAME']
        if state_name in replacements:
            election_results.iloc[i, election_results.columns.get_loc('STATE NAME')] = replacements[state_name]



    merged_gdf = gdf.merge(election_results, left_on='unique_id', right_on='unique_id',how='right')
    for feature in geojson_data['features']:
        unique_id = feature['properties']['unique_id']
        matching_rows = merged_gdf[merged_gdf['unique_id'] == unique_id]
    
        if not matching_rows.empty:
            print(unique_id)
            matching_row = matching_rows.iloc[0]
            feature['properties']['Party Name'] = matching_row['Party Name']

    with open('india_pc_2019 (3)', 'w') as f:
        json.dump(geojson_data, f, indent=2)
    
    color_mapping = dict(zip(election_results['Party Name'], election_results['Hex Code']))

    # Function to color constituencies based on the winning party
    def get_color(party):
        return color_mapping.get(party, 'gray')  # Default to gray if party not found
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5) #Indias loc
    folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
    'fillColor':get_color(feature['properties'].get('Party Name', '')) ,
    'color': 'black',
    'weight': 0.5,
    'fillOpacity': 0.7,
    },
    tooltip=folium.GeoJsonTooltip(fields=['pc_name', 'Party Name'], aliases=['Constituency:', 'Winning Party:'])
    ).add_to(m)

    merged_gdf['color'] = merged_gdf['Party Name'].map(get_color)
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))
    merged_gdf.boundary.plot(ax=ax, linewidth=0.5,color='black')
    merged_gdf.plot(column='color', ax=ax, color=merged_gdf['color'], legend=True)
    # Save as SVG
    svg_file = 'map.svg'
    fig.savefig(svg_file, format='svg')


    # Display the map in Streamlit
    st.title("Indian Election Results Map")
    with open(svg_file, "rb") as f:
        st.download_button(
        label="Download SVG for map",
        data=f,
        file_name="map.svg",
        mime="image/svg+xml"
    )
    folium_static(m)

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Main Page \U0001F4CA", "Vote Share \U0001F4CD", "Other Visualizations \U0001F4C8"])

# Display the selected page
if page == "Main Page \U0001F4CA":
    main_page(merged_df, df, party_hex_dict)
elif page == "Vote Share \U0001F4CD":
    vote_share_page(df1, df2, merged_df, df, party_hex_dict)
elif page == "Other Visualizations \U0001F4C8":
    map_visualisation()
