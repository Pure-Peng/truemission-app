import os
import json
from google.cloud import datastore
import datetime
import hashlib
from flask import Flask, render_template, request, session, redirect, abort

app = Flask(__name__)
app.secret_key = "avhyfwbcbf89qu8f3uqc8y8vb"
client = datastore.Client()


port = int(os.environ.get('PORT', 5000))
jst = datetime.timezone(datetime.timedelta(hours=9), 'JST')


@app.route("/pr")
def pr():
    return render_template("pr.html")


@app.errorhandler(404)
def notfound(error):
    return render_template("notfound.html", for_="/asayake_ninsho"), 404


@app.route('/signup')
def signup_view():
    return render_template("signup.html")


@app.route('/signup_submit', methods=["POST"])
def signup_submit():
    if len(request.form["passw"]) != 5:
        result = {
            "result": {
                "tf": "fail",
                "inner": "ログインに失敗しました。"
            }
        }
        return json.dumps(result)
    elif len(str(request.form["num"])) != 1:
        result = {
            "result": {
                "tf": "fail",
                "inner": "ログインに失敗しました。"
            }
        }
        return json.dumps(result)
    elif not 3 <= len(str(request.form["name"])) <= 10:
        result = {
            "result": {
                "tf": "fail",
                "inner": "ログインに失敗しました。"
            }
        }
        return json.dumps(result)
    else:
        ent = datastore.Entity(client.key("team", str(request.form["name"])))
        ent["num"] = int(request.form["num"])
        ent["passwhash"] = hashlib.sha3_256(
            request.form['passw'].encode()).hexdigest()
        ent["time"] = datetime.datetime.now(jst)
        client.put(ent)
        return redirect("/login")


@app.route('/login_check', methods=["POST"])
def login_check():
    if len(request.form["passw"]) != 5:
        del session["teamname"]
        result = {
            "result": {
                "tf": "fail",
                "inner": "ログインに失敗しました。"
            }
        }
        return json.dumps(result)
    ent = client.get(client.key("team", request.form['id']))
    if hashlib.sha3_256(request.form['passw'].encode()).hexdigest() == ent["passwhash"]:
        session["teamname"] = ent.key.id_or_name
        result = {
            "result": {
                "tf": "success",
                "inner": ""
            }
        }
        return json.dumps(result)
    else:
        del session["teamname"]
        result = {
            "result": {
                "tf": "fail",
                "inner": "ログインに失敗しました。"
            }
        }
        return json.dumps(result)


@app.route('/login')
def login():
    print("hello")
    return render_template('login.html')


@app.route('/yugure_hokoku')
def hokoku():
    if ("teamname" in session) and ("passwhash" in session):
        print("this is logging in")
    else:
        return redirect("/login?from_='/yugure_hokoku'")
    userhokoku = tuple()
    query = client.query(kind="secondreport")
    houkoku = list(query.fetch())
    if len(houkoku) > 3:
        return render_template('almost.html')
    else:
        return render_template('hokoku.html', nokori=3-len(userhokoku))


@app.route('/asayake_ninsho')
def ninsho():
    if ("teamname" in session):
        print("this is logging in")
    else:
        return redirect("/login?from_='/asayake_ninsho'")
    return render_template('ninsho.html')


@app.route('/firststage_check', methods=["POST"])
def firststage_check():
    if ("teamname" in session) and ("passwhash" in session):
        print("this is logging in")
    else:
        return redirect("/login?from_='/firststage_check'")
    keyword = request.form['keyword']
    if isinstance(keyword, str):
        if keyword == 738:
            result = {
                "result": {
                    "tf": "success",
                    "inner": "認証に成功しました。私は京王八王子のマックに居ます。ユウグレ教祖の謎の紙をそこで渡したいと思います。移動を宜しくお願いします。<a href='/' class='box button'>戻る</a>"
                }
            }
            try:
                ent = datastore.Entity(client.key(
                    "firstclear", session["teamname"]))
                ent["success"] = True
                ent["time"] = datetime.datetime.now(jst)
                client.put(ent)
            except:
                print("an error ocujijaed on the firstclear")
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
    if ("teamname" in session) and ("passwhash" in session):
        print("this is logging in")
    else:
        return redirect("/login?from_='/keyword_check'")
    keyword = request.form['keyword']

    result = {
        "result": {
            "tf": "success",
            "inner": "最終報告を済ませました。解答発表までお待ちください。<a href='/' class='box button'>戻る</a>"
        }
    }
    ent = datastore.Entity(client.key("secondreport", session["teamname"]))
    ent["keyword"] = keyword
    ent["time"] = datetime.datetime.now(jst)
    client.put(ent)

    return json.dumps(result)


if __name__ == '__main__':
    app.run(port=port)
