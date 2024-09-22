from flask import Flask, request, jsonify, render_template
import os
import bot

app = Flask(__name__)
bot_running = False

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = os.environ['GOOGLE_SECRET_KEY']
GMAIL_APP_PASSWORD = os.environ['GMAIL_APP_PASSWORD']

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)