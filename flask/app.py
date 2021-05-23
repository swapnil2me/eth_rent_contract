import os
import ssl
import json
from web3 import Web3
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
from flask_qrcode import QRcode
from flask_session import Session

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, Time
from flask_marshmallow import Marshmallow

app = Flask(__name__)
qrcode = QRcode(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'super secret key'

##
ganache_url = "HTTP://192.168.0.104:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))


### sqlite DB settings
dataLocation = '/mnt/5a576321-1b84-46e6-ba92-46de6b117d92/Dump'
DB_URL = 'sqlite:///'+os.path.join(dataLocation, 'database.db')

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)
ma = Marshmallow(app)

class LoginTable(db.Model):
    __tablename__ = 'login'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    hexId = Column(String)
    privateKey = Column(String)

class LoginTableSchema(ma.Schema):
    class Meta:
        fields = ('id','username','hexId','privateKey')

login_table_schema = LoginTableSchema(many = True)


@app.route("/login", methods=["POST", "GET"])
def login():
    if not session.get('messages'):
        session['messages'] = ''
    if request.method == "POST":
        session["name"] = request.form.get("name")
        return redirect("/")

    return render_template("login.html", msg = session['messages'])


@app.route('/')
def index():

    table = LoginTable.query.all()
    result = login_table_schema.dump(table)
    users = [result[i]['username'] for i in range(len(result))]
    hix = [result[i]['hexId'] for i in range(len(result))]
    print(users,hix)



    if not session.get("name"):
        return redirect(url_for('login'))

    user = session.get("name")

    if user not in users:
        print("not registered please register")
        session.pop('name',None)
        session['messages'] = "not registered please register yourself"
        return redirect(url_for('login'))

    pk = [result[i]['privateKey'] for i in range(len(result)) if result[i]['username']==user]
    hi = [result[i]['hexId'] for i in range(len(result)) if result[i]['username']==user]
    balance = (web3.eth.get_balance(hi[0]))*1e-18
    return render_template('index.html',user = user, balance = balance)


@app.route('/getUsers')
def getUsers():
    table = LoginTable.query.all()
    result = login_table_schema.dump(table)
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin','*')
    # print(result[0]['username'])
    return response


@app.route('/scan_qr')
def scan_qr():
    table = LoginTable.query.all()
    result = login_table_schema.dump(table)
    user = session.get("name")
    pk = [result[i]['privateKey'] for i in range(len(result)) if result[i]['username']==user]
    hi = [result[i]['hexId'] for i in range(len(result)) if result[i]['username']==user]
    balance = (web3.eth.get_balance(hi[0]))*1e-18
    return render_template('scan_qr.html',user = user, balance = balance)


@app.route('/pay_qr/<hexId>/<ammount>',methods=['GET', 'POST'])
def pay_qr(hexId,ammount=1):
    ##
    table = LoginTable.query.all()
    result = login_table_schema.dump(table)
    user = session.get("name")
    pk = [result[i]['privateKey'] for i in range(len(result)) if result[i]['username']==user]
    hi = [result[i]['hexId'] for i in range(len(result)) if result[i]['username']==user]

    account_to = hexId
    account_from = hi[0]
    pk = pk[0]

    nonce = web3.eth.getTransactionCount(account_from)

    tx = {
        'nonce': nonce,
        'from':account_from,
        'to': account_to,
        'value': web3.toWei(ammount,'ether'),
        'gas': 2000000,
        'gasPrice': web3.toWei('50','gwei')
        }
    print(tx)
    signed_tx = web3.eth.account.signTransaction(tx, pk)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    # print(web3.toHex(tx_hash))
    ##

    return redirect(url_for('index'))


@app.route('/receive')
def receive():
    # return send_file(qrcode("swapnilmore"), mimetype="image/png")
    data = request.args.get("data", "")
    table = LoginTable.query.all()
    result = login_table_schema.dump(table)
    user = session.get("name")
    pk = [result[i]['privateKey'] for i in range(len(result)) if result[i]['username']==user]
    hi = [result[i]['hexId'] for i in range(len(result)) if result[i]['username']==user]
    balance = (web3.eth.get_balance(hi[0]))*1e-18
    return render_template('receive.html', hexId=hi[0], balance = balance)


@app.route('/rent')
def rent():
    return render_template('rent.html')


@app.route("/qrcode", methods=["GET"])
def get_qrcode():
    # please get /qrcode?data=<qrcode_data>
    data = request.args.get("data", "")
    return send_file(qrcode(data, mode="raw"), mimetype="image/png")


ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    # context = ('server.crt', 'server.key')
    # app.run(host='10.217.77.128',port=8000, debug=True, ssl_context=context)
    app.run(port=8080,debug=True)
    # app.run(host='192.168.0.103',port=8080, debug=True)
