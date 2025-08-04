import random
import uuid

import pandas as pd
from faker import Faker

fake = Faker()


def random_warehouse_id():
    """Our warehouses are nigeria.
    We have 10 warehouses per region in nigeria"""
    regions = ["east", "west", "north", "south"]
    return f"ng-{random.choice(regions)}-{random.randint(a=1, b=10)}"


def generate_transaction_data(min_rows: int, max_rows: int):

    total_transactions = random.randint(a=min_rows, b=max_rows)

    print(f"Generating {total_transactions} transactions, please wait . . .")

    customer_ids = [
        str(uuid.uuid4()) for _ in range(200_000)
    ]  # Total unique customers make up 50%
    product_ids = [
        str(uuid.uuid4()) for _ in range(10_000)
    ]  # Total unique products is 1000

    states = [
        "Lagos",
        "Abia",
        "Adamawa",
        "Akwa Ibom",
        "Anambra",
        "Bauchi",
        "Bayelsa",
        "Benue",
        "Borno",
        "Cross River",
        "Delta",
        "Ebonyi",
        "Edo",
        "Ekiti",
        "Enugu",
        "Gombe",
        "Imo",
        "Jigawa",
        "Kaduna",
        "Kano",
        "Katsina",
        "Kebbi",
        "Kogi",
        "Kwara",
        "Lagos",
        "Nasarawa",
        "Niger",
        "Ogun",
        "Ondo",
        "Osun",
        "Oyo",
        "Plateau",
        "Rivers",
        "Sokoto",
        "Taraba",
        "Yobe",
        "Zamfara",
        "FCT",
    ]

    records = []
    for i in range(total_transactions):
        tx_id = str(uuid.uuid4())
        customer_id = random.choice(customer_ids)
        product_id = random.choice(product_ids)
        order_date = fake.date_time_between(start_date="-1d", end_date="now")
        quantity = random.randint(1, 10)
        unit_price = random.randint(1_000, 1_000_000)
        total_amount = quantity * unit_price
        payment_method = random.choice(["debit_card", "bank_transfer"])
        payment_status = random.choice(
            ["paid", "pending", "failed", "refunded"]
        )
        shipping_warehouse = random_warehouse_id()
        shipping_cost = random.randint(1_000, 5_000)
        order_status = random.choice(
            ["placed", "shipped", "delivered", "returned"]
        )
        customer_country = "NG"
        customer_state = random.choice(states)

        records.append(
            {
                "transaction_id": tx_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "order_date": order_date,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount_naira": total_amount,
                "payment_method": payment_method,
                "payment_status": payment_status,
                "shipping_warehouse": shipping_warehouse,
                "shipping_cost": shipping_cost,
                "order_status": order_status,
                "customer_country": customer_country,
                "customer_state": customer_state,
            }
        )
    print("Data Generaton Successful")

    return pd.DataFrame(records)
