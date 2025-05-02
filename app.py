
**Code (app.py)**  
'''
'''code'''
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
    app.run(debug=True)'''


from flask import Flask, render_template_string, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for sessions

def init_db():
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT, user TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    conn.commit()
    conn.close()

def get_tasks(user):
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("SELECT id, task FROM tasks WHERE user=?", (user,))
    tasks = c.fetchall()
    conn.close()
    return tasks

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    tasks = get_tasks(session["user"])
    return render_template_string("""
    <h1>To-Do</h1>
    <form method="post" action="/add"><input name="task"><button>Add</button></form>
    <ul>{% for id, task in tasks %}
        <li>{{task}} 
            <a href="/edit/{{id}}">edit</a> 
            <a href="/delete/{{id}}">x</a>
        </li>
    {% endfor %}</ul>
    <a href="/logout">Logout</a>
    """, tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")
    task = request.form["task"]
    if task.strip() == "":
        return redirect("/")
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task, user) VALUES (?, ?)", (task, session["user"]))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:tid>")
def delete(tid):
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=? AND user=?", (tid, session["user"]))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/edit/<int:tid>", methods=["GET", "POST"])
def edit(tid):
    if "user" not in session:
        return redirect("/login")
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    if request.method == "POST":
        new_task = request.form["task"]
        c.execute("UPDATE tasks SET task=? WHERE id=? AND user=?", (new_task, tid, session["user"]))
        conn.commit()
        conn.close()
        return redirect("/")
    c.execute("SELECT task FROM tasks WHERE id=? AND user=?", (tid, session["user"]))
    task = c.fetchone()
    conn.close()
    return render_template_string("""
        <form method="post">
            <input name="task" value="{{task[0]}}">
            <button>Save</button>
        </form>
    """, task=task)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("todo.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect("/")
    return render_template_string("""
        <h2>Login</h2>
        <form method="post">
            <input name="username" placeholder="username">
            <input name="password" placeholder="password" type="password">
            <button>Login</button>
        </form>
        <a href="/signup">Sign Up</a>
    """)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("todo.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            session["user"] = username
            conn.close()
            return redirect("/")
        except sqlite3.IntegrityError:
            conn.close()
    return render_template_string("""
        <h2>Sign Up</h2>
        <form method="post">
            <input name="username" placeholder="username">
            <input name="password" placeholder="password" type="password">
            <button>Sign Up</button>
        </form>
        <a href="/login">Login</a>
    """)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
