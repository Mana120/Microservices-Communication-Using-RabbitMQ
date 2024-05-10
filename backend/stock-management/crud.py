def order_status(connection, order):
    try:
        if connection.is_connected():
            cursor = connection.cursor()

            product_id = order.get("Product_ID", "")
            quantity = order.get("Quantity", 0)  # Assuming default quantity is 0

            # SQL query to check if the given quantity is greater than the quantity in storage
            storage_query = "SELECT Quantity FROM Storage WHERE Product_ID = %s"
            cursor.execute(storage_query, (product_id,))
            storage_quantity = cursor.fetchone()[0]

            # Check if the given quantity is greater than the quantity in storage
            if quantity < storage_quantity:
                result = 'True'
            else:
                result = 'False'
            
            # Commit the transaction
            connection.commit()
            if result == 'True':
                reduce_quantity(connection,order)
            # Return the result
            return result

    except Exception as e:
        print("Error Inserting Order:", e)
        return None
    
def reduce_quantity(connection, order):
    try:
        if connection.is_connected():
            # Define the SQL query to update the quantity in the Storage table
            product_id = order.get("Product_ID", "")
            quantity = order.get("Quantity", 0)
            query = '''
                UPDATE Storage
                SET Quantity = Quantity - %s
                WHERE Product_ID = %s;
            '''
            cursor = connection.cursor()

            # Execute the SQL query with parameters
            cursor.execute(query, (quantity, product_id))

            #If threshold greater than quantity
            cursor.execute("SELECT Quantity, Threshold, Restock_Time FROM Storage WHERE Product_ID = %s", (product_id,))
            storage_data = cursor.fetchone()
            current_quantity, threshold, Restock_Time = storage_data
            if current_quantity < threshold:
                insert_restock(connection,order,threshold - current_quantity, Restock_Time, "Storage")
            # Commit the transaction
            connection.commit()
            print("Quantity reduced successfully")

    except Exception as e:
        print("Error reducing quantity:", e)


def insert_restock_request(connection, restock_request):
    try:
        if connection.is_connected():
            cursor = connection.cursor()

            # Extract data from the restock_request dictionary
            product_id = restock_request.get("Product_ID", "")
            order_id = restock_request.get("Order_ID", "")
            date_time = restock_request.get("Date_Time", "")
            quantity = restock_request.get("Quantity", "")

            # Define the SQL query to insert into the Restock_Requests table
            query = '''
                INSERT INTO Restock_Requests (Product_ID, Type, Order_ID, Date_Time, Status, Quantity)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''

            # Execute the SQL query with parameters
            cursor.execute(query, (product_id, "Order", order_id, date_time, "In Progress", quantity))

            # Commit the transaction
            connection.commit()

            print("Restock request inserted successfully")

    except Exception as e:
        print("Error inserting restock request:", e)

def get_restock_time(connection, product_id):
    try:
        if connection.is_connected():
            cursor = connection.cursor()

            # Define the SQL query to retrieve the restock time from the Storage table
            query = "SELECT Restock_Time FROM Storage WHERE Product_ID = %s"

            # Execute the SQL query with parameters
            cursor.execute(query, (product_id,))

            # Fetch the result
            result = cursor.fetchone()

            if result:
                restock_time = result[0]
                return restock_time
            else:
                print("Product not found in storage")
                return None

    except Exception as e:
        print("Error retrieving restock time:", e)
        return None

def get_storage_quantity(connection, product_id):
    try:
        if connection.is_connected():
            cursor = connection.cursor()

            # Define the SQL query to retrieve the quantity from the Storage table
            query = '''
                SELECT Quantity
                FROM Storage
                WHERE Product_ID = %s;
            '''

            # Execute the SQL query with parameters
            cursor.execute(query, (product_id,))

            # Fetch the result
            result = cursor.fetchone()

            if result:
                return result[0]  # Return the quantity
            else:
                print("Product not found in Storage table")
                return None

    except Exception as e:
        print("Error retrieving quantity from Storage table:", e)
        return None

def insert_restock(connection, order, quantity, time, type):
    try:
        if connection.is_connected():
            # Extract values from the order dictionary
            order_id = order.get("Order_ID", "")
            product_id = order.get("Product_ID", "")

            # Define the SQL query to insert restock request
            query = """
                INSERT INTO Restock_Requests 
                (Product_ID, Type, Order_ID, Date_Time, Status, Quantity) 
                VALUES (%s, %s, %s, DATE_ADD(NOW(), INTERVAL %s SECOND), %s, %s)
            """
            cursor = connection.cursor()

            # Execute the SQL query
            cursor.execute(query, (product_id, type, order_id, time * quantity, "In Progress", quantity))

            # Commit the transaction
            connection.commit()
            print("Restock inserted successfully")

    except Exception as e:
        print("Error Inserting Restock:", e)






