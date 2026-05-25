import json
import csv
from datetime import datetime
from collections import defaultdict

def read_users():
    with open('users.json', 'r') as f:
        return {user['id']: user for user in json.load(f)}

def read_products():
    with open('products.json', 'r') as f:
        return {prod['id']: prod for prod in json.load(f)}

def read_and_clean_orders():
    seen = set()
    cleaned = []
    products = read_products()
    with open('orders.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order_id = row['order_id']
            if order_id in seen:
                continue
            seen.add(order_id)
            amount = row['amount'].strip()
            if not amount:
                continue
            try:
                amount_float = float(amount)
            except ValueError:
                continue
            date_str = row['date']
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                month = dt.strftime('%Y-%m')
            except ValueError:
                continue
            cleaned.append({
                'order_id': order_id,
                'user_id': int(row['user_id']),
                'product': row['product'],
                'amount': amount_float,
                'month': month
            })
    return cleaned

def main():
    users = read_users()
    products = read_products()
    orders = read_and_clean_orders()
    
    # 1. user LTV
    user_totals = defaultdict(float)
    for order in orders:
        user_totals[order['user_id']] += order['amount']
    
    ltv_rows = []
    for uid, total in user_totals.items():
        user = users.get(uid)
        name = user['name'] if user else 'Unknown'
        ltv_rows.append({
            'user_id': uid,
            'name': name,
            'total_amount': round(total, 2)
        })
    ltv_rows.sort(key=lambda x: x['total_amount'], reverse=True)
    with open('user_ltv.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'name', 'total_amount'])
        writer.writeheader()
        writer.writerows(ltv_rows)
    
    # 2. category sales
    cat_sales = defaultdict(float)
    for order in orders:
        prod = products.get(order['product'])
        if prod:
            cat_sales[prod['category']] += order['amount']
    cat_dict = {cat: round(amt, 2) for cat, amt in cat_sales.items()}
    with open('category_sales.json', 'w') as f:
        json.dump(cat_dict, f, indent=2)
    
    # 3. monthly orders
    monthly_counts = defaultdict(int)
    for order in orders:
        monthly_counts[order['month']] += 1
    month_rows = [{'month': m, 'order_count': c} for m, c in sorted(monthly_counts.items())]
    with open('monthly_orders.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['month', 'order_count'])
        writer.writeheader()
        writer.writerows(month_rows)

if __name__ == '__main__':
    main()