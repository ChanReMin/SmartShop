# app/utils/dbseed.py
import sys
import os
import random
from faker import Faker

# Thêm thư mục gốc vào Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app import create_app, db
from app.models import User, Category, Product, Inventory

fake = Faker()
Faker.seed(42)  # Đặt seed để dữ liệu nhất quán giữa các lần chạy

# Danh sách category thực tế
REAL_CATEGORIES = [
    "Smartphones", "Laptops", "Tablets", "Headphones", "Smartwatches",
    "Cameras", "Gaming Consoles", "Printers", "Monitors", "Keyboards",
    "Mice", "Routers", "External Hard Drives", "USB Flash Drives", "Speakers",
    "Projectors", "Drones", "VR Headsets", "Computer Cases", "Power Supplies"
]

def generate_sku(name: str, id: int) -> str:
    """Tạo SKU từ tên sản phẩm"""
    words = name.split()[:3]
    prefix = "".join(word[:2].upper() for word in words)
    return f"{prefix}{id:05d}"

def seed_data():
    app = create_app()
    with app.app_context():
        print("🗑️ Dropping and recreating tables...")
        db.drop_all()
        db.create_all()

        # =============== 1. Categories ===============
        print("📦 Creating 100 categories...")
        categories = []
        # Thêm 20 category thực tế
        for name in REAL_CATEGORIES:
            categories.append(Category(name=name, description=fake.text(max_nb_chars=200)))
        # Thêm 80 category ngẫu nhiên
        for i in range(20, 100):
            categories.append(Category(
                name=fake.word().title() + " " + fake.word().title(),
                description=fake.text(max_nb_chars=200)
            ))
        db.session.add_all(categories)
        db.session.commit()
        category_ids = [c.id for c in categories]

        # =============== 2. Users ===============
        print("👥 Creating 100 users (1 admin)...")
        admin = User(
            username="admin",
            email="admin@smartshop.com",
            is_admin=True
        )
        admin.set_password("admin123")
        users = [admin]

        for i in range(99):
            username = fake.user_name()
            # Đảm bảo username unique
            while User.query.filter_by(username=username).first():
                username = fake.user_name() + str(random.randint(10, 99))
            user = User(
                username=username,
                email=fake.email(),
                is_admin=False
            )
            user.set_password("password123")
            users.append(user)
        db.session.add_all(users)
        db.session.commit()

        # =============== 3. Products ===============
        print("📱 Creating 10,000 products...")
        products = []
        product_names = set()  # Tránh trùng lặp tên

        for i in range(1, 10001):
            # Tạo tên sản phẩm thực tế
            brand = random.choice(["Apple", "Samsung", "Sony", "Dell", "HP", "Lenovo", "Asus", "Acer", "Xiaomi", "Huawei"])
            device_type = random.choice(["Phone", "Laptop", "Tablet", "Watch", "Headphones", "Camera", "Monitor"])
            model = fake.lexify(text="????-####")
            name = f"{brand} {device_type} {model}"
            
            # Tránh trùng lặp (hiếm, nhưng có thể)
            while name in product_names:
                model = fake.lexify(text="????-####")
                name = f"{brand} {device_type} {model}"
            product_names.add(name)

            category_id = random.choice(category_ids)
            price = round(random.uniform(50, 2000), 2)
            sku = generate_sku(name, i)

            product = Product(
                sku=sku,
                name=name,
                price=price,
                category_id=category_id,
                description=fake.text(max_nb_chars=500)
            )
            products.append(product)

            if len(products) % 1000 == 0:
                db.session.add_all(products)
                db.session.commit()
                print(f"  ✅ {len(products)} products created")
                products = []

        if products:
            db.session.add_all(products)
            db.session.commit()

        # =============== 4. Inventory ===============
        print("📦 Creating inventory records...")
        inventories = []
        for p in Product.query.all():
            inv = Inventory(
                product_id=p.id,
                quantity=random.randint(0, 200)  # Stock từ 0-200
            )
            inventories.append(inv)
            if len(inventories) % 1000 == 0:
                db.session.add_all(inventories)
                db.session.commit()
                inventories = []
        if inventories:
            db.session.add_all(inventories)
            db.session.commit()

        print("✅ Seed completed! Summary:")
        print(f"   - Categories: {len(categories)}")
        print(f"   - Users: {len(users)} (1 admin)")
        print(f"   - Products: {Product.query.count()}")
        print(f"   - Inventory: {Inventory.query.count()}")

if __name__ == "__main__":
    seed_data()