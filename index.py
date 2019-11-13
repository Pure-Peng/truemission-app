import os
import json
from google.cloud import datastore
import datetime
import hashlib
from flask import Flask, render_template, request, session, redirect, abort

app = Flask(__name__)
app.secret_key = "avhyfwbcbf89qu8f3uqc8y8vb"
client = datastore.Client.from_service_account_json(
    "truemission-db-3cc26d81eb59.json")


port = int(os.environ.get('PORT', 5000))
jst = datetime.timezone(datetime.timedelta(hours=9), 'JST')


@app.route("/pr")
def pr():
    return render_template("pr.html")


@app.errorhandler(404)
def notfound(error):
    return render_template("notfound.html", for_="asayake_ninsho"), 404


@app.route('/signup')
def signup_view():
    return render_template("signup.html")


@app.route('/signup_submit', methods=["POST"])
def signup_submit():
    if "teamname" in session:
        result = {
            "result": {
                "tf": "fail",
                "inner": "既に登録しています。<a href='/login' class='box button'>ログイン</a>"
            }
        }
        return json.dumps(result)
    elif len(request.form["passw"]) != 5:
        result = {
            "result": {
                "tf": "fail",
                "inner": "登録に失敗しました。パスワードは英数8文字で入力してください。<a href='/signup' class='box button'>戻る</a>"
            }
        }
        return json.dumps(result)
    elif (len(str(request.form["num"])) != 1) and (1 <= int(request.form["num"] <= 4)):
        result = {
            "result": {
                "tf": "fail",
                "inner": "登録に失敗しました。可能な参加人数は1~4人です。<a href='/signup' class='box button'>戻る</a>"
            }
        }
        return json.dumps(result)
    elif not 3 <= len(str(request.form["name"])) <= 10:
        result = {
            "result": {
                "tf": "fail",
                "inner": "登録に失敗しました。チーム名は3~10文字で入力してください。<a href='/signup' class='box button'>戻る</a>"
            }
        }
        return json.dumps(result)
    elif client.get(client.key("team", request.form['name'])) is not None:
        result = {
            "result": {
                "tf": "fail",
                "inner": "登録に失敗しました。チーム名の重複があります。違うチーム名にしてください。<a href='/signup' class='box button'>戻る</a>"
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
        result = {
            "result": {
                "tf": "success",
                "inner": "成功しました。"
            }
        }
        return json.dumps(result)


@app.route('/')
def mypage():
    if not "teamname" in session:
        return redirect("/login")
    else:
        print("this is logging in on {}".format(session["teamname"]))
        firstclear = str()
        if client.get(client.key("firstclear", session['teamname'])) is None:
            firstclear = "未クリア"
        else:
            firstclear = "クリア済"
        print(client.get(client.key("firstclear", session['teamname'])))
        query = client.query(kind="secondreport")
        query.add_filter("name", "=", session["teamname"])
        houkoku = list(query.fetch())
        return render_template(
            'index.html',
            teamname=session["teamname"],
            firstclear=firstclear,
            secondreports=houkoku,
            secondreport_num=3-len(houkoku))


@app.route('/login_check', methods=["POST"])
def login_check():
    if len(request.form["passw"]) != 5:
        try:
            del session["teamname"]
        except:
            pass
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
        try:
            del session["teamname"]
        except:
            pass
        result = {
            "result": {
                "tf": "fail",
                "inner": "ログインに失敗しました。"
            }
        }
        return json.dumps(result)


@app.route('/login')
def login():
    if ("teamname" in session):
        print("this is logging in on {}".format(session["teamname"]))
        if "from" in request.form:
            return redirect(request.form["from_"])
        else:
            return redirect("/")
    else:
        return render_template('login.html')


@app.route('/kaito')
def success_team():
    query = client.query(kind="secondreport")
    query.add_filter("keyword", "=", "夕闇の金剛石")
    houkoku = list(query.fetch())
    return render_template('kaito.html', secondreport=houkoku)


@app.route('/yugure_hokoku')
def hokoku():
    if ("teamname" in session):
        print("this is logging in on {}".format(session["teamname"]))
    else:
        return redirect("/login?from_=/yugure_hokoku")
    query = client.query(kind="secondreport")
    query.add_filter("name", "=", session["teamname"])
    houkoku = list(query.fetch())
    if len(houkoku) >= 3:
        return render_template('almost.html')
    else:
        return render_template('hokoku.html', nokori=3-len(houkoku))


@app.route('/asayake_ninsho')
def ninsho():
    if ("teamname" in session):
        print("this is logging in on {}".format(session["teamname"]))
    else:
        return redirect("/login?from_=/asayake_ninsho")
    return render_template('ninsho.html')


@app.route('/firststage_check', methods=["POST"])
def firststage_check():
    if ("teamname" in session):
        print("this is logging in on {}".format(session["teamname"]))
    else:
        result = {
            "result": {
                "tf": "fail",
                "inner": "ログインしてください。<a href='/login' class='box button'>ログイン</a>"
            }
        }
        return json.dumps(result)
    keyword = request.form['keyword']
    if isinstance(keyword, str):
        if keyword == "738":
            result = {
                "result": {
                    "tf": "success",
                    "inner": "認証に成功しました。私は京王八王子のマックに居ます。ユウグレ教祖の謎の紙をそこで渡したいと思います。移動を宜しくお願いします。<a href='/' class='box button'>戻る</a>"
                }
            }
            if client.get(client.key("firstclear", session['teamname'])) is None:
                ent = datastore.Entity(client.key(
                    "firstclear", session["teamname"]))
                ent["success"] = True
                ent["time"] = datetime.datetime.now(jst)
                client.put(ent)
            else:
                pass
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
    if ("teamname" in session):
        print("this is logging in on {}".format(session["teamname"]))
    else:
        result = {
            "result": {
                "tf": "fail",
                "inner": "ログインしてください。<a href='/login' class='box button'>ログイン</a>"
            }
        }
        return json.dumps(result)
    if keyword == "":
        result = {
            "result": {
                "tf": "fail",
                "inner": "何か文字を入力してください。<a href='/yugure_hokoku' class='box button'>戻る</a>"
            }
        }
        return json.dumps(result)
    result = {
        "result": {
            "tf": "success",
            "inner": "最終報告を済ませました。解答発表までお待ちください。<a href='/' class='box button'>戻る</a>"
        }
    }
    ent = datastore.Entity(client.key("secondreport"))
    ent["keyword"] = keyword
    ent["time"] = datetime.datetime.now(jst)
    ent["name"] = session["teamname"]
    client.put(ent)

    return json.dumps(result)


if __name__ == '__main__':
    app.run(port=port)
