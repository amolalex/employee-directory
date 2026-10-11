import os
import time
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def init_db():
    for _ in range(10):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS employees ("
                "id SERIAL PRIMARY KEY, "
                "name TEXT NOT NULL, "
                "department TEXT NOT NULL)"
            )
            conn.commit()
            cur.close()
            conn.close()
            return
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("Database not reachable")


init_db()


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/employees", methods=["GET"])
def list_employees():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, department FROM employees ORDER BY id")
    rows = [{"id": r[0], "name": r[1], "department": r[2]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(rows)


@app.route("/employees", methods=["POST"])
def add_employee():
    data = request.get_json()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO employees (name, department) VALUES (%s, %s) RETURNING id",
        (data["name"], data["department"]),
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(id=new_id), 201
