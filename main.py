from app.routes.routes import setup_routes
import sqlite3
import pandas as pd
import json
import sys
import os

db_name = "chinook.db"
odataurl = db_name.split('.')[0] + ".xsodata"

tables = {"metadata": {"d": {"EntitySets": []}}, "data": {}}

# Using a context manager for the database connection
with sqlite3.connect(db_name) as conn:
    c = conn.cursor()
    x = c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    available_table = x.fetchall()

for y in available_table:
    tables["metadata"]["d"]["EntitySets"].append(y[0])

from flask import Flask, request, jsonify

app = Flask(__name__)
port = int(os.environ.get('PORT', 8080))

# Set up additional routes from routes.py
setup_routes(app)

if __name__ == '__main__':
    print(f"Starting Flask app with odataurl: {odataurl}")
    app.run(host='localhost', port=port)

# Function to generate metadata document (same as previously defined)
def generate_metadata_document(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve the list of tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # XML root element
    root = ET.Element('Schema', xmlns="http://docs.oasis-open.org/odata/ns/edm")

    for table_name in tables:
        # Each table represents an EntityType
        entity_type = ET.SubElement(root, 'EntityType', Name=table_name[0])

        # Retrieve the columns for each table
        cursor.execute(f"PRAGMA table_info({table_name[0]})")
        columns = cursor.fetchall()

        for col in columns:
            # Add each column as a Property of the EntityType
            ET.SubElement(entity_type, 'Property', Name=col[1], Type='Edm.String')  # Simplified type assumption

    # Convert the XML tree to a string
    metadata_str = ET.tostring(root, encoding='utf8', method='xml').decode()

    conn.close()
    return metadata_str

# New route for OData metadata

# Dynamic base path derived from db_name
base_path = db_name.split('.')[0] + '.xsodata'

# New route for OData metadata with dynamic base path
@app.route(f'/{base_path}/$metadata')
def odata_metadata():
    metadata_xml = generate_metadata_document(db_name)
    return Response(metadata_xml, mimetype='application/xml')

    metadata_xml = generate_metadata_document(db_name)
    return Response(metadata_xml, mimetype='application/xml')
