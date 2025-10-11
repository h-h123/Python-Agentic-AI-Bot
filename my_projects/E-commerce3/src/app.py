import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import create_app, db
from src.models import User, Product, Cart, Order, OrderItem
from flask_migrate import upgrade

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Cart': Cart,
        'Order': Order,
        'OrderItem': OrderItem
    }

@app.cli.command("init-db")
def init_db():
    """Initialize the database with tables"""
    db.create_all()
    print("Database tables created")

@app.cli.command("seed-db")
def seed_db():
    """Seed the database with initial data"""
    from src.seeds import seed_database
    seed_database()
    print("Database seeded with initial data")

if __name__ == '__main__':
    app.run()