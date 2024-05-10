package main

type Product struct {
	Product_ID  string `json:"Product_ID"`
	Name        string `json:"Name"`
	Description string `json:"Description"`
	Price       int    `json:"Price"`
}

type Order struct {
	Order_ID    string `json:"Order_ID"`
	Customer_ID string `json:"Customer_ID"`
	Product_ID  string `json:"Product_ID"`
	Quantity    int    `json:"Quantity"`
}
