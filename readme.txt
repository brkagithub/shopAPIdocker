python main.py --type all --with-authentication --authentication-address http://127.0.0.1:5002 --jwt-secret JWT_SECRET_KEY --roles-field roles --administrator-role admin --customer-role customer --warehouse-role manager --customer-address http://127.0.0.1:5006 --warehouse-address http://127.0.0.1:5001 --administrator-address http://127.0.0.1:5010

docker swarm init

docker stack deploy --compose-file compose.yaml projekat
sacekati da se sve digne

docker stack rm projekat
sacekati da se sve ugasi i obrisati volumes ako se pokrece pod istim imenom

