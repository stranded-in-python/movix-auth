from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from main_flask import app


http_server = WSGIServer(('', 8002), app)
http_server.serve_forever()
