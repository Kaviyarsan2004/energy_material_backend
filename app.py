import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from pymongo import MongoClient
from pymatgen.core import Structure, Lattice
import crystal_toolkit.components as ctc
from crystal_toolkit.components.structure import StructureMoleculeComponent


# Connect to MongoDB
MONGO_URI = "mongodb+srv://ECD517:bing24@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["ECD517"]  # Database for VASP structures

# Fetch dopants from MongoDB
def fetch_dopants():
    results = db["Dopant"].find({}, {"_id": 0, "Dopants": 1})
    return [doc["Dopants"] for doc in results if "Dopants" in doc]

# Default placeholder structure
default_structure = Structure(Lattice.hexagonal(5, 3), ["Na", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]])

# Function to fetch structure from MongoDB
def get_structure(selected_dopant):
    if selected_dopant:
        db = client["vasp_data"]
        collection = db[selected_dopant]
        stored_structure = collection.find_one()
        if stored_structure and "structure" in stored_structure:
            return Structure.from_dict(stored_structure["structure"])
    return default_structure  # Return default structure if nothing found

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

# Layout
app.layout = dbc.Container([
    html.H1("Material Doping UI", className="text-center text-white mt-4"),

    dcc.Tabs(id="tabs", value="tab1", children=[
        dcc.Tab(label="Get Dopant Data", value="tab1"),
        dcc.Tab(label="Task 1", value="tab2"),
        dcc.Tab(label="Task 2", value="tab3"),
        dcc.Tab(label="Task 3", value="tab4"),
    ]),

    html.Div(id="tab-content", className="mt-4")
], fluid=True, style={"background-color": "#111", "min-height": "100vh", "padding": "20px"})

# Store for the structure data
app.layout.children.append(dcc.Store(id="structure-store"))

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
                        html.H2("Select Parameters", className="text-white"),

                        dbc.Label("Dopant", className="text-white"),
                        dcc.Dropdown(id="dopant-dropdown", options=[
                            {"label": dopant, "value": dopant} for dopant in fetch_dopants()
                        ], placeholder="Select a Dopant"),

                        html.Br(),
                        dbc.Button("Submit", id="submit-btn", color="danger", n_clicks=0)
                    ])
                )
            ], width=4),

            # Column 2: Crystal Structures (Side-by-Side)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H2("Crystal Structures", className="text-white text-center"),
                        dbc.Row([
                            dbc.Col(html.Div(id="structure-container-1",
                                             children=ctc.StructureMoleculeComponent(default_structure).layout())),
                        ])
                    ])
                )
            ], width=8),
        ])

    return html.Div("Task content goes here", className="text-white")


# Callback to update structure in store and render it
# Callback to update structure in store and render it
@app.callback(
    Output("structure-store", "data"),
    Output("structure-container-1", "children"),
    Input("submit-btn", "n_clicks"),
    State("dopant-dropdown", "value"),
    prevent_initial_call=True
)
def update_structure(n_clicks, selected_dopant):
    if selected_dopant:
        structure = get_structure(selected_dopant)
    else:
        structure = default_structure

    structure_component = ctc.StructureMoleculeComponent(structure)
    return structure.as_dict(), structure_component.layout()  # Changed to .as_dict()



# Register Crystal Toolkit
ctc.register_crystal_toolkit(app=app, layout=app.layout)

if __name__ == "__main__":
    app.run_server(debug=True)
