from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Define relationship with orders (if you have an Order model)
    orders = db.relationship('Order', backref='user', lazy=True)

    # --- Methods ---
    @classmethod
    def get_all(cls):
        """Get all users from the database ordered by ID descending."""
        return cls.query.order_by(cls.id.desc()).all()
    
    @classmethod
    def get_total_count(cls):
        """Get total count of users."""
        return cls.query.count()

    def save(self):
        """Adds the user to the session and commits the transaction."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Deletes the user from the database."""
        db.session.delete(self)
        db.session.commit()
    
    def set_password(self, password):
        """Hashes and stores the user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def create_order(self, order):
        """Attach a new order to the user."""
        self.orders.append(order)
        return order
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<User {self.username}>"