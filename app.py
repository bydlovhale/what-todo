
**Code (app.py)**  
```python
from flask import Flask, render_template_string, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT)")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return render_template_string("""
    <h1>To-Do</h1>
    <form method="post" action="/add"><input name="task"><button>Add</button></form>
    <ul>{% for id, task in tasks %}<li>{{task}} <a href="/delete/{{id}}">x</a></li>{% endfor %}</ul>
    """, tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    task = request.form["task"]
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:tid>")
def delete(tid):
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (tid,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
