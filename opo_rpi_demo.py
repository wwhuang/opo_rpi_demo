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

        reader = open('Node_Ids.csv', 'rb')
        reader.readline()
        for line in reader:
            raw = line.strip().split()
            ds2411_id = int(raw[0], 16)
            node_id = int(raw[1])
            db.execute('insert into id_map (ds2411_id, node_id) values (?, ?)',
                        [ds2411_id, node_id])
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return "Hello"


@app.route('/receive_data', methods=["POST"])
def receive_data():
    data = request.get_json()
    g.db.execute('insert into interactions (rx_id, tx_id, range, time, rtc_time) values (?, ?, ?, ?, ?)',
                 [data['rx_id'], data['tx_id'], data['range'], data['time'], data['rtc_time']])
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
    id_cur = g.db.execute('SELECT * FROM id_map')
    raw_ids, ids, rows = [], []
    id_map = {}

    for row in cur.fetchall():
        raw_ids.append(row[1])
        raw_ids.append(row[2])
        rows.append(row)

    for row in id_cur.fetchall():
        id_map[row[0]] = row[1]

    for i in raw_ids:
        ids.append(raw_ids[i])

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
        rx_id, tx_id, m_range, real_time, rtc_time = row[1], row[2], row[3], row[4], row[5]
        rx_id = id_map[rx_id]
        tx_id = id_map[tx_id]
        i1, i2 = ids.index(rx_id), ids.index(tx_id)
        interactions[i1][i2].append((r, t))

    for i in range(len(ids)):
        for j in range(len(ids)):
            if len(interactions[i][j]) > 0:
                last_time, total_time = interactions[i][j][0][1], 0
                for d in interactions[i][j]:
                    print d
                    print last_time
                    if d[0] < 1.1:
                        if d[1] - last_time <= 12:
                            total_time += (d[1] - last_time)
                        last_time = d[1]
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