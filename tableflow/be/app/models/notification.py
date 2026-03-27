from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey, DateTime, func
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum("order_received", "order_ready", "order_cancelled", "general"), nullable=False, default="general")
    is_read = Column(Boolean, nullable=False, default=False)
    related_order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
