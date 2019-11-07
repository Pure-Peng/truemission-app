import os
import json
import sqlite3
import hashlib
from contextlib import closing
from flask import Flask, render_template, request, session, redirect, abort

app = Flask(__name__)

dbname = "tm.db"

# Bind to PORT if defined, otherwise default to 5000.
port = int(os.environ.get('PORT', 5000))

@app.route("write_db")
def write_db():
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        c.execute("create table")


@app.route("/pr")
def pr():
    return render_template("pr.html")


@app.errorhandler(404)
def notfound(error):
    return render_template("notfound.html", for_="yugure_hokoku"), 404


def areyoulogin(*dargs):
    def decorator(f):
        def wrapper(*args):
            newargs = dargs + args
            if "username" in session and "passwhash" in session:
                if len(session["username"]) == 3:
                    f()
                else:
                    redirect("/login?from_="+str(*newargs[0]))
            else:
                redirect("/login?from_="+str(*newargs[0]))

        return wrapper
    return decorator


@app.route('/logincheck', methods=["POST"])
def login_check():
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        c.execute("select from users where id == (?)", (request.form['id']))
        users = c.fetchall()
        userid = list()
        passwhash = list()
        for i in users:
            passwhash.append(i[1])
            userid.append(i[0])
        if hashlib.sha3_256(request.form['passw'].encode()).hexdigest() in passwhash:
            result = {
                "result": {
                    "tf": "success",
                    "inner": ""
                }
            }
        else:
            result = {
                "result": {
                    "tf": "fail",
                    "inner": "ログインに失敗しました。"
                }
            }


@app.route('/login')
def login():
    return render_template('login.html')


@areyoulogin('/yugure_hokoku')
@app.route('/yugure_hokoku')
def hokoku():
    userhokoku = tuple()
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        c.execute("select from houkoku where (?)", (session["passwhash"],))
        userhokoku = c.fetchall()
    if len(userhokoku) >= 3:
        return render_template('almost.html')
    else:
        return render_template('houkoku.html', {"nokori": len(userhokoku)})


@areyoulogin('/asayake_ninsho')
@app.route('/asayake_ninsho')
def ninsho():
    return render_template('ninsho.html')


@areyoulogin('/firststage_check')
@app.route('/firststage_check', methods=["POST"])
def firststage_check():
    keyword = request.form['keyword']
    KEYWORDS = os.environ.get('KEYWORD')
    if isinstance(keyword, str):
        if keyword == KEYWORDS["1ststage_num"]:
            result = {
                "result": {
                    "tf": "success",
                    "inner": "認証に成功しました。私は京王八王子のマックに居ます。ユウグレ教祖の謎の紙をそこで渡したいと思います。移動を宜しくお願いします。<a href='/' class='box button'>戻る</a>"
                }
            }
            return json.dumps(result)
        else:
            result = {
                "result": {
                    "tf": "fail",
                    "inner": "認証に失敗しました。もう一度考えてみてください。<a href='/' class='box button'>戻る</a>"
                }
            }
            return json.dumps(result)


@areyoulogin('/keyword_check')
@app.route('/keyword_check', methods=["POST"])
def check():
    keyword = request.form['keyword']

    # json.loads(os.environ.get('KEYWORDS'))

    result = {
        "result": {
            "tf": "success",
            "inner": "最終報告を済ませました。解答発表までお待ちください。<a href='/' class='box button'>戻る</a>"
        }
    }
    with closing(sqlite3.connect(dbname)) as conn:
        c = conn.cursor()
        c.execute("insert into users (id, keyword) values (?,?)",
                  (session["username"], keyword))

    return json.dumps(result)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=port)
