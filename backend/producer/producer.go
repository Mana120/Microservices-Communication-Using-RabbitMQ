package main

import (
	"fmt"
	"log"

	"github.com/gin-gonic/gin"
	"github.com/streadway/amqp"
)

func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

func main() {
	fmt.Println("##################################################")
	fmt.Println("         Producer Microservice Running")
	fmt.Println("##################################################")
	fmt.Println()

	conn, err := amqp.Dial("amqp://guest:guest@rabbitmq:5672/")
	failOnError(err, "Failed to connect to RabbitMQ")
	defer conn.Close()

	Ch, err = conn.Channel() // Problematic line
	failOnError(err, "Failed to open a channel")
	defer Ch.Close()

	// Declare queues
	_, err = Ch.QueueDeclare(
		"Read", // name
		false,  // durable
		false,  // delete when unused
		false,  // exclusive
		false,  // no-wait
		nil,    // arguments
	)
	failOnError(err, "Failed to declare a queue")

	_, err = Ch.QueueDeclare(
		"Data", // name
		false,  // durable
		false,  // delete when unused
		false,  // exclusive
		false,  // no-wait
		nil,    // arguments
	)
	failOnError(err, "Failed to declare a queue")

	_, err = Ch.QueueDeclare(
		"HealthCheck", // name
		false,         // durable
		false,         // delete when unused
		false,         // exclusive
		false,         // no-wait
		nil,           // arguments
	)
	failOnError(err, "Failed to declare a queue")

	fmt.Println("RabbitMQ Queues Declared.")
	go ConsumeDataMessages()
	router := gin.Default()
	router.GET("/products", GetProducts)
	router.GET("/orders/:id", GetOrdersByID)
	router.POST("/orders", PostOrder)
	fmt.Println()
	fmt.Println("--------------------------------------------------")
	fmt.Println("           HTTP Server Listening on 8080")
	fmt.Println("--------------------------------------------------")
	fmt.Println()
	go SendHeartbeat()
	router.Run(":8080")
}
