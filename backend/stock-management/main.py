import os
import crud
import pika
import json
import time
import threading
import mysql.connector
import crud
import datetime

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

    channel.queue_declare(queue='CheckStock')
    channel.queue_declare(queue='StockAvailable')

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        print("--------------------------------------------------")
        print("Received message on CheckStock Queue:", message)

        # Message Format: {Order_ID: str, Product_ID: str, Quantity: int}
        # Process Message
        order = {}
        order["Order_ID"] = message.get('Order_ID')
        order["Product_ID"] = message.get('Product_ID')
        order["Quantity"] = message.get('Quantity')

        connection = get_connection()

        if connection:
            # DO STUFF
            # Database Operations
            result = crud.order_status(connection, order)
            # Publish Message to StockAvailable
            # Message Format: {Order_ID: str, Available: bool}
            if result == "True":
                print(f"Publishing message to StockAvailable Queue.")
                data_to_publish = json.dumps({"Order_ID": order["Order_ID"], "Available": "yes"})
                channel.basic_publish(
                    exchange = '',
                    routing_key = 'StockAvailable',
                    body = data_to_publish
                )
            else:
                print(f"Publishing message to StockAvailable Queue.")
                data_to_publish = json.dumps({"Order_ID": order["Order_ID"], "Available": "no"})
                channel.basic_publish(
                    exchange = '',
                    routing_key = 'StockAvailable',
                    body = data_to_publish
                )
                # crud.insert_order(connection, order)
                restock_time = crud.get_restock_time(connection, order["Product_ID"])
                existing_quantity = crud.get_storage_quantity(connection, order["Product_ID"])
                if restock_time is not None:
                    current_time = datetime.datetime.now()
                    minutes_to_add = (order["Quantity"]) * restock_time
                    new_date_time = current_time + datetime.timedelta(minutes=minutes_to_add)
                    request = {
                    "Product_ID": order["Product_ID"],
                    "Order_ID": order["Order_ID"],
                    "Date_Time": new_date_time,
                    "Quantity": order["Quantity"]
                    }
                    crud.insert_restock_request(connection, request)


        print("--------------------------------------------------\n")

    channel.basic_consume(queue='CheckStock', on_message_callback=callback, auto_ack=True)
    print()
    print("--------------------------------------------------")
    print("            Listening For Messages")
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
    message = json.dumps({"Microservice_Name": "stock-management"})

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
    print("       Stock-Management Microservice Running")
    print("##################################################")
    print()

    listen_thread = threading.Thread(target=listen_for_requests)
    heartbeat_thread = threading.Thread(target=heartbeat)

    listen_thread.start()
    heartbeat_thread.start()

    listen_thread.join()
    heartbeat_thread.join()
