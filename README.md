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

Chứa logic nghiệp vụ (business logic) như kiểm tra tồn kho, giảm tồn, xử lý đơn hàng.
Không truy cập DB trực tiếp, mà gọi repository tương ứng.

insufficient = self.check_stock(items)
if insufficient:
    order.status = OrderStatus.FAILED.value
    self.session.commit()
