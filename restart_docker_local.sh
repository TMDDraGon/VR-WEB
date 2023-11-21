#!/bin/sh
# auto everything
docker-compose down
docker system prune -a -f

docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml --compatibility up -d

docker-compose exec web python3 manage.py create_db
docker-compose exec web python3 manage.py seed_db