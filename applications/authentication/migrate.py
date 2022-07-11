from flask import Flask;
from configuration import Configuration;
from flask_migrate import Migrate, init, migrate, upgrade;
from models import database, User;
from sqlalchemy_utils import database_exists, create_database, drop_database
import os
import shutil

dirpath = "/opt/src/authentication/migrations"

if os.path.exists(dirpath) and os.path.isdir(dirpath):
    shutil.rmtree(dirpath)

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

done = False
while done==False:
    try:
        if (database_exists(application.config["SQLALCHEMY_DATABASE_URI"])):
            drop_database(application.config["SQLALCHEMY_DATABASE_URI"])


        create_database(application.config["SQLALCHEMY_DATABASE_URI"])

        database.init_app(application);

        with application.app_context() as context:
            init();
            migrate(message="Production migration");
            upgrade();

            customer = User (
                email = "admin@admin.com",
                password = "1",
                forename = "admin",
                surname = "admin",
                isCustomer = False
            )

            database.session.add(customer);
            database.session.commit();

            done = True
    except Exception as error:
        print(error)

while True:
    pass