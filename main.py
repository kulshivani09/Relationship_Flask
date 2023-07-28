from flask import Flask, request, jsonify,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, backref
from datetime import date
from UserNotFound import UserNotFoundException
from flask_swagger_ui import get_swaggerui_blueprint
#from routes import request_api

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=f"postgresql://{'postgres'}:{'Shiva09'}@{'localhost'}:{'5432'}/{'ecommerce'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static',path)

SWAGGER_URL='/swagger'
API_URL='/static/swagger.json'
swaggerui_blueprint=get_swaggerui_blueprint(SWAGGER_URL,API_URL,config={"app_name":"Bank Project"})
app.register_blueprint(swaggerui_blueprint,url_prefix=SWAGGER_URL)
#app.register_blueprint(request_api.get_blueprint())


#parent class
class BankCustomer(db.Model):
    __tablename__ = 'BankCustomer'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(50))
    address=db.Column(db.String(50))
    mob=db.Column(db.String(10))
    gender=db.Column(db.String(10))
    accounts=db.relationship('Account',backref='bankCustomer',cascade='all, delete-orphan') #backref='bankcustomer' creates attribute in child class

    def __init__(self,name,address,mob,gender):
        self.name=name
        self.address=address
        self.mob=mob
        self.gender=gender
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

#child class
class Account(db.Model):
    __tablename__ ='Account'
    acc_no=db.Column(db.Integer,primary_key=True)
    balance=db.Column(db.Integer)
    acc_created=db.Column(db.Date)
    cust_id=db.Column(db.Integer,db.ForeignKey('BankCustomer.id'))

    def __init__(self,acc_no,balance,cust_id):
        self.acc_no=acc_no
        self.balance=balance
        self.acc_created=date.today()
        self.cust_id=cust_id
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

@app.route("/api/InsertBankCustomer",methods=['POST'])
def insert_bank_customer():
    data=request.get_json()
    name=data["name"]
    address = data["address"]
    mob=data["mob"]
    gender=data["gender"]
    cust=BankCustomer(name,address,mob, gender)
    db.session.add(cust)
    db.session.commit()
    BankCustomer.query.all()
    return jsonify(cust.as_dict())

@app.route("/api/InsertAccount",methods=['POST'])
def insert_account():
    data=request.get_json()
    acc_no=data["acc_no"]
    balance = data["balance"]
    cust_id=data["cust_id"]
    try:
        acc=Account(acc_no,balance,cust_id)
        db.session.add(acc)
        db.session.commit()
        Account.query.all()
        return jsonify(acc.as_dict())
    except IntegrityError as e:
        # Handling the integrity error
        return jsonify({"Exception":f"{e}"}),401

@app.route("/api/UpdateBankCustomer",methods=['POST'])
def update_customer():
    data = request.get_json()
    cust = BankCustomer.query.get(data['cust_id'])
    try:
        if cust is not None:
            if 'name' in data.keys():
                cust.name = data['name']
            if 'address' in data.keys():
                cust.address = data['address']
            if 'mob' in data.keys():
                cust.mob = data['mob']
            if 'gender' in data.keys():
                cust.gender = data['gender']

            db.session.add(cust)
            db.session.commit()
            return jsonify(cust.as_dict())
        else:
            raise UserNotFoundException("User not found")
    except UserNotFoundException as unf:
        return jsonify({"msg":f"{unf.msg}"}),404

@app.route("/api/DeleteCustomer",methods=['POST'])
def delete_customer():
    data = request.get_json()
    cust = BankCustomer.query.get(data['id'])
    if not cust:
        return jsonify({"message": f"User with ID {data['id']} not found"}), 404
    try:
        db.session.delete(cust)
        db.session.commit()
        return jsonify({"message": f"User with ID {data['id']} has been deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error while deleting user with ID {cust.id}: {str(e)}"}), 500

@app.route("/api/DeleteAccount/<acc_no>",methods=['DELETE'])
def delete_account(acc_no):
    cust = Account.query.get(acc_no)
    if not cust:
        return jsonify({"message": f"User with ID {acc_no} not found"}), 404
    try:
        db.session.delete(cust)
        db.session.commit()
        return jsonify({"message": f"User with ID {acc_no} has been deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error while deleting account with ID {cust.acc_no}: {str(e)}"}), 500



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)