import sqlite3
from aiohttp import request
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('../clan_data.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    raids = conn.execute('select * from raids').fetchall()
    conn.close()
    return render_template('index.html', raids=raids)

@app.route('/_is_complete', methods=['POST'])
def is_complete():
    cheevo_id = request.form.get('cheevoid')
    player_id = request.form.get('playerid')
    conn = get_db_connection()
    progress = conn.execute('select complete from progress where cheevo=%s and player=%s' % (cheevo_id, player_id,)).fetchone()
    if progress[0] == 1:
        progress = "Done"
    else:
         progress = "Incomplete"
    conn.close()
    return (progress)

@app.route('/_cheevo_desc', methods=['POST'])
def cheevo_desc():
    cheevo_id = request.form.get('cheevodescid')
    conn = get_db_connection()
    result = conn.execute('select desc from cheevos where id=%s' % (cheevo_id,)).fetchone()
    conn.close()
    return (result[0])

@app.route('/raid/<raid_id>')
def raid(raid_id):
    conn = get_db_connection()
    raid_name = conn.execute("select name from raids where id=%s" % (raid_id,)).fetchone()
    cheevos = conn.execute("select * from cheevos where raid=%s" % (raid_id,)).fetchall()
    players = conn.execute('select * from players').fetchall()
    conn.close()
    return render_template('raid.html', raid_name=raid_name, cheevos=cheevos, players=players)

if __name__ == '__main__':
   app.run(debug = True)