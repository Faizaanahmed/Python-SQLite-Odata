import sqlite3
import pandas as pd
import json
tablelist = []
db_name = "chinook.db"
odataurl = db_name.split('.')[0] + ".xsodata"
tables = {"metadata":{"d":{"EntitySets" : []}},"data":{}}
conn = sqlite3.connect(db_name)
c = conn.cursor()

x = c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
available_table = x.fetchall()
print(available_table)
c.close()

for y in available_table:
    tables["metadata"]["d"]["EntitySets"].append(y[0])

from flask import Flask, request, jsonify
import os
app = Flask(__name__)
port = int(os.environ.get('PORT', 8080))
@app.route("/<odataurl>", methods=['GET', 'POST'])
def odata(odataurl):
    return jsonify(tables["metadata"])

@app.route("/<odataurl>/<tablename>", methods=['GET', 'POST'])
def odatatable(odataurl,tablename):
    with sqlite3.connect(db_name) as conn:
        df = pd.read_sql_query("SELECT * FROM " + tablename, conn)
        data = json.loads(json.dumps(list(df.T.to_dict().values())))

    return jsonify({"d" : {"results" : [data]}})

if __name__ == '__main__':
    app.run(host='localhost', port=port)
# Create your connection.
