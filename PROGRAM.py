import json
from dataclasses import asdict
from models import Product, Order, OrderItem
# 1. Load JSON Data
def load_data(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
        if "products" not in data or "orders" not in data:
            raise ValueError("JSON must contain products and orders")
        products = {}
        for product_id, product in data["products"].items():
            products[product_id] = Product(
                product_id=product_id,
                name=product["name"],
                price=product["price"],
                category=product["category"],
                stock=product["stock"]
            )
        orders = []
        for order in data["orders"]:
            items = []
            for item in order["items"]:
                items.append(
                    OrderItem(
                        product_id=item["product_id"],
                        quantity=item["quantity"]
                    )
                )
            orders.append(
                Order(
                    order_id=order["order_id"],
                    customer=order["customer"],
                    items=items,
                    payment_status=order["payment_status"]
                )
            )
        return products, orders
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return {}, []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
        return {}, []
    except ValueError as error:
        print("Error:", error)
        return {}, []
# 2. Save JSON Data
def save_data(filename, products, orders):
    try:
        data = {
            "products": {
                product_id: asdict(product)
                for product_id, product in products.items()
            },
            "orders": [
                asdict(order)
                for order in orders
            ]
        }
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print("Data saved successfully.")
    except PermissionError:
        print("Error: Permission denied.")
    except OSError as error:
        print("Error while saving file:", error)
# 3. Validate Orders
def validate_order(order, products, check_stock=True):
    try:
        if not order.items:
            raise ValueError("Order has no items.")
        if not order.payment_status:
            raise ValueError("Payment status is missing.")
        for item in order.items:
            if not item.product_id:
                raise ValueError("Product ID is missing.")
            if item.product_id not in products:
                raise ValueError(
                    f"Invalid product ID: {item.product_id}"
                )
            if not isinstance(item.quantity, int) or item.quantity <= 0:
                raise ValueError(
                    "Quantity must be a positive integer."
                )
            if check_stock:
                if item.quantity > products[item.product_id].stock:
                    raise ValueError(
                        f"Not enough stock for {item.product_id}"
                    )
        return True
    except (ValueError, TypeError, KeyError) as error:
        print("Order validation error:", error)
        return False
# 4. Calculate Order Subtotal
def calculate_order_subtotal(order, products):
    sub_total = 0
    for item in order.items:
        product = products[item.product_id]
        sub_total += product.price * item.quantity
    return sub_total
# 5. Apply Discounts
def calculate_discount(subtotal):
    if subtotal >= 1000:
        discount = subtotal * 15 / 100
    elif subtotal >= 500:
        discount = subtotal * 10 / 100
    elif subtotal >= 200:
        discount = subtotal * 5 / 100
    else:
        discount = 0
    return discount
# 6. Calculate Shipping
def Calculate_Shipping(subtotal):
    if subtotal >= 500:
        shipping = 0
    else:
        shipping = 20
    return shipping
# 7. Calculate Total
def calculate_total(*amounts):
    total = 0
    for amount in amounts:
        total += amount
    return total
# 8. Payment Handling
def process_order(order, products, **kwargs):
    if not validate_order(order, products):
        return 0
    if order.payment_status != "paid":
        return 0
    subtotal = calculate_order_subtotal(
        order,
        products
    )
    discount = 0
    shipping = 0
    if kwargs.get("apply_discount", False):
        discount = calculate_discount(subtotal)
    if kwargs.get("include_shipping", False):
        shipping = Calculate_Shipping(subtotal)
    total = calculate_total(
        subtotal,
        -discount,
        shipping
    )
    return total
# 9. Update Inventory
def update_inventory(order, products):
    if not validate_order(order, products):
        return
    if order.payment_status != "paid":
        return
    for item in order.items:
        products[item.product_id].stock -= item.quantity
# 10. Generate Reports
def generate_report(orders, products):
    total_orders = len(orders)
    paid_orders = 0
    pending_orders = 0
    rejected_orders = 0
    total_revenue = 0
    total_discount = 0
    total_shipping = 0
    customer_sales = {}
    product_sales = {}
    unique_customers = set()
    for order in orders:
        if not validate_order(order, products, check_stock=False):
            rejected_orders += 1
            continue
        if order.payment_status == "pending":
            pending_orders += 1
            continue
        if order.payment_status == "paid":
            paid_orders += 1
            customer = order.customer
            unique_customers.add(customer)
            subtotal = calculate_order_subtotal(
                order,
                products
            )
            discount = calculate_discount(subtotal)
            shipping = Calculate_Shipping(subtotal)
            revenue = process_order(
                order,
                products,
                apply_discount=True,
                include_shipping=True
            )
            total_revenue += revenue
            total_discount += discount
            total_shipping += shipping
            if customer not in customer_sales:
                customer_sales[customer] = 0
            customer_sales[customer] += revenue
            for item in order.items:
                product_id = item.product_id
                quantity = item.quantity
                if product_id not in product_sales:
                    product_sales[product_id] = 0
                product_sales[product_id] += quantity
    low_stock_products = [
        product.name
        for product in products.values()
        if product.stock < 10
    ]
    print("\n========== SALES REPORT ==========")
    print("Total Orders:", total_orders)
    print("Paid Orders:", paid_orders)
    print("Pending Orders:", pending_orders)
    print("Rejected Orders:", rejected_orders)
    print("Total Revenue: $", total_revenue)
    print("Total Discount: $", total_discount)
    print("Total Shipping: $", total_shipping)
    if customer_sales:
        top_customer = max(
            customer_sales.items(),
            key=lambda x: x[1]
        )
        print("Top Customer:", top_customer[0])
    else:
        print("Top Customer: None")
    if product_sales:
        top_product = max(
            product_sales.items(),
            key=lambda x: x[1]
        )
        product_id = top_product[0]
        print(
            "Top Selling Product:",
            products[product_id].name
        )
    else:
        print("Top Selling Product: None")
    print("Low Stock Products:")
    if low_stock_products:
        for product in low_stock_products:
            print("-", product)
    else:
        print("None")
    print("Unique Customers:", unique_customers)
    print("==================================")
# Main Program
if __name__ == "__main__":
    products, orders = load_data("data.json")
    if products and orders:
        for order in orders:
            if order.payment_status == "paid":
                total = process_order(
                    order,
                    products,
                    apply_discount=True,
                    include_shipping=True
                )
                if total > 0:
                    update_inventory(
                        order,
                        products
                    )
        generate_report(
            orders,
            products
        )
        save_data(
            "data.json",
            products,
            orders
        )
    else:
        print("No data available.")
