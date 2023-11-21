#!/bin/sh

if [ "$FLASK_ENV" = "development" ]; then
    echo "Creating the database tables..."
    python3 manage.py create_db
    python3 manage.py seed_db
    echo "Tables created"
    if [ "$FLASK_DEBUG" = "1" ]; then
        echo "Running on Flask Development Server"
        python3 main.py
    else
        echo "Running on Gunicorn"
        gunicorn main:app -c "$PWD"/gunicorn.config.py    
    fi
else
    echo "Running on Gunicorn"
    gunicorn main:app -c "$PWD"/gunicorn.config.py
fi
