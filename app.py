import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from pymongo import MongoClient
from dash.dependencies import Input, Output

# Connect to MongoDB

client = MongoClient("mongodb+srv://ECD517:bing24@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client["ECD517"]

# Fetch data from MongoDB
def fetch_dopants():
    results = db["Dopant"].find({}, {"_id": 0, "Dopants": 1})
    return [doc["Dopants"] for doc in results if "Dopants" in doc]

def fetch_host_materials():
    results = db["HostMaterial"].find({}, {"_id": 0, "Material": 1})
    return [doc["Material"] for doc in results if "Material" in doc]

def fetch_charge_states():
    results = db["ChargeState"].find({}, {"_id": 0, "Charge": 1})
    return [doc["Charge"] for doc in results if "Charge" in doc]

# Initialize Dash app with Material theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])  # Bright theme

# Custom Styles
TAB_STYLE = {
    "background-color": "#f8f9fa",  
    "color": "#343a40",
    "font-size": "18px",
    "border-radius": "10px",
    "padding": "10px",
}

CARD_STYLE = {
    "border-radius": "10px",
    "box-shadow": "2px 2px 10px rgba(0, 0, 0, 0.1)",
    "padding": "20px",
    "background": "white"
}

BUTTON_STYLE = {
    "background-color": "#007bff",
    "color": "white",
    "border-radius": "10px",
    "font-size": "18px",
    "width": "100%",
}

# Layout
app.layout = dbc.Container([
    html.H1("Material Doping UI", className="text-center mt-4", style={"color": "#0056b3"}),

    dcc.Tabs(id="tabs", value="tab1", children=[
        dcc.Tab(label="Get Dopant Data", value="tab1", style=TAB_STYLE),
        dcc.Tab(label="Task 1", value="tab2", style=TAB_STYLE),
        dcc.Tab(label="Task 2", value="tab3", style=TAB_STYLE),
        dcc.Tab(label="Task 3", value="tab4", style=TAB_STYLE),
    ], colors={"border": "#ddd", "primary": "#007bff", "background": "#f8f9fa"}),

    html.Div(id="tab-content", className="mt-4")
], fluid=True, style={"background-color": "#eef2f7", "min-height": "100vh", "padding": "20px"})

# Callback for tab content
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def update_tab_content(tab):
    if tab == "tab1":
        return dbc.Row([
            # Column 1: Form
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H2("Select Parameters", style={"color": "#007bff"}),
                        
                        dbc.Label("Host Material", className="mt-2"),
                        dcc.Dropdown(id="host-dropdown", options=[
                            {"label": mat, "value": mat} for mat in fetch_host_materials()
                        ], placeholder="Select a Host Material"),

                        dbc.Label("Dopant", className="mt-2"),
                        dcc.Dropdown(id="dopant-dropdown", options=[
                            {"label": dopant, "value": dopant} for dopant in fetch_dopants()
                        ], placeholder="Select a Dopant"),

                        dbc.Label("Charge State", className="mt-2"),
                        dcc.Dropdown(id="charge-dropdown", options=[
                            {"label": charge, "value": charge} for charge in fetch_charge_states()
                        ], placeholder="Select a Charge State"),

                        html.Br(),
                        dbc.Button("Submit", id="submit-btn", style=BUTTON_STYLE, n_clicks=0)
                    ]),
                    style=CARD_STYLE
                )
            ], width=4),  # Column 1: Form

            # Column 2: Crystal Structure 1
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H2("Crystal Structure 1", className="text-center", style={"color": "#28a745"}),
                        html.Div("🧪 Rendered Structure Here", className="text-center")
                    ]),
                    style=CARD_STYLE
                )
            ], width=4),

            # Column 3: Crystal Structure 2
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H2("Crystal Structure 2", className="text-center", style={"color": "#dc3545"}),
                        html.Div("🔬 Rendered Structure Here", className="text-center")
                    ]),
                    style=CARD_STYLE
                )
            ], width=4)
        ])
    
    return html.Div("Task content goes here")


if __name__ == "__main__":
    app.run_server(debug=True)
