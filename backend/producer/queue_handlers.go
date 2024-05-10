package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/streadway/amqp"
)

type Message struct {
	Type       string `json:"type"`
	CustomerID string `json:"customer_id"`
}
type Heartbeat struct {
	Microservice_name string `json:"Microservice_Name"`
}

var ProductsMessageChannel = make(chan map[string]interface{})
var OrdersMessageChannel = make(chan map[string]interface{})
var Ch *amqp.Channel

func ProduceReadMessage(msg Message) {
	body, err := json.Marshal(msg)
	failOnError(err, "Failed to marshal JSON")
	err = Ch.Publish(
		"",     // exchange
		"Read", // routing key
		false,  // mandatory
		false,  // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
		})
	failOnError(err, "Failed to publish a message")
	fmt.Println(" [x] Message Sent to Read Queue: ", msg)
}

func SendHeartbeat() {
	var heartbeat Heartbeat
	heartbeat.Microservice_name = "producer"
	fmt.Println("--------------------------------------------------")
	fmt.Println("         Heartbeat for Producer Initialized")
	fmt.Println("--------------------------------------------------")
	fmt.Println()
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		<-ticker.C
		ProduceHealthCheckMessage(heartbeat)
	}
}

func ProduceHealthCheckMessage(msg Heartbeat) {
	body, err := json.Marshal(msg)
	failOnError(err, "Failed to marshal JSON")
	err = Ch.Publish(
		"",            // exchange
		"HealthCheck", // routing key
		false,         // mandatory
		false,         // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
		})
	failOnError(err, "Failed to publish a message")
	fmt.Println(" [x] Heartbeat Sent: ", msg)
}

func ProduceOrderMessage(msg Order) {
	body, err := json.Marshal(msg)
	failOnError(err, "Failed to marshal JSON")
	err = Ch.Publish(
		"",          // exchange
		"New_Order", // routing key
		false,       // mandatory
		false,       // immediate
		amqp.Publishing{
			ContentType: "application/json",
			Body:        body,
		})
	failOnError(err, "Failed to publish a message")
	fmt.Println(" [x] Message Sent to New_Order Queue: ", msg)
}

func ConsumeDataMessages() {
	msgs, err := Ch.Consume(
		"Data", // queue
		"",     // consumer
		true,   // auto-ack
		false,  // exclusive
		false,  // no-local
		false,  // no-wait
		nil,    // args
	)
	failOnError(err, "Failed to register a consumer")

	for d := range msgs {
		var data map[string]interface{}
		err := json.Unmarshal(d.Body, &data)
		failOnError(err, "Failed to unmarshal JSON")
		fmt.Println(" [x] Received Data from Data Queue")
		// fmt.Printf(" [x] Received data from %s\n", data["table"])
		// fmt.Println("Data:", data["data"])

		if data["table"] == "products" {
			ProductsMessageChannel <- data
		} else {
			OrdersMessageChannel <- data
		}
	}
}
