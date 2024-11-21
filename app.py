from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'Hola mundo'

if __name__ == '__main__':
    app.run(debug=True)
