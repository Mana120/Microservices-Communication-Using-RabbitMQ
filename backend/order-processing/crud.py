import json

def insert_order(connection, order):
    try:
        if connection.is_connected():
            # Insert Order to Database here
            query = "INSERT INTO Orders (Order_ID, Customer_ID, Product_ID, Quantity,Status) VALUES (%s, %s, %s, %s,%s)"
            cursor = connection.cursor()

            # Extract values from the order dictionary
            order_id = order.get("Order_ID", "")
            customer_id = order.get("Customer_ID", "")
            product_id = order.get("Product_ID", "")
            quantity = order.get("Quantity", 0)  # Assuming default quantity is 0

            # Execute the SQL query
            cursor.execute(query, (order_id, customer_id, product_id, quantity,"In Progress"))

            # Commit the transaction
            connection.commit()
            print("Order inserted successfully")
            
    except Exception as e:
        print("Error Inserting Order:", e)

def update_order(connection, order_id):
    try:
        if connection.is_connected():
           # Update order status to 'Completed'
            query = "UPDATE Orders SET Status = 'Complete' WHERE Order_ID = %s"
            cursor = connection.cursor()
            cursor.execute(query, (order_id,))
            connection.commit()
            print("Order status updated to 'Completed'")
    except Exception as e:
        print("Error Updating Status:", e)
