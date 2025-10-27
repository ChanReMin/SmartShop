# app/services/order_facade.py
from .order_service import OrderService
from .inventory_service import InventoryService
from .payment_factory import PaymentFactory
from app.models.order import OrderStatus
from app import db

import logging
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

def with_transaction(func):
    """✅ Decorator để quản lý transaction tự động."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Bắt đầu savepoint để có thể rollback
            db.session.begin_nested()
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transaction rolled back: {str(e)}")
            raise
    return wrapper

class OrderFacade:
    @staticmethod
    @with_transaction
    def place_order(user_id, items, payment_method):
        """
        ✅ Enhanced order placement với proper transaction management.
        
        Flow:
        1. Validate input
        2. Check stock (với thông tin chi tiết)
        3. Calculate total
        4. Create PENDING order
        5. Process payment (với retry)
        6. Reduce stock (với lock)
        7. Update to CONFIRMED
        """
        # ✅ Validate input
        if not items:
            return {
                "success": False,
                "error": "Cart is empty"
            }
        
        if not user_id:
            return {
                "success": False,
                "error": "User ID is required"
            }
        
        order_service = OrderService(db.session)
        inventory_service = InventoryService(db.session)

        try:
            # 1️⃣ Kiểm tra tồn kho
            logger.info(f"Checking stock for user {user_id}")
            insufficient = inventory_service.check_stock_bulk(items)
            
            if insufficient:
                # Tạo order FAILED nếu thiếu hàng
                failed_order = order_service.create_order(
                    user_id, items=[], total_amount=0, status=OrderStatus.FAILED.value
                )
                # inventory_service.release_reserved_stock(items)
                
                logger.warning(f"Order failed due to insufficient stock: {insufficient}")
                return {
                    "success": False,
                    "order_id": failed_order.id,
                    "error": "Insufficient stock",
                    "details": insufficient
                }


            # 2️⃣ Tính tổng tiền
            logger.info("Calculating order total")
            total = 0
            order_items = []
            for item in items:
                product = inventory_service.product_repo.get_by_id(item["product_id"])
                if not product:
                    raise ValueError(f"Product {item['product_id']} not found")
                total += float(product.price) * item["quantity"]
                order_items.append({
                    "product_id": product.id,
                    "quantity": item["quantity"],
                    "unit_price": product.price
                })

            # ✅ Validate total > 0
            if total <= 0:
                raise ValueError("Order total must be greater than 0")

            # 3️⃣ Tạo order PENDING
            logger.info(f"Creating PENDING order for user {user_id}, total: {total}")
            order = order_service.create_order(user_id, order_items, total, status=OrderStatus.PENDING.value)

            logger.info(f"Reserving inventory for PENDING order {order.id}")
            inventory_service.reserve_stock(items)

            logger.info(f"Order {order.id} created as PENDING. Awaiting payment.")

            return {
                "success": True,
                "order_id": order.id,
                "total": float(total),
                "status": OrderStatus.PENDING.value,
                "message": "Order created successfully. Please proceed to payment.",
            }

        except Exception as e:
            logger.error(f"Order placement failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Order placement failed: {str(e)}"
            }

    @staticmethod
    def _process_payment_with_retry(strategy, order_id, amount, max_retries=2):
        """✅ Retry payment với exponential backoff."""
        import time
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Payment attempt {attempt + 1}/{max_retries + 1}")
                result = strategy.pay(order_id, amount)
                
                if result.get("success"):
                    return result
                
                # Nếu fail và còn retry
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Payment failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    return result
                    
            except Exception as e:
                logger.error(f"Payment attempt {attempt + 1} error: {str(e)}")
                if attempt >= max_retries:
                    return {
                        "success": False,
                        "message": f"Payment failed after {max_retries + 1} attempts: {str(e)}"
                    }
                time.sleep(2 ** attempt)
    @staticmethod
    def get_order(order_id):
        try:
            order_service = OrderService()
            order = order_service.get_order_with_items(order_id)
            
            if not order:
                return {
                    "success": False, 
                    "error": "Order not found"
                }
            
            return {
                "success": True, 
                "data": order.to_dict()
            }
        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_user_orders(user_id):
        """ Get user orders"""
        try:
            order_service = OrderService()
            orders = order_service.get_orders_by_user(user_id)
            
            return {
                "success": True,
                "count": len(orders),
                "orders": [o.to_dict() for o in orders]
            }
        except Exception as e:
            logger.error(f"Failed to get orders for user {user_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def cancel_order(order_id, current_user_id, reason=None):
        """Cancel order and restock"""
        try:
            order_service = OrderService()
            inventory_service = InventoryService()
            
            order = order_service.get_order_with_items(order_id)
            if not order:
                return {
                    "success": False,
                    "error": "Order not found"
                }
            
            if order.user_id != current_user_id:
                return {
                    "success": False,
                    "error": "You are not authorized to cancel this order"
                }
            # Chỉ cho phép cancel nếu chưa ship
            if order.status not in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
                return {
                    "success": False,
                    "error": f"Cannot cancel order with status {order.status}"
                }
            
            # Restock
            for item in order.items:
                inventory_service.inventory_repo.increase_stock(
                    item.product_id, 
                    item.quantity
                )
            
            order_service.update_order_status(order_id, OrderStatus.CANCELLED.value)
            db.session.commit()
            
            logger.info(f"Order {order_id} cancelled. Reason: {reason}")
            
            return {
                "success": True,
                "message": "Order cancelled successfully",
                "refunded_items": len(order.items)
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        
    @staticmethod
    def pay_pending_order(order_id, current_user_id, payment_method):
        """Pay for a pending order"""
        try:
            order_service = OrderService()
            inventory_service = InventoryService()
            
            order = order_service.get_order_with_items(order_id)
            if not order:
                return {"success": False, "error": "Order not found"}
            
            # Checking order ownership
            if order.user_id != current_user_id:
                return {"success": False, "error": "Not authorized to pay this order"}
            
            # pay only for PENDING order
            if order.status != OrderStatus.PENDING.value:
                return {
                    "success": False,
                    "error": f"Order must be in 'pending' status. Current: {order.status}"
                }

            # Get items from order
            items = [
                {"product_id": item.product_id, "quantity": item.quantity}
                for item in order.items
            ]

            # Check quantity
            insufficient = inventory_service.check_stock_bulk(items)
            if insufficient:
                # order_service.update_order_status(order_id, OrderStatus.FAILED.value)
                # inventory_service.release_reserved_stock(items)
                # db.session.commit()
                return {
                    "success": False,
                    "error": "Insufficient stock at payment time",
                    "details": insufficient
                }

            # Proceed payment
            strategy = PaymentFactory.get_strategy(payment_method)
            payment_result = OrderFacade._process_payment_with_retry(
                strategy, order.id, float(order.total_amount), max_retries=3
            )

            if not payment_result.get("success"):
                # order_service.update_order_status(order_id, OrderStatus.FAILED.value)
                # inventory_service.release_reserved_stock(items)
                db.session.commit()
                return {
                    "success": False,
                    "order_id": order.id,
                    "error": "Payment failed",
                    "payment_details": payment_result
                }

            # reduce stock
            try:
                inventory_service.reduce_stock(items)
                inventory_service.release_reserved_stock(items)
            except Exception as e:
                # payment sucess but error in reduce stock
                order_service.update_order_status(order_id, OrderStatus.PAID.value)
                db.session.commit()
                return {
                    "success": False,
                    "error": "Payment succeeded but inventory update failed. Manual review required.",
                    "requires_manual_review": True
                }

            # Update status to PAID
            order_service.update_order_status(order_id, OrderStatus.PAID.value)
            db.session.commit()

            return {
                "success": True,
                "message": "Order paid successfully, waiting for confirmation...",
                "order_id": order.id,
                "payment_details": payment_result,
                "total": float(order.total_amount),
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to pay order {order_id}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
        
    @staticmethod
    def auto_cancel_pending_order(order_id, timeout_seconds=60):
        """
        Tự động hủy order PENDING sau timeout_seconds.
        - order_id: ID của order cần kiểm tra
        - timeout_seconds: thời gian tối đa chờ thanh toán (default 60s)
        """
        try:
            order_service = OrderService()
            inventory_service = InventoryService()

            order = order_service.get_order_with_items(order_id)
            if not order:
                return {"success": False, "error": "Order not found"}

            # Chỉ hủy PENDING
            if order.status != OrderStatus.PENDING.value:
                return {"success": False, "message": f"Order not PENDING. Status: {order.status}"}

            # Kiểm tra thời gian
            now = datetime.utcnow()
            if order.created_at + timedelta(seconds=timeout_seconds) > now:
                return {"success": False, "message": "Order is still within payment window"}

            # Restock
            for item in order.items:
                inventory_service.inventory_repo.increase_stock(item.product_id, item.quantity)

            # Update status
            order_service.update_order_status(order_id, OrderStatus.CANCELLED.value)
            db.session.commit()

            logger.info(f"Order {order_id} auto-cancelled after {timeout_seconds}s timeout")

            return {"success": True, "message": "Order auto-cancelled", "order_id": order_id}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to auto-cancel order {order_id}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}