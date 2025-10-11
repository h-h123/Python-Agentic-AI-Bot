import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])