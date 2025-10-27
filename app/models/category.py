from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    products = db.relationship("Product", backref="category", lazy="dynamic", cascade="all,delete")

    def add_product(self, product):
        """Add a product to this category."""
        self.products.append(product)
        db.session.add(product)
        db.session.commit()

    @classmethod
    def get_by_id(cls, product_id):
        """Get a product by its ID."""
        return cls.query.get(product_id)
    
    def save(self):
        """Save or update the product in the database."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the product from the database."""
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        """Update product fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
    def __repr__(self):
        return f"<Category {self.name}>"
