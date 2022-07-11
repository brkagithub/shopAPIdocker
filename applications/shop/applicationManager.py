from flask import Flask, request, Response, jsonify;
from configuration import Configuration;
#from applications.shop.models import database, User;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity;
from sqlalchemy import and_;
import json
import csv
import io
from redis import Redis
from models import database

application = Flask(__name__);
application.config.from_object(Configuration);

jwt = JWTManager ( application );

@application.route("/update", methods=["POST"])
@jwt_required(refresh=False)
def update():
    accessClaims = get_jwt()

    if accessClaims["roles"] != "manager":
        return Response(json.dumps({"msg": "Missing Authorization Header"}),status=401)

    if 'file' not in request.files:
        return Response(json.dumps({"message":"Field file is missing."}), status=400)

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    productsToAdd = []

    for count, row in enumerate(reader):
        if len(row)!=4:
            return Response(json.dumps({"message": f"Incorrect number of values on line {count}."}), status=400);

        categories = row[0].split('|')
        name = row[1]
        if not row[2].isnumeric():
            return Response(json.dumps({"message": f"Incorrect quantity on line {count}."}), status=400);
        quantity = int(row[2])

        if quantity==0:
            return Response(json.dumps({"message": f"Incorrect quantity on line {count}."}), status=400);

        try:
            price = float(row[3])
            if price <= 0:
                return Response(json.dumps({"message": f"Incorrect price on line {count}."}), status=400);
        except ValueError:
            return Response(json.dumps({"message": f"Incorrect price on line {count}."}), status=400);

        productsToAdd.append(json.dumps({"categories":json.dumps(categories), "name":str(name), "quantity":quantity, "price":price}))

    for prod in productsToAdd:
        with Redis(host=Configuration.REDIS_HOST) as redis:
            redis.rpush(Configuration.REDIS_PRODUCTS_LIST, prod)

    return Response(status=200)
if (__name__ == "__main__"):
    database.init_app(application);
    #application.run(debug=True, port=5001)
    application.run ( debug = True, host = "0.0.0.0", port = 5001 );
