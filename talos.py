import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go

# Fetching data from the URL
url = "https://liberal-donkey.dataos.app/talos/public:pod-usage-data/api/feasiblitydata"

headers = {
    'Authorization': 'Bearer dG9rZW5fc3VyZWx5X2hhcmRseV91cF93aGFsZS4yYzgzZDdlYy1mODRjLTQ0YjQtYTUzZS1jN2Q3ZmVjMjJmOGI='
}

response = requests.get(url, headers=headers)
data = response.json()

# Check if the data is a list of dictionaries
if isinstance(data, list) and all(isinstance(item, dict) for item in data):
    # Convert to DataFrame
    df = pd.DataFrame(data)
else:
    st.error("Unexpected data format")
    st.stop()

# Ensure the expected columns are present
expected_columns = ['lens_name', 'event_date', 'resources_usage', 'resources_request', 'utlization_percentage']
if not all(column in df.columns for column in expected_columns):
    missing_columns = [column for column in expected_columns if column not in df.columns]
    st.error(f"Missing columns in the DataFrame: {missing_columns}")
    st.stop()

# Convert event_date to datetime
df['event_date'] = pd.to_datetime(df['event_date'])

# Format utilization percentage to 2 decimal places
df['utlization_percentage'] = df['utlization_percentage'].round(2)

# Streamlit app
st.set_page_config(page_title="DP Resource Utilisation App", layout="wide")
st.title("📊 DP Resource Utilisation App")

# Sidebar filters
st.sidebar.header("Filter Options")
lens_name = st.sidebar.selectbox("Select DP Name", df['lens_name'].unique())
filtered_df = df[df['lens_name'] == lens_name]
event_dates = st.sidebar.multiselect("Select Event Dates", filtered_df['event_date'].dt.strftime('%Y-%m-%d').unique(), default=filtered_df['event_date'].dt.strftime('%Y-%m-%d').unique())

# Filter dataframe based on selected event_date
filtered_df = filtered_df[filtered_df['event_date'].dt.strftime('%Y-%m-%d').isin(event_dates)]

# Display filtered data
st.subheader(f"Resources Usage Info for {lens_name}")
st.write(filtered_df)

# Check for utilization percentage alerts and provide suggestions
alert_df = filtered_df[(filtered_df['utlization_percentage'] > 50) | (filtered_df['utlization_percentage'] < -50)]
if not alert_df.empty:
    for _, row in alert_df.iterrows():
        utilization = row['utlization_percentage']
        alert_message = f"Alert: Utilization percentage for {row['lens_name']} on {row['event_date'].strftime('%Y-%m-%d')} is {utilization}%."
        
        # Suggestion based on utilization percentage
        if utilization > 50:
            suggestion = "Please scale up your resources."
        elif utilization < -50:
            suggestion = "Please scale down your resources."
        
        st.error(f"{alert_message} {suggestion}")

# Plotting resource usage vs. request with Plotly
fig = go.Figure()

# Adding traces for resource usage and request
fig.add_trace(go.Scatter(x=filtered_df['event_date'].dt.strftime('%Y-%m-%d'), y=filtered_df['resources_usage'], mode='lines+markers', name='Resources Usage'))
fig.add_trace(go.Scatter(x=filtered_df['event_date'].dt.strftime('%Y-%m-%d'), y=filtered_df['resources_request'], mode='lines+markers', name='Resources Request'))

fig.update_layout(title='Resource Usage vs Request Over Time', xaxis_title='Event Date', yaxis_title='Resources', template='plotly_dark')

st.plotly_chart(fig)

# Additional styling
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    .reportview-container .main .block-container{
        padding-top: 2rem;
        background: black;
    }
    .reportview-container .main {
        background: black;
    }
    .css-18e3th9 {
        background-color: black;
    }
    .css-1d391kg {
        background-color: black;
    }
    .css-qrbaxs {
        background-color: black;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
    <style>
    .sidebar .sidebar-content {
        padding: 20px;
    }
    .sidebar .sidebar-content .block-container {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
