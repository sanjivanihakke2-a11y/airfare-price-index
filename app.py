import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# Page setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Airfare Price Index India",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ Airfare Price Index for India")
st.caption(
    "BCA Final Year Project | Airfare Price Monitoring "
    "and Price Index Analysis"
)

with st.expander("About This Project"):
    st.write(
        "This dashboard analyzes flight fare records across routes and dates. "
        "It summarizes fares, compares route-level changes, and displays a "
        "sample airfare price index."
    )
    st.info(
        "This project uses sample data unless a CSV is uploaded. "
        "It does not show live airline prices and is not an official NSO/CPI index."
    )

st.markdown(
    """
    ### Indian Domestic Flight Fare Analytics

    Track airfare trends, compare routes, and analyze fare changes
    using sample data or your own CSV file.
    """
)
st.divider()

# ---------------------------------------------------------
# Sample data
# ---------------------------------------------------------
sample_data = {
    "Date": [
        "2026-10-01", "2026-10-02", "2026-10-03",
        "2026-10-01", "2026-10-02", "2026-10-03",
        "2026-10-01", "2026-10-02", "2026-10-03",
    ],
    "Route": [
        "Mumbai-Delhi", "Mumbai-Delhi", "Mumbai-Delhi",
        "Pune-Bengaluru", "Pune-Bengaluru", "Pune-Bengaluru",
        "Delhi-Bengaluru", "Delhi-Bengaluru", "Delhi-Bengaluru",
    ],
    "Fare": [
        4500, 4800, 5100,
        3800, 4000, 3900,
        5200, 5000, 5500,
    ],
}

# ---------------------------------------------------------
# Upload data
# ---------------------------------------------------------
st.subheader("1. Upload Airfare Data")
uploaded_file = st.file_uploader(
    "Upload a CSV file with Date, Route and Fare columns",
    type=["csv"],
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()

        required_columns = {"Date", "Route", "Fare"}
        if not required_columns.issubset(df.columns):
            st.error("CSV must contain these columns: Date, Route, Fare.")
            st.stop()

        df = df[["Date", "Route", "Fare"]].copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Route"] = df["Route"].astype("string").str.strip()
        df["Fare"] = pd.to_numeric(df["Fare"], errors="coerce")
        df = df.dropna(subset=["Date", "Route", "Fare"])
        df = df[(df["Route"] != "") & (df["Fare"] > 0)].copy()

        if df.empty:
            st.error("No valid rows found. Please check your CSV data.")
            st.stop()

        st.success(f"Successfully loaded {len(df)} valid records.")

    except Exception as error:
        st.error(f"Could not read the CSV file: {error}")
        st.stop()
else:
    df = pd.DataFrame(sample_data)
    df["Date"] = pd.to_datetime(df["Date"])
    st.caption("Showing built-in sample data.")

# Sort records by date before filters and comparisons
df = df.sort_values("Date").copy()

# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("Dashboard Filters")
st.sidebar.subheader("Select Date Range")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Choose start and end dates",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    date_filtered_df = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
    ].copy()
else:
    # The date picker may temporarily contain only one date.
    date_filtered_df = df.copy()

if date_filtered_df.empty:
    st.warning("No records found for this date range. Choose another range.")
    st.stop()

st.sidebar.subheader("Select Route")
routes = ["All Routes"] + sorted(date_filtered_df["Route"].unique().tolist())
selected_route = st.sidebar.selectbox("Choose Flight Route", routes)

if selected_route == "All Routes":
    filtered_df = date_filtered_df.copy()
else:
    filtered_df = date_filtered_df[
        date_filtered_df["Route"] == selected_route
    ].copy()

if filtered_df.empty:
    st.warning("No records found for the selected route and date range.")
    st.stop()

# ---------------------------------------------------------
# Calculate sample price index
# Base fare = first available fare for each route in selected date range
# ---------------------------------------------------------
base_fares = (
    date_filtered_df.sort_values("Date")
    .groupby("Route")["Fare"]
    .first()
    .to_dict()
)

filtered_df["Base Fare"] = filtered_df["Route"].map(base_fares)
filtered_df["Price Index"] = (
    filtered_df["Fare"] / filtered_df["Base Fare"] * 100
).round(2)

# ---------------------------------------------------------
# Dashboard overview and summary
# ---------------------------------------------------------
st.subheader("2. Dashboard Overview")
total_records = len(filtered_df)
total_routes = filtered_df["Route"].nunique()

col1, col2 = st.columns(2)
col1.metric("Total Fare Records", total_records)
col2.metric("Total Routes", total_routes)

st.subheader("3. Airfare Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Average Fare", f"₹{filtered_df['Fare'].mean():,.0f}")
col2.metric("Lowest Fare", f"₹{filtered_df['Fare'].min():,.0f}")
col3.metric("Highest Fare", f"₹{filtered_df['Fare'].max():,.0f}")

