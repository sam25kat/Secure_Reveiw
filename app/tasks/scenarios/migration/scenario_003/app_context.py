# checkout_service/order_processor.py
class OrderProcessor:
    def create_order(self, user_id: int, items: list):
        """Create a new order - high-throughput path (500 writes/sec)."""
        order = self.db.execute(
            "INSERT INTO orders (user_id, total_amount, status) "
            "VALUES (%s, %s, 'pending') RETURNING id",
            user_id, self.calculate_total(items)
        )
        for item in items:
            self.db.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
                "VALUES (%s, %s, %s, %s)",
                order.id, item.product_id, item.quantity, item.unit_price
            )
        return order


# analytics_service/reporting.py
class OrderAnalytics:
    def daily_revenue_report(self):
        """Generate daily revenue report - reads order_items extensively."""
        return self.db.query(
            "SELECT DATE(o.created_at), SUM(oi.unit_price * oi.quantity) "
            "FROM orders o JOIN order_items oi ON oi.order_id = o.id "
            "WHERE o.created_at > NOW() - INTERVAL '30 days' "
            "GROUP BY DATE(o.created_at)"
        )
