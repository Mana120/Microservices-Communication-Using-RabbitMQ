package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/streadway/amqp"
)

const (
	databaseThreshold = 15 
	order_processingThreshold = 15 
	producerThreshold = 15
	stock_managementThreshold = 15
)

var (
	lastMessageTimedatabase         time.Time
	lastMessageTimeorder_processing time.Time
	lastMessageTimeproducer         time.Time
	lastMessageTimestock_management time.Time
	mutex                           sync.Mutex
)

type Message struct {
	MicroserviceName string `json:"Microservice_Name"`
}

func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

func handleMessages(d amqp.Delivery) {
	var message Message
	err := json.Unmarshal(d.Body, &message)
	if err != nil {
		log.Printf("Error decoding message: %s", err)
		return
	}

	mutex.Lock()
	defer mutex.Unlock()

	switch message.MicroserviceName {
	
	case "database":
		
		lastMessageTimedatabase = time.Now()
		break
		
		
	case "Order_Processing":
		lastMessageTimeorder_processing = time.Now()
		break
	
	case "producer":
		lastMessageTimeproducer = time.Now()
		break
	case "stock-management":
		lastMessageTimestock_management = time.Now()
		break
	

	}
	fmt.Printf("Heartbeat Recieved : %s\n",message.MicroserviceName)
}

func checkProducers() {
	for {
		time.Sleep(10 * time.Second) // Check every 30 seconds

		mutex.Lock()
		currentTime := time.Now()
		
		
		
		if currentTime.Sub(lastMessageTimeorder_processing) > order_processingThreshold*time.Second {
			fmt.Println("Order Processing is not working")
		}
		if currentTime.Sub(lastMessageTimedatabase) > databaseThreshold*time.Second {
			fmt.Println("Database is not working")
		}
		if currentTime.Sub(lastMessageTimeproducer) > producerThreshold*time.Second {
			fmt.Println("Producer is not working")
		}

		if currentTime.Sub(lastMessageTimestock_management) > stock_managementThreshold*time.Second {
			fmt.Println("Stock Management is not working")
		}

		mutex.Unlock()
	}
}

func main() {
	fmt.Println("##################################################")
	fmt.Println("         Healthcheck Microservice Running")
	fmt.Println("##################################################")
	fmt.Println()

	conn, err := amqp.Dial("amqp://guest:guest@rabbitmq:5672/")
	failOnError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	ch, err := conn.Channel()
	failOnError(err, "Failed to open a channel")
	defer ch.Close()

	q, err := ch.QueueDeclare(
		"HealthCheck", // Queue name
		false,         // Durable
		false,         // Delete when unused
		false,         // Exclusive
		false,         // No-wait
		nil,           // Arguments
	)
	failOnError(err, "Failed to declare a queue")

	msgs, err := ch.Consume(
		q.Name, // queue
		"",     // consumer
		true,   // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // args
	)
	failOnError(err, "Failed to register a consumer")

	go checkProducers()

	for d := range msgs {
		handleMessages(d)
	}
	fmt.Println("--------------------------------------------------")
	fmt.Println("		Consumer started. To exit press CTRL+C")
	fmt.Println("--------------------------------------------------")
	signalCh := make(chan os.Signal, 1)
	signal.Notify(signalCh, syscall.SIGINT, syscall.SIGTERM)
	<-signalCh
	fmt.Println("Shutting down...")
}
