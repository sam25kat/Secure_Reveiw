# pricing_service/price_calculator.py
class PriceCalculator:
    def calculate_discount(self, product_id: int) -> float:
        """Calculate discount based on old vs current price."""
        product = self.db.query(
            "SELECT old_price, current_price FROM products WHERE id = %s",
            product_id
        )
        if product.old_price and product.old_price > product.current_price:
            return (product.old_price - product.current_price) / product.old_price
        return 0.0


# audit_service/audit_logger.py
class AuditLogger:
    def log_action(self, user_id: int, session_id: int, action: str, details: dict):
        """Log an audit event - references sessions table via FK."""
        self.db.execute(
            "INSERT INTO audit_log (user_id, session_id, action, details) "
            "VALUES (%s, %s, %s, %s)",
            user_id, session_id, action, json.dumps(details)
        )

    def get_session_audit_trail(self, session_id: int):
        """Get all actions for a session."""
        return self.db.query(
            "SELECT a.*, s.token FROM audit_log a "
            "JOIN sessions s ON s.id = a.session_id "
            "WHERE a.session_id = %s ORDER BY a.created_at",
            session_id
        )


# catalog_service/product_manager.py
class ProductManager:
    def update_product_price(self, product_id: int, new_price: float):
        """Update product price, storing old price for reference."""
        self.db.execute(
            "UPDATE products SET old_price = current_price, current_price = %s WHERE id = %s",
            new_price, product_id
        )
