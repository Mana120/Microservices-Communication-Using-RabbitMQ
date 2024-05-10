import os
import ddl
import crud
import pika
import json
import time
import threading
import mysql.connector

port = 3406
password = "password"

def database_init():
    try:
        # Connect to MySQL database using host machine's IP address
        connection = mysql.connector.connect(
            host = "host.docker.internal",
            port = port,
            user = "root",
            password = password
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            ddl.create_db_if_not_exists( connection, "Inventory_DB")
            ddl.create_event(connection)
    except mysql.connector.Error as error:
        print("Failed to connect to MySQL Server:", error)

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

    channel.queue_declare(queue='Read')
    channel.queue_declare(queue='Data')

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        print("--------------------------------------------------")
        print("Received message:", message)

        request_type = message.get('type')

        if request_type == "read_products":
            connection = get_connection()
            if connection:
                products_json = crud.read_products(connection)
                if products_json:
                    print("Publishing products to Data Queue.")
                    data_to_publish = json.dumps({"table": "products", "data": products_json})
                    channel.basic_publish(
                        exchange='',
                        routing_key='Data',
                        body=data_to_publish
                    )
        elif request_type == "read_orders":
            connection = get_connection()
            if connection:
                customer_id = message.get('customer_id')
                orders_json = crud.read_orders(connection, customer_id)
                if orders_json:
                    print(f"Publishing orders of Customer {customer_id} to Data Queue.")
                    data_to_publish = json.dumps({"table": "orders", "data": orders_json, "customer_id": customer_id})
                    channel.basic_publish(
                        exchange='',
                        routing_key='Data',
                        body=data_to_publish
                    )
        print("--------------------------------------------------\n")

    channel.basic_consume(queue='Read', on_message_callback=callback, auto_ack=True)
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
    message = json.dumps({"Microservice_Name": "database"})

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
    print("         Database Microservice Running")
    print("##################################################")
    print()

    database_init()

    listen_thread = threading.Thread(target=listen_for_requests)
    heartbeat_thread = threading.Thread(target=heartbeat)

    listen_thread.start()
    heartbeat_thread.start()

    listen_thread.join()
    heartbeat_thread.join()
