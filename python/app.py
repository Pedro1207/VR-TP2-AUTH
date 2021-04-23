from flask import Flask, flash, redirect, render_template, request, session, url_for, make_response
from connector import Connector
from datetime import timedelta
import os
import json

app = Flask(__name__)
connector = Connector()

@app.before_request
def func():
  session.modified = True

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for("login"));
    else:
        return render_template("home.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        password = request.form['password']
        username = request.form['username']
        if(len(username) == 0 or len(password) == 0):
            flash("Please introduce your name and password")
            return render_template("login.html")
        token = connector.getToken(username, password)
        if(token != False):
            session['logged_in'] = True
            resp = make_response(redirect(url_for("home")))
            resp.set_cookie("vr_username", username)
            resp.set_cookie("vr_token", token)
            return resp;
        else:
            flash("Wrong username or password")
            return render_template("login.html")
    elif not session.get('logged_in'):
        return render_template("login.html")
    else:
        return redirect(url_for('home'))

@app.route('/elogin', methods=['POST', 'GET'])
def elogin():
    if request.method == "POST":
        redirect_url = session.get('redirect')
        if not redirect_url:
            return redirect(url_for('login'))
        password = request.form['password']
        username = request.form['username']

        if(len(username) == 0 or len(password) == 0):
            flash("Please introduce your name and password")
            return render_template("elogin.html")

        token = connector.getToken(username, password)
        if(token != False):
            session['logged_in'] = True
            resp = make_response(redirect(redirect_url + '?user=' + username + '&token=' + token))
            resp.set_cookie("vr_username", username)
            resp.set_cookie("vr_token", token)
            return resp;
        else:
            flash("Wrong username or password")
            return render_template("elogin.html")
    else:
        redirect_url = request.args.get('redirect')
        if(redirect):
            if not session.get('logged_in'):
                session['redirect'] = redirect_url
                return render_template("elogin.html")
            else:
                username = request.cookies.get('vr_username')
                token = request.cookies.get('vr_token')
                return redirect(redirect_url + '?user=' + username + '&token=' + token)
        else:
            return redirect(url_for(login))

@app.route('/checklogin')
def checklogin():
    username = request.args.get('username')
    token = request.args.get('token')
    if username != None and token != None:
        return str(connector.checkToken(token, username))
    else:
        return str(False)

@app.route('/checkadmin')
def checkadmin():
    username = request.args.get('username')
    if username != None:
        return str(connector.checkAdmin(username))
    else:
        return str(False)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        password = request.form['password']
        repeatpassword = request.form['repeatpassword']
        username = request.form['username']
        admin = request.form.get('admin')

        if(username == ""):
            flash("Your username is invalid")
            return render_template("create.html")
        elif(len(password) < 8):
            flash("Your password is too short")
            return render_template("create.html")
        elif(password != repeatpassword):
            flash("Your passwords do not match.")
            return render_template("create.html")
        elif(connector.checkForUser(username)):
            flash("Username already exists.")
            return render_template("create.html")
        else:
            if(admin):
                connector.insertUser(username, password, True)
            else:
                connector.insertUser(username, password, False)
            flash("Success. You can now login")
            return render_template("login.html")

    else:
        return render_template("create.html")

@app.route('/logout')
def logout():
    session['logged_in'] = False
    username = request.cookies.get('vr_username')
    if(username):
        connector.logout(username)

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.permanent_session_lifetime = timedelta(minutes=5)
    app.run(debug=True,host='0.0.0.0', port=80)
