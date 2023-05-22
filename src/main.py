from flask import Flask

from db.db import init_db

app = Flask(__name__)


@app.route('/hello-world')
def hello_world():
    
    return 'Hello, World!'


if __name__ == '__main__':
    # init_db()
    app.run()