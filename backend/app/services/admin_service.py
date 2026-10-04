from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import (User, Product, Category, Order, Payment, OrderStatus, PaymentStatus)
from app.schemas import DashboardResponse


def get_dashboard_data(db: Session) -> DashboardResponse:

    # User counts
    user_counts = (
        db.query(
            func.count(User.id).label("total_users"),
            func.count(User.id)
            .filter(User.is_active.is_(True))
            .label("active_users"),
        )
        .one()
    )

    # Product counts
    product_counts = (db.query(func.count(Product.id).label("total_products"), func.count(Product.id)
            .filter(Product.is_active.is_(True))
            .label("active_products"),
        )
        .one()
    )

    # Category counts
    category_counts = (
        db.query(
            func.count(Category.id).label("total_categories"),
            func.count(Category.id)
            .filter(Category.is_active.is_(True))
            .label("active_categories"),
        )
        .one()
    )

    # Order counts grouped by status
    order_counts = (db.query(Order.status, func.count(Order.id).label("count")).group_by(Order.status).all())

    order_count_map = {
        status: count
        for status, count in order_counts
    }

    # Payment counts grouped by status
    payment_counts = (db.query(Payment.status, func.count(Payment.id).label("count")).group_by(Payment.status).all())

    payment_count_map = {
        status: count
        for status, count in payment_counts
    }

    dashboard_data = DashboardResponse(
        total_users=user_counts.total_users or 0,
        active_users=user_counts.active_users or 0,

        total_products=product_counts.total_products or 0,
        active_products=product_counts.active_products or 0,

        total_categories=category_counts.total_categories or 0,
        active_categories=category_counts.active_categories or 0,

        pending_orders=order_count_map.get(OrderStatus.PENDING, 0),
        confirmed_orders=order_count_map.get(OrderStatus.CONFIRMED, 0),
        preparing_orders=order_count_map.get(OrderStatus.PREPARING, 0),
        out_for_delivery_orders=order_count_map.get(OrderStatus.OUT_FOR_DELIVERY, 0),
        delivered_orders=order_count_map.get(OrderStatus.DELIVERED, 0),
        cancelled_orders=order_count_map.get(OrderStatus.CANCELLED, 0),

        pending_payments=payment_count_map.get(PaymentStatus.PENDING, 0),
        paid_payments=payment_count_map.get(PaymentStatus.PAID, 0),
    )

    return dashboard_data