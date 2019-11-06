import os
import json
import sqlite3
import hashlib
from contextlib import closing
from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)

dbname = "tm.db"

# Bind to PORT if defined, otherwise default to 5000.
port = int(os.environ.get('PORT', 5000))


def areyoulogin(func):
    if "username" in session and "hash" in session:
        if hashlib.sha3_256(str(session["username"]).encode()).hexdigest() == session["hash"]:
            return func
        else:
            return redirect("/login")
    else:
        return redirect("/login")


@app.route('/logincheck')
def login_check():
    hashlib.sha3_256(str(session["username"]).encode()
                     ).hexdigest() == session["hash"]


@app.route('/login')
def login():
    return render_template('login.html')


@areyoulogin
@app.route('/yugure_hokoku')
def hokoku():
    return render_template('houkoku.html')


@app.route('/asayake_ninsho')
def ninsho():
    return render_template('ninsho.html')


@app.route('/firststage_check', methods=["POST"])
def firststage_check():
    keyword = request.form['keyword']
    KEYWORDS = {"1ststage_num": "738"}
    if isinstance(keyword, str):
        if keyword == KEYWORDS["1ststage_num"]:
            result = {
                "result": {
                    "tf": "success",
                    "inner": "おめでとうございます！認証に成功しました。私は京王八王子のマックに居ます。ユウグレ教祖の謎の紙をそこで渡したいと思います。移動を宜しくお願いします。<a href='/' class='box button'>戻る</a>"
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
