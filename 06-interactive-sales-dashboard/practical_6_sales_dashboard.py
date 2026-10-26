
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# 1. CREATE SAMPLE DATA
rng = np.random.default_rng(42)
n = 5000

df = pd.DataFrame({
    "date": pd.Timestamp("2025-01-01") +
            pd.to_timedelta(rng.integers(0, 365, n), unit="D"),
    "region": rng.choice(["North", "South", "East", "West"], n),
    "category": rng.choice(
        ["Electronics", "Clothing", "Home", "Sports"], n
    ),
    "units": rng.integers(1, 10, n),
    "unit_price": rng.uniform(10, 200, n).round(2)
})

df["revenue"] = df["units"] * df["unit_price"]

# 2. CREATE DASH APP
app = Dash(__name__)

CARD = {
    "backgroundColor": "white",
    "padding": "18px",
    "borderRadius": "10px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
    "flex": "1",
    "minWidth": "150px"
}

# 3. DASHBOARD LAYOUT
app.layout = html.Div(
    style={
        "fontFamily": "Arial",
        "backgroundColor": "#F4F6F9",
        "padding": "25px"
    },
    children=[
        html.H1(
            "Sales Analytics Dashboard",
            style={"textAlign": "center", "color": "#243447"}
        ),

        html.P(
            "Interactive Sales Performance Analysis",
            style={"textAlign": "center"}
        ),

        html.Div(
            style={
                "display": "flex",
                "gap": "20px",
                "flexWrap": "wrap",
                "marginBottom": "20px"
            },
            children=[
                html.Div([
                    html.Label("Select Region"),
                    dcc.Dropdown(
                        id="region-filter",
                        options=[
                            {"label": r, "value": r}
                            for r in sorted(df["region"].unique())
                        ],
                        value=sorted(df["region"].unique()),
                        multi=True
                    )
                ], style={"flex": "1", "minWidth": "200px"}),

                html.Div([
                    html.Label("Select Category"),
                    dcc.Dropdown(
                        id="category-filter",
                        options=[
                            {"label": c, "value": c}
                            for c in sorted(df["category"].unique())
                        ],
                        value=sorted(df["category"].unique()),
                        multi=True
                    )
                ], style={"flex": "1", "minWidth": "200px"}),

                html.Div([
                    html.Label("Select Date Range"),
                    dcc.DatePickerRange(
                        id="date-filter",
                        min_date_allowed=df["date"].min().date(),
                        max_date_allowed=df["date"].max().date(),
                        start_date=df["date"].min().date(),
                        end_date=df["date"].max().date(),
                        display_format="DD-MM-YYYY"
                    )
                ], style={"flex": "1", "minWidth": "240px"})
            ]
        ),

        html.Div(
            id="kpi-row",
            style={
                "display": "flex",
                "gap": "16px",
                "flexWrap": "wrap",
                "marginBottom": "20px"
            }
        ),

        dcc.Graph(id="trend-chart"),

        html.Div(
            style={"display": "flex", "gap": "15px", "flexWrap": "wrap"},
            children=[
                dcc.Graph(
                    id="category-chart",
                    style={"flex": "1", "minWidth": "300px"}
                ),
                dcc.Graph(
                    id="region-chart",
                    style={"flex": "1", "minWidth": "300px"}
                )
            ]
        )
    ]
)

# 4. KPI CARD FUNCTION
def kpi_card(title, value):
    return html.Div(
        [
            html.Div(title, style={"color": "#666"}),
            html.H2(value, style={"margin": "8px 0 0"})
        ],
        style=CARD
    )

# 5. DASHBOARD CALLBACK
@app.callback(
    Output("kpi-row", "children"),
    Output("trend-chart", "figure"),
    Output("category-chart", "figure"),
    Output("region-chart", "figure"),
    Input("region-filter", "value"),
    Input("category-filter", "value"),
    Input("date-filter", "start_date"),
    Input("date-filter", "end_date")
)
def update_dashboard(regions, categories, start, end):

    if not start or not end:
        d = df.iloc[0:0].copy()
    else:
        d = df[
            df["region"].isin(regions or [])
            & df["category"].isin(categories or [])
            & df["date"].between(
                pd.Timestamp(start), pd.Timestamp(end)
            )
        ]

    if d.empty:
        empty_fig = px.scatter(
            title="No data for selected filters"
        )
        kpis = [
            kpi_card("Total Revenue", "$0.00"),
            kpi_card("Orders", "0"),
            kpi_card("Average Order Value", "$0.00"),
            kpi_card("Units Sold", "0")
        ]
        return kpis, empty_fig, empty_fig, empty_fig

    # KPI calculations
    kpis = [
        kpi_card("Total Revenue", f"${d['revenue'].sum():,.2f}"),
        kpi_card("Orders", f"{len(d):,}"),
        kpi_card("Average Order Value", f"${d['revenue'].mean():,.2f}"),
        kpi_card("Units Sold", f"{d['units'].sum():,}")
    ]

    # Monthly revenue trend
    monthly = (
        d.set_index("date")["revenue"]
        .resample("MS")
        .sum()
        .reset_index()
    )

    fig_trend = px.line(
        monthly,
        x="date",
        y="revenue",
        markers=True,
        title="Monthly Revenue Trend",
        labels={"date": "Month", "revenue": "Revenue ($)"}
    )

    # Revenue by category
    by_cat = (
        d.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue")
    )

    fig_cat = px.bar(
        by_cat,
        x="revenue",
        y="category",
        orientation="h",
        title="Revenue by Category",
        labels={"category": "Category", "revenue": "Revenue ($)"}
    )

    # Revenue by region
    by_reg = (
        d.groupby("region", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    fig_reg = px.bar(
        by_reg,
        x="region",
        y="revenue",
        title="Revenue by Region",
        labels={"region": "Region", "revenue": "Revenue ($)"}
    )

    return kpis, fig_trend, fig_cat, fig_reg

# 6. RUN DASHBOARD
if __name__ == "__main__":
    app.run(debug=True)
