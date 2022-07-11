Command for running tests

python main.py --type all --with-authentication --authentication-address http://127.0.0.1:5002 --jwt-secret JWT_SECRET_KEY --roles-field roles --administrator-role admin --customer-role customer --warehouse-role manager --customer-address http://127.0.0.1:5006 --warehouse-address http://127.0.0.1:5001 --administrator-address http://127.0.0.1:5010

Commands to initialize docker swarm with the running containers

docker swarm init

docker stack deploy --compose-file compose.yaml projekat

docker stack rm projeka
