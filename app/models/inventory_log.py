from app import db
from datetime import datetime

class InventoryLog(db.Model):
    __tablename__ = "inventory_logs"
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False, index=True)
    change = db.Column(db.Integer, nullable=False)  # positive for restock, negative for purchase
    before = db.Column(db.Integer, nullable=False)
    after = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.Index('idx_invlog_product_time', 'inventory_id', 'created_at'),)
