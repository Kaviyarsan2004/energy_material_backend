from dash import dcc, html, Input, Output
import dash
from flask import request, jsonify
from pymatgen.core import Structure
from motor.motor_asyncio import AsyncIOMotorClient
import crystal_toolkit.components as ctc
import dash_bootstrap_components as dbc
from pymongo import MongoClient

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], requests_pathname_prefix='/dash/')

# MongoDB client setup
client = MongoClient("mongodb+srv://ECD517:bing24@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["vasp_data"]

# Global variable to store selected element data
selected_dopant_data = None

# Layout
app.layout = html.Div([
    html.Div(id='structure_output'),  # Where the structure will be rendered
])

# Flask route to handle POST requests from React
@app.server.route('/select-dopant', methods=['POST'])
def select_dopant():
    global selected_dopant_data
    data = request.json
    selected_dopant_data = data.get("element")
    print(f'POST data: {selected_dopant_data}')
    
    if data:
        selected_dopant_data = data.get("element")
        
        # Force update by using Dash callback trigger
        # This returns the updated structure directly as JSON
        return jsonify({"message": "Data updated successfully", "refresh": True})
    
    return jsonify({"message": "Element not found"}), 404

# Callback to render structure
@app.callback(
    Output('structure_output', 'children'),
    Input('structure_output', 'children')
)
def render_structure(_):
    global selected_dopant_data
    if not selected_dopant_data:
        return html.Div("No data selected.")
    
    collection = db[selected_dopant_data]
    stored_structure = collection.find_one()
    
    if stored_structure is None:
        return html.Div("No structure data found in the database.")
    
    structure_data = stored_structure.get('structure')
    if structure_data is None:
        return html.Div("Structure data not found in the document.")
    
    structure = Structure.from_dict(structure_data)
    structure_component = ctc.StructureMoleculeComponent(structure, id="my_structure")
    return structure_component.layout()


# Register Crystal Toolkit
ctc.register_crystal_toolkit(app=app, layout=app.layout)

if __name__ == "__main__":
    app.run_server(port=8050, debug=True)
