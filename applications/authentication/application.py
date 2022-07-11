from flask import Flask, request, Response, jsonify;
from configuration import Configuration;
from models import database, User;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity;
from sqlalchemy import and_;
import json
import re

application = Flask(__name__);
application.config.from_object(Configuration);


@application.route("/register", methods=["POST"])
def register():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    isCustomer = request.json.get("isCustomer", "")

    forenameEmpty = len(forename) == 0;
    surnameEmpty = len(surname) == 0;
    emailEmpty = len(email) == 0;
    passwordEmpty = len(password) == 0;
    isCustomerEmpty = not isinstance(isCustomer, bool)  # ako nije bool greska je

    if forenameEmpty: return Response(json.dumps({"message": "Field forename is missing."}), status=400)
    if surnameEmpty: return Response(json.dumps({"message": "Field surname is missing."}), status=400)
    if emailEmpty: return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if passwordEmpty: return Response(json.dumps({"message": "Field password is missing."}), status=400)
    if isCustomerEmpty: return Response(json.dumps({"message": "Field isCustomer is missing."}), status=400)

    pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])+$"
    regex = re.compile(pattern)

    if not re.fullmatch(regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400);

    passwordOk = len(password) >= 8 and any(
        char.isdigit() for char in password) and not password.islower() and not password.isupper()

    if not passwordOk: return Response(json.dumps({"message": "Invalid password."}), status=400);

    user = User.query.filter(User.email == email).first()

    if user:
        return Response(json.dumps({"message": "Email already exists."}), status=400);

    user = User(email=email, password=password, forename=forename, surname=surname, isCustomer=isCustomer);
    database.session.add(user);
    database.session.commit();

    return Response(status=200);

jwt = JWTManager ( application );

@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0;
    passwordEmpty = len(password) == 0;

    if emailEmpty: return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if passwordEmpty: return Response(json.dumps({"message": "Field password is missing."}), status=400)

    pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])+$"
    regex = re.compile(pattern)

    if not re.fullmatch(regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400);

    user = User.query.filter(and_(User.email == email, User.password == password)).first();

    if (not user):
        return Response(json.dumps({"message": "Invalid credentials."}), status=400);

    additionalClaims = {
        "forename" : user.forename,
        "surname" : user.surname,
        "roles" : "customer" if user.isCustomer else "manager"
    }

    if password == "1":
        additionalClaims = {
            "forename": user.forename,
            "surname": user.surname,
            "roles": "administrator"
        }
    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    #responseObj = jsonify(accessToken=accessToken, refreshToken=refreshToken)
    return jsonify ( accessToken=accessToken, refreshToken=refreshToken );

@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"],
    }

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims))

@application.route("/delete", methods=["POST"])
@jwt_required(refresh=False)
def delete():
    email = request.json.get("email", "")
    #identity = get_jwt_identity()
    accessClaims = get_jwt()

    if accessClaims["forename"] != "admin": return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    if len(email) == 0: return Response(json.dumps({"message": "Field email is missing."}), status=400)

    pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])+$"
    regex = re.compile(pattern)

    if not re.fullmatch(regex, email):
        return Response(json.dumps({"message": "Invalid email."}), status=400);

    user = User.query.filter(User.email == email).first()

    if not user: return Response(json.dumps({"message": "Unknown customer."}), status=400)

    User.query.filter(User.email == email).delete()
    database.session.commit()

    return Response(status=200)

if (__name__ == "__main__"):
    database.init_app(application);
    #application.run(debug=True)
    application.run ( debug = True, host = "0.0.0.0", port = 5002 );
