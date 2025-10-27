TIMEOUT_SECONDS=60
INTERVAL_SECONDS=60
# app/tasks/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.order_facade import OrderFacade
from app.services.order_service import OrderService
from app.logger_config import setup_logger

logger = setup_logger(name="scheduler", log_file="app/logs/scheduler.log")

def start_scheduler(app, timeout_seconds=TIMEOUT_SECONDS, interval_seconds=INTERVAL_SECONDS):
    scheduler = BackgroundScheduler()

    def auto_cancel_orders():
        with app.app_context():
            try:
                pending_orders = OrderService().get_pending_orders()
                logger.info(f"Checking {len(pending_orders)} pending orders...")
                for order in pending_orders:
                    result = OrderFacade.auto_cancel_pending_order(order.id, timeout_seconds=timeout_seconds)
                    if result.get("success"):
                        logger.info(f"Order {order.id} auto-cancelled.")
                    else:
                        logger.info(f"Order {order.id} not cancelled: {result.get('message')}")
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}", exc_info=True)

    scheduler.add_job(auto_cancel_orders, 'interval', seconds=interval_seconds, id='auto_cancel_orders')
    scheduler.start()
    logger.info(f"Scheduler started: check every {interval_seconds}s with timeout {timeout_seconds}s.")
