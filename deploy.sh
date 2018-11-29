source env/bin/activate
pip install -r requirements.txt
env/bin/gunicorn -b 0.0.0.0:8080 wsgi:app >& out.log &