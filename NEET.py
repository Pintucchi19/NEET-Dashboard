import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="Participation in Education, Training and Employment",
    layout="wide"
)

st.title(
    "Participation in Education, Training and Employment Age 16 to 21"
)

# Load data
BASE_DIR = Path(__file__).parent

neet = pd.read_csv(
    BASE_DIR / "Data" / "state_participation_LA_chars_0406.zip",
    compression="zip"
)

########## Create Year column ########
neet["Year"] = neet["time_period"].astype(int)
neet["percent"] = pd.to_numeric(
    neet["percent"],
    errors="coerce"
)

########## Local Authority Groups########################################
statistical_neighbours = [
    "Barnet",
    "Croydon",
    "Ealing",
    "Haringey",
    "Harrow",
    "Hillingdon",
    "Hounslow",
    "Lewisham",
    "Redbridge",
    "Southampton"
]

neet["LocalAuthority"] = np.select(
    [
        neet["la_name"].isin(statistical_neighbours),
        neet["la_name"] == "Waltham Forest",
        neet["la_name"].isna() & (neet["region_name"] == "London"),
        neet["la_name"].isna() & neet["region_name"].isna()
    ],
    [
        "Statistical Neighbours",
        "Waltham Forest",
        "London",
        "England"
    ],
    default="Other"
)
####################Colours for the charts#########################
COLOURS = {
    "Waltham Forest": "#00977C",
    "Statistical Neighbours": "#80225F",
    "London": "#693F23",
    "England": "#002D72"
}

############################################################################################

######## CHART 1 - NEET by SEX ################### 

st.subheader ("Not in Education or Apprenticeships by Sex")

# Filter sex 
neet_sex = neet[
    (neet["breakdown_topic"] == "Sex") &
    (neet["participation_measure"] == "Not in Education or Apprenticeships")
]

col1, col2 = st.columns([1,1])

with col1:

    selected_sex = st.selectbox(
        "Sex",
        sorted(neet_sex["breakdown"].dropna().unique()),
        key="sex_filter"
    )

with col2:

    selected_age = st.selectbox(
        "Age",
        sorted(neet_sex["age"].dropna().unique()),
        key="age_filter"
    )

chart_filter = neet_sex[
    (neet_sex['breakdown'] == selected_sex) &
    (neet_sex["age"] == selected_age)
    ]

# Waltham Forest, London and England
main_groups = (
    chart_filter[
        chart_filter["LocalAuthority"].isin(
            ["Waltham Forest", "London", "England"]
        )
    ]
    [["Year", "LocalAuthority", "percent"]]
)

# Statistical Neighbours Average
sn_group = (
    chart_filter[
        chart_filter["LocalAuthority"] == "Statistical Neighbours"
    ]
    .groupby("Year", as_index=False)["percent"]
    .mean()
)

sn_group["LocalAuthority"] = "Statistical Neighbours"

# Combine together
chart_data_sex = pd.concat(
    [main_groups, sn_group],
    ignore_index=True
)

fig = px.line(
    chart_data_sex,
    x="Year",
    y="percent",
    color="LocalAuthority",
    markers=True,
    color_discrete_map= COLOURS
)

fig.update_yaxes(
    ticksuffix="%",
    tickformat=".1f"
)

fig.update_traces(
    hovertemplate="%{y:.1f}%<extra></extra>"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
