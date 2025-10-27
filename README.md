# 🛒 SmartShop — E-commerce Backend

> 🚀 A modular, scalable e-commerce backend built with **FastAPI**, **SQLAlchemy**, and **Repository-Service Pattern**.

---

## 📘 Overview

**SmartShop** is a backend system that simulates an e-commerce platform, designed with a **multi-layered** and **clean architecture** approach.  
The project focuses on:
- Managing **products**, **inventory**, and **orders**
- Supporting multiple **payment methods**
- Modularized with key **Design Patterns** (Repository, Factory, Strategy, Facade, Service Layer)

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Language** | Python 3.12 |
| **Framework** | FastAPI |
| **ORM** | SQLAlchemy |
| **Database** | SQL Server |
| **Authentication** | JWT |
| **Design Patterns** | Repository, Factory, Strategy, Facade, Service Layer |
| **Environment** | `.env` configuration |

---

## 🧠 Design Patterns Overview

### 🏢 Repository Pattern
- Each database table has its own repository (`OrderRepository`, `ProductRepository`, `InventoryRepository`).
- Separates **data access logic** from **business logic**.
- Improves testability, maintainability, and flexibility when changing the database layer.

```python
order = order_repo.create_order(user_id, total)
order_repo.add_items(order, order_items)
```

##⚙️ Service Layer Pattern
Contains business logic such as checking stock, reducing inventory, or processing orders.
Does not access the database directly — it delegates all data access to repositories.

```python
insufficient = self.check_stock(items)
if insufficient:
    order.status = OrderStatus.FAILED.value
    self.session.commit()
```

##🧩 Facade Pattern
Acts as a coordinator layer between multiple services.
OrderFacade calls OrderService, InventoryService, and PaymentFactory to process the entire order workflow.

```python
order = service.create_pending_order(user_id, items)
payment_result = strategy.pay(order.id, order.total_amount)
``
##🧭 Strategy Pattern
Each payment method (e.g., PayPal, CreditCard) is implemented as a separate strategy inheriting from PaymentStrategy.

Allows flexible extension of payment types without modifying existing logic.

```python
class PayPalPayment(PaymentStrategy):
    def pay(self, order_id, amount):
        return {"success": True, "status": "success", "message": "Paid via PayPal"}
```
##🏭 Factory Pattern
PaymentFactory is responsible for creating the correct payment strategy instance based on the payment_method in the request.

```python
strategy = PaymentFactory.get_strategy(payment_method)
payment_result = strategy.pay(order.id, order.total_amount)
```

📁 Folder Structure
app/
├── models/
│   ├── order.py
│   ├── product.py
│   └── inventory.py
│
├── repositories/
│   ├── base_repository.py
│   ├── order_repository.py
│   ├── product_repository.py
│   └── inventory_repository.py
│
├── services/
│   ├── order_service.py
│   ├── inventory_service.py
│   ├── payment_strategy.py
│   ├── payment_factory.py
│   └── order_facade.py
│
├── routes/
│   ├── api/
│   │   ├── order_route.py
│   │   ├── product_route.py
│   │   └── ...
│   └── auth_route.py
│
└── main.py

##⚙️ Installation & Setup
1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/SmartShop.git
cd SmartShop
```
2️⃣ Create & activate a virtual environment
bash
Copy code
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure environment variables
Create a .env file in the project root:

env
Copy code
DATABASE_URL=mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
SECRET_KEY=supersecretkey
5️⃣ Run database migrations
bash
Copy code
flask db init
flask db migrate -m "initial migration"
flask db upgrade
6️⃣ Start the FastAPI server
bash
Copy code
uvicorn app.main:app --reload
Open the interactive API docs at 👉 http://127.0.0.1:8000/docs

🧪 Example API Usage
📦 Create Order
POST /api/order

Request Body
json
Copy code
{
  "user_id": 1,
  "items": [
    { "product_id": 2, "quantity": 10 }
  ],
  "payment": "creditcard"
}
Response
json
Copy code
{
  "success": true,
  "order_id": 23,
  "total": 1200.0,
  "status": "success",
  "message": "Order placed and paid successfully"
}
