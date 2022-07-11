from flask import Flask;
from flask_migrate import Migrate, init, migrate, upgrade;
#from applications.shop.models import database, User;
from sqlalchemy_utils import database_exists, create_database;
from configuration import Configuration;
from redis import Redis
application = Flask(__name__)
application.config.from_object(Configuration)
import json
from models import database, Product, Category, ProductCategory, Order, ProductOrder
from sqlalchemy import and_, or_

database.init_app(application);

while(True):
    product = None
    with Redis(host = Configuration.REDIS_HOST) as redis:
        product = json.loads(redis.blpop(Configuration.REDIS_PRODUCTS_LIST)[1])

    productExists = None
    productName = None
    with application.app_context() as context:
        productExists = Product.query.filter(Product.name==product.get("name")).first()
        if productExists:
            productName = productExists.name


    if not productExists: # ako ne postoji
        with application.app_context() as context:

            newProduct = Product(
                name=product.get("name"),
                price=product.get("price"),
                quantity=product.get("quantity")
            )

            database.session.add(newProduct) #dodaj proizvod
            database.session.commit()

            for category in json.loads(product.get("categories")):
                categoryExists = Category.query.filter(Category.name==category).first()
                if not categoryExists:
                    category = Category(name=category)
                    database.session.add(category) # dodaj ako ne postoji
                    database.session.commit()
                    productCategory = ProductCategory(productId=newProduct.id, categoryId=category.id)
                    database.session.add(productCategory) # dodaj vezu
                    database.session.commit()
                else:
                    productCategory = ProductCategory(productId = newProduct.id, categoryId=categoryExists.id)
                    database.session.add(productCategory) # vec postoji kategorija
                    database.session.commit() # dodati samo vezu
    else: # ako postoji
        with application.app_context() as context:
            productDB = Product.query.filter(Product.name==productName).first()
            categoriesList = productDB.categories
            categoriesNamesList = []
            for c in categoriesList: # napraviti niz imena kategorija iz baze
                categoriesNamesList.append(c.name)

            categoriesOK = True

            for c in json.loads(product.get("categories")):
                if c in categoriesNamesList:
                    continue
                else:
                    categoriesOK = False
                    break

            if categoriesOK:
                toAddQuantity = product.get("quantity")
                newQuantity = productDB.quantity + product.get("quantity")
                newPrice = (productDB.quantity*productDB.price + product.get("quantity")*product.get("price"))/(productDB.quantity+product.get("quantity"))

                #print(newPrice, flush=True)

                #product = Product.query.filter(Product.name==productName).first()

                productDB.price = newPrice
                productDB.quantity = newQuantity
                # database.session.add(productDB)
                database.session.commit()

                ordersToBeUpdated = Order.query.join(ProductOrder).join(Product).filter(
                    and_(Order.status=="PENDING",
                         Product.id == productDB.id,
                         #Product.quantity<ProductOrder.quantity,
                         ProductOrder.requested - ProductOrder.received > 0
                         )
                ).order_by(Order.timestamp)


                for o in ordersToBeUpdated:
                    po = ProductOrder.query.join(Order).filter(
                        ProductOrder.productId == productDB.id,
                        Order.id == o.id
                    ).first()

                    oldReceived = po.received

                    po.received = po.requested if po.received+productDB.quantity > po.requested else po.received+productDB.quantity

                    print(f"requested:{po.requested} received:{po.received}", flush=True)

                    productDB.quantity -= (po.received - oldReceived)


                    numOrdersCanBeUpdated = ProductOrder.query.join(Order).filter( #broj producta koji nisu jos potpuno isporuceno
                        and_(Order.id == o.id,
                             ProductOrder.requested - ProductOrder.received > 0
                             )
                    ).count()

                    ordersCanBeUpdated = numOrdersCanBeUpdated == 0

                    if ordersCanBeUpdated: o.status = "COMPLETE"

                    database.session.add(productDB)
                    database.session.add(po)
                    database.session.add(o)
                    database.session.commit()