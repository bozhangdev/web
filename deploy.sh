source env/bin/activate
pip install -r requirements.txt
env/bin/gunicorn -w 4 -b 0.0.0.0:8080 wsgi:app >& out.log &