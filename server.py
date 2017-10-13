from flask import Flask, request
import json

app = Flask(__name__)


@app.route('/fontto/processing', methods=['POST'])
def processing_fontto():
    print(request.json)
    return json.dumps(request.json)


@app.route('/')
def test_root():
    return 'OK'


if __name__ == '__main__':
    app.run(port=5959)
