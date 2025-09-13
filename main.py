import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Car Data Dashboard")


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Loads and preprocesses data from a public URL.
    """
    data_file = "cars.json"
    try:
        df = pd.read_json(data_file)

        # Rename columns to be more descriptive for a car dashboard
        df = df.rename(
            columns={
                "Name": "Car Name",
                "Miles_per_Gallon": "MPG",
                "Displacement": "Displacement",
                "Weight_in_lbs": "Weight",
                "Cylinders": "Cylinders",
                "Horsepower": "Horsepower",
            }
        )

        df = df.dropna()

        # Convert cylinders to a string category for better filtering
        df["Cylinders"] = df["Cylinders"].astype(str)

    except Exception as e:
        st.error(f"Error loading data: {e}. Please check the data source.")
        return pd.DataFrame()

    return df


df = load_data()

if df.empty:
    st.stop()

st.title("🚗 Car Data Dashboard")
st.markdown(
    """
This is a simple dashboard built with Streamlit to showcase key metrics and insights
from a sample car dataset. Use the filters on the sidebar to explore the data interactively.
"""
)

st.sidebar.header("Filter Cars")

categories = sorted(df["Cylinders"].unique())
selected_categories = st.sidebar.multiselect(
    "Select Number of Cylinders:", options=categories, default=categories
)

price_range = st.sidebar.slider(
    "Select Displacement Range:",
    min_value=float(df["Displacement"].min()),
    max_value=float(df["Displacement"].max()),
    value=(float(df["Displacement"].min()), float(df["Displacement"].max())),
)

rating_range = st.sidebar.slider(
    "Select MPG Range:",
    min_value=float(df["MPG"].min()),
    max_value=float(df["MPG"].max()),
    value=(float(df["MPG"].min()), float(df["MPG"].max())),
)

filtered_df = df[
    (df["Cylinders"].isin(selected_categories))
    & (df["Displacement"] >= price_range[0])
    & (df["Displacement"] <= price_range[1])
    & (df["MPG"] >= rating_range[0])
    & (df["MPG"] <= rating_range[1])
]

st.header("Key Performance Indicators")
col1, col2, col3 = st.columns(3)

total_products = len(filtered_df)
avg_mpg = round(filtered_df["MPG"].mean(), 2) if not filtered_df.empty else 0
avg_displacement = (
    round(filtered_df["Displacement"].mean(), 2) if not filtered_df.empty else 0
)

with col1:
    st.metric(label="Total Cars", value=f"{total_products:,}")
with col2:
    st.metric(label="Average MPG", value=avg_mpg)
with col3:
    st.metric(label="Average Displacement", value=avg_displacement)

if total_products == 0:
    st.warning("No cars match the selected filters. Please adjust your selections.")
else:
    st.header("Car Insights")
    st.markdown(
        "Use the charts below to understand car distribution and relationships."
    )

    st.subheader("Cars by Number of Cylinders")
    category_counts = filtered_df.groupby("Cylinders").size().reset_index(name="Count")
    fig1 = px.bar(
        category_counts,
        x="Cylinders",
        y="Count",
        title="Number of Cars by Cylinders",
        color="Cylinders",
        labels={"Count": "Number of Cars", "Cylinders": "Number of Cylinders"},
        template="plotly_white",
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Displacement vs. MPG")
    fig2 = px.scatter(
        filtered_df,
        x="Displacement",
        y="MPG",
        color="Cylinders",
        hover_data=["Car Name", "Displacement", "MPG"],
        title="Displacement vs. Miles per Gallon",
        labels={"Displacement": "Displacement", "MPG": "Miles per Gallon"},
        template="plotly_white",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Distribution of MPG")
    fig3 = px.histogram(
        filtered_df,
        x="MPG",
        nbins=20,
        title="Distribution of Miles per Gallon",
        labels={"MPG": "Miles per Gallon", "count": "Number of Cars"},
        template="plotly_white",
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.header("Filtered Cars Table")
    st.dataframe(filtered_df)
