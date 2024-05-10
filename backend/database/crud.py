import json

def read_products(connection):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            select_query = f"SELECT * FROM Product;"
            cursor.execute(select_query)
            products = cursor.fetchall()
            cursor.close()

            products_dict = []
            for product in products:
                product_dict = {
                    "Product_ID": product[0],
                    "Name": product[1],
                    "Description": product[2],
                    "Price": product[3]
                }
                products_dict.append(product_dict)

            # Convert list of dictionaries to JSON
            products_json = json.dumps(products_dict, indent=4)

            # print("Products Fetched:")
            # print(products_json)

            return products_json

    except Exception as e:
        print("Error Fetching Products:", e)

def read_orders(connection, customer_id):
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            select_query = f"""SELECT * FROM Orders WHERE Customer_ID = '{customer_id}'
                            ORDER BY Order_ID;"""
            cursor.execute(select_query)
            orders = cursor.fetchall()
            cursor.close()

            orders_dict = []
            for order in orders:
                order_dict = {
                    "Order_ID": order[0],
                    "Customer_ID": order[1],
                    "Product_ID": order[2],
                    "Quantity": order[3],
                    "Status": order[4]
                }
                orders_dict.append(order_dict)

            # Convert list of dictionaries to JSON
            orders_json = json.dumps(orders_dict, indent=4)

            # print("Orders Fetched:")
            # print(orders_json)

            return orders_json

    except Exception as e:
        print("Error Fetching Orders:", e)