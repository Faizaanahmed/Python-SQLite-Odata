import logging
from dicttoxml import dicttoxml
from flask import Response, request, jsonify
import sqlite3
import xml.etree.ElementTree as ET
from app.db.database import execute_query, execute_insert, execute_update, execute_delete
import app.utils.utils as utils

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

def setup_routes(app):
    @app.route('/<odataurl>/')
    def list_tables(odataurl):
        # Assuming odataurl corresponds to a database name, adjust as needed
        db_name = f"{odataurl.split('.')[0]}.db"

        # Connect to the database and fetch table names
        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
        except sqlite3.Error as e:
            return jsonify({'success': False, 'error': str(e)}), 500

        # Format the list of tables for JSON response
        table_list = [table[0] for table in tables]
        return jsonify({'success': True, 'tables': table_list})

    @app.route('/<odataurl>/<tablename>', methods=['GET'])
    def get_table_data(odataurl, tablename):
        logging.info('Accessing table data for: %s', tablename)
        try:
            # Input validation
            if not tablename.isalnum():
                raise ValueError('Invalid table name')
            query_params = request.args

            # Parsing query options ($top, $skip, $filter, $select, $orderby)
            top = query_params.get('$top', None)
            skip = query_params.get('$skip', None)
            filter_option = query_params.get('$filter', None)
            select_option = query_params.get('$select', None)
            orderby_option = query_params.get('$orderby', None)

            # Construct the query with the parsed options
            results = utils.construct_get_query(tablename, query_params, top, skip, filter_option, select_option, orderby_option)
            data = execute_query(results)
            response_format = query_params.get('$format', 'json').lower()

            if response_format == 'json':
                # OData-compliant JSON formatting
                odata_response = {
                    "@odata.context": f"{request.url_root}{odataurl}/$metadata",
                    "value": data
                }
                return jsonify(odata_response)
            else:
                # OData-compliant XML formatting
                xml_data = dicttoxml(data, custom_root='feed', attr_type=False)
                return Response(xml_data, mimetype='application/xml')
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            logging.error('Error accessing table data: %s', str(e))
            return jsonify({'error': str(e)}), 500

    @app.route('/<odataurl>/<tablename>', methods=['POST'])
    def add_record(odataurl, tablename):
        try:
            record_data = request.json
            results = utils.construct_insert_query(tablename, record_data)
            execute_insert(results)
            return jsonify({'success': True, 'message': 'Record added successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/<odataurl>/<tablename>/<id>', methods=['PATCH'])
    def update_record(odataurl, tablename, id):
        try:
            update_data = request.json
            results = utils.construct_patch_query(tablename, id, update_data)
            rows_affected = execute_update(results)
            return jsonify({'success': True, 'message': f'{rows_affected} record(s) updated'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/<odataurl>/<tablename>/<id>', methods=['DELETE'])
    def delete_record(odataurl, tablename, id):
        try:
            query = f'DELETE FROM {tablename} WHERE id = ?'
            execute_delete(query, (id,))
            return jsonify({'success': True, 'message': 'Record deleted successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/<odataurl>/$metadata', methods=['GET'])
    def metadata(odataurl):
        return generate_metadata_document(f"{odataurl.split('.')[0]}.db")
