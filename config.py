from app import app
from app.settings import PORT_DEFAULT

if __name__ == '__main__':
    # Para desenvolvimento local
    app.run(host='127.0.0.1', port=PORT_DEFAULT, debug=True)