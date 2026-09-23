def calculate_discount_percent(old_price: int, new_price: int) -> int:
    if not old_price or old_price <= new_price:
        return 0
    return round(((old_price - new_price) / old_price) * 100)
