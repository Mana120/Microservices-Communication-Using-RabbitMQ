const axios = require('axios');
const prompt = require('prompt');

const Table = require('cli-table3');
const URL = 'http://localhost:8080';

function printProductsTable(productsData) {
    // console.log('Type of productsData:', typeof productsData);
    productsData = JSON.parse(productsData);

    const table = new Table({
        head: ['Product ID', 'Name', 'Price'],
        colWidths: [15, 30, 15]
    });

    productsData.forEach(product => {
        table.push([product.Product_ID, product.Name, product.Price]);
    });

    console.log(table.toString());
}

function printOrdersTable(ordersData) {
    // console.log('Type of productsData:', typeof productsData);
    ordersData = JSON.parse(ordersData);

    const table = new Table({
        head: ['Order ID', 'Product ID', 'Quantity', 'Status'],
        colWidths: [15, 30, 15]
    });
    ordersData.forEach(order => {
        table.push([order.Order_ID, order.Product_ID, order.Quantity, order.Status]);
    });

    console.log(table.toString());
}

async function getProducts() {
    const url = `${URL}/products`;
    try {
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        console.log(error)
        console.error(`Error fetching products: ${error.message}`);
        return null;
    }
}

async function getOrders(id) {
    const url = `${URL}/orders/${id}`;
    try {
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        console.error(`Error fetching orders: ${error.message}`);
        return null;
    }
}

async function placeOrder( Customer_ID, Product_ID, Quantity) {
    // Order_ID -> Customer_ID_CurrentTimestamp
    const timestamp = new Date().getTime();
    const Order_ID = `${Customer_ID}_${timestamp}`;
    const orderData = {
        Order_ID:       Order_ID,
        Customer_ID:    Customer_ID,
        Product_ID:     Product_ID,
        Quantity:       Quantity
    };
    const url = `${URL}/orders`;
    try {
        const response = await axios.post(url, orderData);
        console.log(`Successfully Placed Order for Product: ${Product_ID}, Quantity: ${Quantity} Against Customer: ${Customer_ID}.`)
        return response.data;
    } catch (error) {
        console.error(`Error posting order: ${error.message}`);
        return null;
    }
}

async function requestLoop(customerId) {
    while (true) {
        console.log("\n###########################################");
        console.log(`              Customer ID: ${customerId}`);
        console.log("###########################################\n");
        console.log("\nChoose an option:");
        console.log("1. Place Order");
        console.log("2. Display Products");
        console.log("3. My Orders");
        console.log("4. Logout");
        console.log();

        prompt.start();
        const { choice } = await prompt.get(['choice']);

        switch (parseInt(choice)) {
            case 1:
                console.log()
                const { Product_ID } = await prompt.get(['Product_ID']);
                const { Quantity } = await prompt.get(['Quantity']);
                const parsedQuantity = parseInt(Quantity);

                if (isNaN(parsedQuantity) || parsedQuantity <= 0) {
                    console.error('Invalid quantity. Quantity must be a positive integer.');
                    console.error('Please Retry.');
                    break;
                }

                await placeOrder( customerId, Product_ID, parsedQuantity);
                break;
            case 2:
                const products = await getProducts();
                if (products) {
                    console.log('\nProducts: ');
                    // console.log(products)
                    printProductsTable(products)
                    // products.forEach(product => console.log(product));
                }
                break;
            case 3:
                const orders = await getOrders(customerId);
                if (orders) {
                    console.log('\nOrders:');
                    printOrdersTable(orders)
                } else {
                    console.log(`No Previously Placed Orders for Customer ${customerId}.`)
                    console.log()
                }
                break;
            case 4:
                console.log("Logging out...");
                return;
            default:
                console.log("Invalid option. Please try again.");
        }
    }
}

async function main() {
    while (true) {
        console.log("\n###########################################");
        console.log(`                 MAIN MENU`);
        console.log("###########################################\n");

        console.log("1. Login");
        console.log("2. Exit");
        console.log();
        prompt.start();
        const { choice } = await prompt.get(['choice']);

        switch (parseInt(choice)) {
            case 1:
                console.log("\n###########################################");
                console.log(`                   LOGIN`);
                console.log("###########################################\n");
                const { customerId } = await prompt.get(['customerId']);
                console.log(`\nLogged in as customer ${customerId}`);
                await requestLoop(customerId);
                break;
            case 2:
                console.log("Exiting the application...");
                return;
            default:
                console.log("Invalid option. Please try again.");
        }
    }
}


main();