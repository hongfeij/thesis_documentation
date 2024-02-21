# let's get started

from flask import Flask
from api_routes import setup_api_routes
import conversation

app = Flask(__name__)
setup_api_routes(app)

conversation.start_chat()

if __name__ == '__main__':
    app.run(debug=True)