# ---------------------------------------------------------
# Fare trend chart
# ---------------------------------------------------------
st.subheader("4. Fare Trend")
fig_trend = px.line(
    filtered_df,
    x="Date",
    y="Fare",
    color="Route",
    markers=True,
    title="Flight Fare Trend Over Time",
    labels={
        "Date": "Travel Date",
        "Fare": "Fare (₹)",
        "Route": "Flight Route",
    },
)
st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------------------------------
# Price index chart
# ---------------------------------------------------------
st.subheader("5. Airfare Price Index Trend")
st.caption("Sample index: first fare for each route in the selected date range = 100.")

fig_index = px.line(
    filtered_df,
    x="Date",
    y="Price Index",
    color="Route",
    markers=True,
    title="Airfare Price Index Over Time",
    labels={
        "Date": "Date",
        "Price Index": "Price Index (Base = 100)",
        "Route": "Flight Route",
    },
)
st.plotly_chart(fig_index, use_container_width=True)

# ---------------------------------------------------------
# Fare change status by route
# Compare first and latest fare for each route in selected date range
# ---------------------------------------------------------
st.subheader("6. Fare Change Status")

status_rows = []
for route, route_data in date_filtered_df.sort_values("Date").groupby("Route"):
    fares = route_data["Fare"].tolist()
    first_fare = fares[0]
    latest_fare = fares[-1]
    change = latest_fare - first_fare

    if len(fares) < 2:
        status = "Not enough data"
    elif change > 0:
        status = "Increased"
    elif change < 0:
        status = "Decreased"
    else:
        status = "Unchanged"

    status_rows.append(
        {
            "Route": route,
            "First Fare (₹)": first_fare,
            "Latest Fare (₹)": latest_fare,
            "Fare Change (₹)": change,
            "Status": status,
        }
    )

status_df = pd.DataFrame(status_rows)
if selected_route != "All Routes":
    status_df = status_df[status_df["Route"] == selected_route].copy()
st.dataframe(status_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# Route-wise average fare chart
# This uses all routes in the selected date range, independent of route filter.
# ---------------------------------------------------------
st.subheader("7. Route-wise Average Fare")
route_avg = (
    date_filtered_df.groupby("Route", as_index=False)["Fare"]
    .mean()
)
route_avg["Fare"] = route_avg["Fare"].round(2)

fig_avg = px.bar(
    route_avg,
    x="Route",
    y="Fare",
    title="Average Fare by Flight Route",
    labels={"Route": "Flight Route", "Fare": "Average Fare (₹)"},
    text="Fare",
)
fig_avg.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
st.plotly_chart(fig_avg, use_container_width=True)

# ---------------------------------------------------------
# Route-wise fare statistics
# ---------------------------------------------------------
st.subheader("8. Route-wise Fare Statistics")
route_stats = (
    date_filtered_df.groupby("Route")
    .agg(
        Total_Records=("Fare", "count"),
        Average_Fare=("Fare", "mean"),
        Minimum_Fare=("Fare", "min"),
        Maximum_Fare=("Fare", "max"),
    )
    .reset_index()
)
route_stats["Average_Fare"] = route_stats["Average_Fare"].round(2)

if selected_route != "All Routes":
    route_stats = route_stats[route_stats["Route"] == selected_route].copy()

st.dataframe(route_stats, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# Fare change bar chart
# ---------------------------------------------------------
st.subheader("9. Fare Change by Route")
fare_change_data = status_df.copy()

if not fare_change_data.empty:
    fig_change = px.bar(
        fare_change_data,
        x="Route",
        y="Fare Change (₹)",
        color="Status",
        title="Fare Increase or Decrease by Route",
        labels={
            "Route": "Flight Route",
            "Fare Change (₹)": "Fare Change (₹)",
            "Status": "Status",
        },
        text="Fare Change (₹)",
    )
    st.plotly_chart(fig_change, use_container_width=True)
else:
    st.info("No route fare changes are available for the selected filters.")

# ---------------------------------------------------------
# Records table
# ---------------------------------------------------------
st.subheader("10. Airfare Records")
display_df = filtered_df.copy()
display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
st.dataframe(display_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# Download buttons
# ---------------------------------------------------------
st.subheader("11. Download Reports")

filtered_csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Fare Data",
    data=filtered_csv,
    file_name="filtered_airfare_data.csv",
    mime="text/csv",
)

route_csv = route_avg.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Route-wise Fare Report",
    data=route_csv,
    file_name="route_wise_fare_report.csv",
    mime="text/csv",
)

stats_csv = route_stats.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Route Statistics",
    data=stats_csv,
    file_name="route_fare_statistics.csv",
    mime="text/csv",
)

st.caption(
    "Project note: Results depend on the supplied/sample data. "
    "The displayed price index is illustrative and is not an official CPI measure."
)
