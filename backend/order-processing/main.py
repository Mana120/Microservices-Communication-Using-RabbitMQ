import os
import crud
import pika
import json
import mysql.connector
import threading
import time

port = 3406
password = "password"

def get_connection():
    try:
        # Connect to MySQL database using host machine's IP address
        connection = mysql.connector.connect(
            host = "host.docker.internal",
            port = port,
            user = "root",
            password = password,
            database = "Inventory_DB"
        )
        if connection.is_connected():
            return connection

    except mysql.connector.Error as error:
        print("Failed to connect to MySQL database:", error)

def listen_for_requests():

    amqp_url = os.environ['AMQP_URL']
    url_params = pika.URLParameters(amqp_url)

    rabbitmq_connection = pika.BlockingConnection(url_params)
    channel = rabbitmq_connection.channel()

    channel.queue_declare(queue='New_Order')
    channel.queue_declare(queue='CheckStock')
    channel.queue_declare(queue='StockAvailable')

    def callback_New_Order(ch, method, properties, body):
        message = json.loads(body.decode())
        print("--------------------------------------------------")
        print("Received message:", message)

        # Create an empty order dictionary
        order = {}

        # Assign values from the message to the order dictionary based on keys
        order["Order_ID"] = message.get("Order_ID", "")
        order["Customer_ID"] = message.get("Customer_ID", "")
        order["Product_ID"] = message.get("Product_ID", "")
        order["Quantity"] = message.get("Quantity", "")

        connection = get_connection()
        if connection:
            # Insert Order to DB
            print("Sending order info to Orders Table")

            crud.insert_order(connection, order)

            # Data give to stock
            data_to_publish = {}
            data_to_publish["Order_ID"] = order["Order_ID"]
            data_to_publish["Product_ID"] = order["Product_ID"]
            data_to_publish["Quantity"] = order["Quantity"]
            print("Sending order info to Stock Queue")

            # Convert the `order` dictionary to a JSON string
            data_to_publish_json = json.dumps(data_to_publish)
            print(data_to_publish_json)

            # Publish message to CheckStock Queue
            channel.basic_publish(
                exchange='',
                routing_key='CheckStock',
                body=data_to_publish_json
            )
        print("--------------------------------------------------")

    def callback_StockAvailable(ch, method, properties, body):
        message = json.loads(body.decode())
        print("--------------------------------------------------")
        print("Received message:", message)

        # Assign values from the message to the order dictionary based on keys
        Order_ID = message.get("Order_ID", "")
        flag = message.get("Available", "")

        print("Hello")
        connection = get_connection()
        if connection and flag == "yes":
            print("Bye")
            # Insert Order to DB
            print("Updating info to Orders Table")
            crud.update_order(connection, Order_ID)
        print("--------------------------------------------------")

    channel.basic_consume(queue='New_Order', on_message_callback=callback_New_Order, auto_ack=True)
    channel.basic_consume(queue='StockAvailable', on_message_callback=callback_StockAvailable, auto_ack=True)
    print()
    print("--------------------------------------------------")
    print("            Listening For Read Requests")
    print("--------------------------------------------------")
    print()
    print('Waiting for messages..')
    channel.start_consuming()

def heartbeat():
    print("--------------------------------------------------")
    print("              Heartbeat Initialized")
    print("--------------------------------------------------")
    amqp_url = os.environ['AMQP_URL']
    url_params = pika.URLParameters(amqp_url)

    rabbitmq_connection = pika.BlockingConnection(url_params)
    channel = rabbitmq_connection.channel()

    channel.queue_declare(queue='HealthCheck')
    message = json.dumps({"Microservice_Name": "Order_Processing"})

    while True:
        channel.basic_publish(
            exchange='',
            routing_key='HealthCheck',
            body = message
        )
        print(" [x] Heartbeat Sent: ", message)
        time.sleep(10)

if __name__ == "__main__":
    print("##################################################")
    print("       Order-Processing Microservice Running")
    print("##################################################")
    print()
    listen_thread = threading.Thread(target=listen_for_requests)
    heartbeat_thread = threading.Thread(target=heartbeat)

    listen_thread.start()
    heartbeat_thread.start()

    listen_thread.join()
    heartbeat_thread.join()


