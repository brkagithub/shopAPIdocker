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
from models import database, Product, ProductCategory, Category, Order, ProductOrder

application = Flask(__name__);
application.config.from_object(Configuration);

jwt = JWTManager ( application );

@application.route("/productStatistics", methods=["GET"])
@jwt_required(refresh=False)
def productStatistics():
    accessClaims = get_jwt()

    if accessClaims["forename"] != "admin":
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    productStats = {}

    for po in ProductOrder.query.all():
        p = Product.query.get(po.productId)
        if productStats.get(po.productId, None) == None:
            productStats[po.productId] = [p.name, po.requested, po.requested-po.received]
        else:
            arr = productStats[po.productId]
            arr[1] += po.requested
            arr[2] += (po.requested-po.received)
            productStats[po.productId] = arr

    returnList = []

    for prodId, arr in productStats.items():
        returnList.append({
            "name": arr[0],
            "sold": arr[1],
            "waiting": arr[2],
        })

    return Response(json.dumps({"statistics" : returnList}), status=200)

@application.route("/categoryStatistics", methods=["GET"])
@jwt_required(refresh=False)
def categoryStatistics():
    accessClaims = get_jwt()

    if accessClaims["forename"] != "admin":
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    categoriesMap = {}

    for c in Category.query.all():
        categoriesMap[c.name] = 0

    for po in ProductOrder.query.all():
        p = Product.query.get(po.productId)
        for c in p.categories:
            categoriesMap[c.name] += po.requested

    returnList = []

    for value in sorted(categoriesMap.items(), key=lambda item: (-item[1], item[0])):
        returnList.append(value[0])

    return Response(json.dumps({"statistics" : returnList}), status=200)

if (__name__ == "__main__"):
    database.init_app(application);
    #application.run(debug=True, port=5001)
    application.run ( debug = True, host = "0.0.0.0", port = 5010 );
