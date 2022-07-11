from flask import Flask, request, Response, jsonify;
from configuration import Configuration;
#from applications.shop.models import database, User;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_, or_
import json
import csv
import io
from redis import Redis
from models import database, Product, ProductCategory, Category, Order, ProductOrder
import datetime

application = Flask(__name__);
application.config.from_object(Configuration);

jwt = JWTManager ( application );

@application.route("/search", methods=["GET"])
@jwt_required(refresh=False)
def search():
    accessClaims = get_jwt()

    if accessClaims["roles"] != "customer":
        return Response(json.dumps({"msg": "Missing Authorization Header"}),status=401)

    name = request.args.get("name")
    category = request.args.get("category")

    if name==None and category==None:
        products=Product.query.all()
    elif name is not None and category==None:
        products=Product.query.filter(Product.name.like(f"%{name}%"))
    elif name==None and category is not None:
        products=Product.query.join(ProductCategory).join(Category).filter(
                Category.name.like(f"%{category}%")
        )
    else: #oba nisu None
        products = Product.query.join(ProductCategory).join(Category).filter(
            and_(Category.name.like(f"%{category}%"), Product.name.like(f"%{name}%"))
        )

    allCategories = [] # sva imena kategorija
    allProducts = []
    for p in products:
        productCategories = []
        for c in p.categories:
            productCategories.append(c.name)
            if c.name not in allCategories:
                allCategories.append(c.name)
        allProducts.append({"categories":productCategories, "id":p.id, "name":p.name, "price":p.price, "quantity":p.quantity})
    return Response(json.dumps({"categories":allCategories, "products":allProducts}))

@application.route("/order", methods=["POST"])
@jwt_required(refresh=False)
def order():
    accessClaims = get_jwt()

    if accessClaims["roles"] != "customer":
        return Response(json.dumps({"msg": "Missing Authorization Header"}),status=401)

    requests = request.json.get("requests", "")

    if requests=="": return Response(json.dumps({"message": "Field requests is missing."}), status=400)

    reqs = []

    for reqnum, req in enumerate(requests):
        if req.get("id", "")=="":
            return Response(json.dumps({"message": f"Product id is missing for request number {reqnum}."}), status=400);
        if req.get("quantity", "")=="":
            return Response(json.dumps({"message": f"Product quantity is missing for request number {reqnum}."}), status=400);
        if not str(req.get("id")).isnumeric() or req.get("id")==0:
            return Response(json.dumps({"message": f"Invalid product id for request number {reqnum}."}), status=400);
        if not str(req.get("quantity")).isnumeric() or req.get("quantity") == 0:
            return Response(json.dumps({"message": f"Invalid product quantity for request number {reqnum}."}), status=400);

        productDB = Product.query.filter(Product.id==req.get("id")).first()
        if productDB is None:
            return Response(json.dumps({"message": f"Invalid product for request number {reqnum}."}), status=400);

        reqs.append(req)

    order = Order(price=0, status="COMPLETE", timestamp=datetime.datetime.now().isoformat(), email=get_jwt_identity())
    haveToWait = False
    database.session.add(order)
    database.session.commit()

    #productsToDelete = []

    for req in reqs: #skupili smo zahteve, sada kreiramo narudzbinu
        productDB = Product.query.filter(Product.id==req.get("id")).first() #moglo je get
        if productDB.quantity >= req.get("quantity"):
            productDB.quantity -= req.get("quantity") # odmah saljemo
            #productsToDelete.append( (productDB.id, req.get("quantity")) )
            order.price += productDB.price * req.get("quantity")
            productOrder = ProductOrder(productId=productDB.id, orderId=order.id, requested=req.get("quantity"), received=req.get("quantity"), price=productDB.price)
            database.session.add(productOrder)
            database.session.commit()
            database.session.add(productDB)
            database.session.commit()
        else:
            haveToWait = True
            order.price += productDB.price * req.get("quantity")
            productOrder = ProductOrder(productId=productDB.id, orderId=order.id, requested=req.get("quantity"), received=productDB.quantity, price=productDB.price)
            productDB.quantity = 0  # sve saljemo jer nema dovoljno
            #database.session.add(order)
            #database.session.commit()
            database.session.add(productOrder)
            database.session.commit()
            database.session.add(productDB)
            database.session.commit()

    if haveToWait: order.status = "PENDING"

    database.session.add(order)
    database.session.commit()

    return jsonify(id=order.id)

@application.route("/status", methods=["GET"])
@jwt_required(refresh=False)
def status():
    accessClaims = get_jwt()

    if accessClaims["roles"] != "customer":
        return Response(json.dumps({"msg": "Missing Authorization Header"}), status=401)

    arrayToReturn = []

    for o in Order.query.filter(Order.email==get_jwt_identity()).all():
        elToAdd = {
            "products": [],
            "price" : float(o.price),
            "status" : o.status,
            "timestamp" : o.timestamp
        }
        for p in o.products:
            categoryNames = []
            for c in p.categories:
                categoryNames.append(c.name)
            productToAdd = {
                "categories" : categoryNames,
                "name" : p.name,
                "price" : float(ProductOrder.query.join(Order).filter(and_(
                    Order.id == o.id,
                    ProductOrder.productId == p.id
                )).first().price),
                "received" : ProductOrder.query.join(Order).filter(and_(
                    Order.id == o.id,
                    ProductOrder.productId == p.id
                )).first().received,
                "requested" : ProductOrder.query.join(Order).filter(and_(
                    Order.id == o.id,
                    ProductOrder.productId == p.id
                )).first().requested
            }
            elToAdd["products"].append(productToAdd)
        arrayToReturn.append(elToAdd)

    return jsonify(orders=arrayToReturn)

if (__name__ == "__main__"):
    database.init_app(application);
    #application.run(debug=True, port=5006)
    application.run ( debug = True, host = "0.0.0.0", port = 5006 );
