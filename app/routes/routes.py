import logging
from dicttoxml import dicttoxml
from flask import Response, request, jsonify
from db.database import execute_query, execute_insert, execute_update, execute_delete
import utils.utils as utils

def setup_routes(app):

    @app.route('/<odataurl>/<tablename>', methods=['GET'])
    def get_table_data(odataurl, tablename):
        logging.info('Accessing table data for: %s', tablename)
        try:
            query_params = request.args
            query, params = utils.construct_get_query(tablename, query_params)
            data = execute_query(query, params)
            response_format = query_params.get('$format', 'json').lower()
            if response_format == 'json':
                return jsonify({'success': True, 'data': data})
            else:
                xml_data = dicttoxml(data)
                return Response(xml_data, mimetype='application/xml')
        except Exception as e:
            logging.error('Error accessing table data: %s', str(e))
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/<odataurl>/<tablename>', methods=['POST'])
    def add_record(odataurl, tablename):
        try:
            record_data = request.json
            query, params = utils.construct_insert_query(tablename, record_data)
            execute_insert(query, params)
            return jsonify({'success': True, 'message': 'Record added successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/<odataurl>/<tablename>/<id>', methods=['PATCH'])
    def update_record(odataurl, tablename, id):
        try:
            update_data = request.json
            query, params = utils.construct_patch_query(tablename, id, update_data)
            rows_affected = execute_update(query, params)
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
        
