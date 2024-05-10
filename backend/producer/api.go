package main

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

func GetProducts(c *gin.Context) {
	fmt.Println("--------------------------------------------------")
	fmt.Println("GET Request for Products.")
	var message Message
	message.CustomerID = ""
	message.Type = "read_products"
	go ProduceReadMessage(message)
	result := <-ProductsMessageChannel
	c.JSON(http.StatusOK, result["data"])
	fmt.Println("Response sent.")
	fmt.Println("--------------------------------------------------")
	fmt.Println()
}

func GetOrdersByID(c *gin.Context) {
	customer_id := c.Param("id")
	fmt.Println("--------------------------------------------------")
	fmt.Println("GET Request for Orders from Customer_ID ", customer_id)
	var message Message
	message.CustomerID = customer_id
	message.Type = "read_orders"
	go ProduceReadMessage(message)

	result := <-OrdersMessageChannel
	c.JSON(http.StatusOK, result["data"])
	fmt.Println("Response sent to Customer_ID ", customer_id)
	fmt.Println("--------------------------------------------------")
	fmt.Println()
}

func PostOrder(c *gin.Context) {
	var newOrder Order
	fmt.Println("--------------------------------------------------")
	fmt.Println("POST Request for Orders from Customer_ID ", newOrder.Customer_ID)
	if err := c.BindJSON(&newOrder); err != nil {
		return
	}
	fmt.Println("Order: ", newOrder)

	ProduceOrderMessage(newOrder)

	fmt.Println("Request Handled.")
	fmt.Println("--------------------------------------------------")
}
