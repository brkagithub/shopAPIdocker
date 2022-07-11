from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy ( );

class ProductCategory(database.Model):
    __tablename__ = "productcategory"
    id = database.Column(database.Integer, primary_key=True);
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False);
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False);

class ProductOrder(database.Model):
    __tablename__ = "productorder"
    id = database.Column(database.Integer, primary_key=True);
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False);
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False);
    requested = database.Column (database.Integer);
    received = database.Column(database.Integer);
    price = database.Column(database.Float);

class Product(database.Model):
    __tablename__ = "products"
    id = database.Column ( database.Integer, primary_key = True );
    name = database.Column ( database.String ( 256 ), nullable = False );
    quantity = database.Column ( database.Integer, nullable=False )
    price = database.Column ( database.Float, nullable=False )
    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products");
    orders = database.relationship("Order", secondary=ProductOrder.__table__, back_populates="products");
    #numSold = database.Column ( database.Integer, default=0)
    #numWaiting = database.Column(database.Integer, default=0)

class Category(database.Model):
    __tablename__ = "categories"
    id = database.Column(database.Integer, primary_key=True);
    name = database.Column ( database.String ( 256 ), nullable = False, unique = True );

    products = database.relationship ( "Product", secondary = ProductCategory.__table__, back_populates = "categories" );

class Order(database.Model):
    __tablename__ = "orders"
    id = database.Column(database.Integer, primary_key=True);
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False);
    timestamp = database.Column(database.String(256), nullable=False);
    products = database.relationship("Product", secondary=ProductOrder.__table__, back_populates="orders");
    email = database.Column(database.String(256), nullable=False)