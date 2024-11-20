from dash import dcc, html, Input, Output
import dash
from flask import request, jsonify
from pymatgen.core import Structure
from motor.motor_asyncio import AsyncIOMotorClient
import crystal_toolkit.components as ctc
import dash_bootstrap_components as dbc
from pymongo import MongoClient
import time

# Initialize Dash app
dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], requests_pathname_prefix='/dash/')

# MongoDB client setup
client = MongoClient("mongodb+srv://ECD517:bing24@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["vasp_data"]
collections = db.list_collection_names()

dash_app.layout = html.Div([
    html.H1("Crystal Structure Display"),
    dcc.Dropdown(
        id="structure-dropdown",
        options=[{'label': col, 'value': col} for col in collections],
        placeholder="Select a structure"
    ),
    html.Div(id="structure-output")
])

@dash_app.callback(
    Output("structure-output", "children"),
    [Input("structure-dropdown", "value")]
)
def update_structure(selected_collection):
    if not selected_collection:
        return html.Div("Please select a structure.")
    collection = db[selected_collection]
    stored_structure = collection.find_one()
    if not stored_structure:
        return html.Div(f"No structure found in {selected_collection}.")
    structure = Structure.from_dict(stored_structure['structure'])
    structure_component = ctc.StructureMoleculeComponent(structure)
    return structure_component.layout()

ctc.register_crystal_toolkit(app=dash_app, layout=dash_app.layout)

# @app.get("/")
# async def root():
#     return {"message": "FastAPI and Dash App"}

