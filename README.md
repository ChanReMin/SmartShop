# 🛒 SmartShop — E-commerce Backend

> 🚀 A modular, scalable e-commerce backend built with **FastAPI**, **SQLAlchemy**, and **Repository-Service Pattern**.

---

## 📘 Overview

**SmartShop** là hệ thống backend mô phỏng sàn thương mại điện tử, được thiết kế với kiến trúc **đa tầng** và **clean architecture**.  
Dự án tập trung vào:
- Quản lý **sản phẩm**, **tồn kho**, **đơn hàng**
- Hỗ trợ nhiều **phương thức thanh toán**
- Mô-đun hóa bằng **Design Patterns** (Repository, Factory, Strategy, Facade, Service Layer)

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Language** | Python 3.12 |
| **Framework** | FastAPI |
| **ORM** | SQLAlchemy |
| **Database** | SQL Server |
| **Auth** | JWT |
| **Design Patterns** | Repository, Factory, Strategy, Facade, Service |
| **Environment** | `.env` configuration |

---

## 🧠 Design Patterns Overview

### 🏢 Repository Pattern
- Mỗi bảng trong database có 1 repository riêng (`OrderRepository`, `ProductRepository`, `InventoryRepository`).
- Tách biệt logic truy cập dữ liệu khỏi logic nghiệp vụ.  
- Giúp dễ test, bảo trì và thay đổi DB mà không ảnh hưởng các tầng khác.

```python
order = order_repo.create_order(user_id, total)
order_repo.add_items(order, order_items)


⚙️ Service Layer Pattern

- Chứa logic nghiệp vụ (business logic) như kiểm tra tồn kho, giảm tồn, xử lý đơn hàng.
- Không truy cập DB trực tiếp, mà gọi repository tương ứng.

```python
insufficient = self.check_stock(items)
if insufficient:
    order.status = OrderStatus.FAILED.value
    self.session.commit()


🧩 Facade Pattern
- Đóng vai trò là lớp “điều phối” giữa các service:
- OrderFacade gọi OrderService, InventoryService và PaymentFactory để xử lý toàn bộ quy trình đặt hàng.

```python
order = service.create_pending_order(user_id, items)
payment_result = strategy.pay(order.id, order.total_amount)


🧭 Strategy Pattern
- Mỗi phương thức thanh toán (PayPal, CreditCard, v.v.) là một chiến lược riêng biệt kế thừa PaymentStrategy.
- Cho phép mở rộng dễ dàng mà không chỉnh sửa code cũ.

```python
class PayPalPayment(PaymentStrategy):
    def pay(self, order_id, amount):
        return {"success": True, "status": "success", "message": "Paid via PayPal"}

🏭 Factory Pattern
- PaymentFactory chịu trách nhiệm khởi tạo chiến lược thanh toán phù hợp dựa trên payment_method trong request.

```python
strategy = PaymentFactory.get_strategy(payment_method)
payment_result = strategy.pay(order.id, order.total_amount)


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

⚙️ Installation & Setup
1️⃣ Clone repository
git clone https://github.com/yourusername/SmartShop.git
cd SmartShop

2️⃣ Create & activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Setup database config

Tạo file .env trong thư mục gốc:

DATABASE_URL=mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
SECRET_KEY=supersecretkey

5️⃣ Run migrations (nếu có)
flask db init
flask db migrate -m "migrating.."
flask db upgrade


🧪 Example API Usage
📦 Create Order

POST /api/order

Request Body

{
  "user_id": 1,
  "items": [
    { "product_id": 2, "quantity": 10 }
  ],
  "payment": "creditcard"
}


Response

{
  "success": true,
  "order_id": 23,
  "total": 1200.0,
  "status": "success",
  "message": "Order placed and paid successfully"
}



