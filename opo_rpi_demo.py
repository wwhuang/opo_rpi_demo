from flask import Flask, request, session, g, url_for, render_template
from contextlib import closing
import sqlite3
import json
import os

app = Flask(__name__)
app.config.from_object('fl_config')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/receive_data', methods=["POST"])
def receive_data():
    data = request.get_json()
    g.db.execute('insert into interactions (xr_id, tx_id, range, seq, time,) \
                 values (?, ?, ?, ?, ?, ?, ?, ?)', \
                 data['RX_ID'], data['TX_ID'], data['SEQ'],
                 data['RANGE'], data['SEQ'], data['TIME'])
    g.db.commit()
    return str(data)


@app.route('/chord_graph')
def chord_graph():
    return render_template('chord.html')


@app.route('/get_chords')
def get_chords():
    """
    Grab all interactions from the database, then create interactions
    based on both time and range. Sequence unused for now.
    """
    cur = g.db.execute('SELECT * FROM interactions')
    ids, rows = [], []
    for row in cur.fetchall():
        ids.append(row[1])
        ids.append(row[2])
        rows.append(row)
    ids = sorted(list(set(ids)))
    chords, interactions = [], []
    results = {}

    for i in range(len(ids)):
        chords.append([])
        interactions.append([])
        for j in range(len(ids)):
            chords[i].append(0)
            interactions[i].append([])

    for row in rows:
        rx_id, tx_id, r, seq, t = row[1], row[2], row[3], row[4], row[5]
        i1, i2 = ids.index(rx_id), ids.index(tx_id)
        interactions[i1][i2].append((r, seq, t))

    for i in range(len(ids)):
        for j in range(len(ids)):
            if len(interactions[i][j]) > 0:
                last_time, total_time = interactions[i][j][0], 0
                for d in interactions[i][j]:
                    if d[0] < 1.1:
                        if d[2] - last_time <= 10:
                            total_time += (t - last_time)
                        last_time = t
                chords[i][j] = total_time

    results['data'] = chords
    results['ids'] = ids
    results['title'] = "Social Interactions"

    return json.dumps(results)

if __name__ == '__main__':
    app.config['DEBUG'] = True
    if not os.path.isfile(app.config['DATABASE']):
        init_db()
    app.run()