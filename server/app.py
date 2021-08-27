from flask import Flask

app = Flask(__name__)

@app.route('/')
def hw():
    return "<h1>Hello, world</h1>"

@app.route('/api')
def api():
    return "<h1>Hello, api</h1>"
