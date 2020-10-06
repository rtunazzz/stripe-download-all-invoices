import os
import stripe
import requests
import datetime

from progress.bar import ChargingBar

class Invoice:
    def __init__(self, invoice_json):
        data = invoice_json

        self.pdf = data["invoice_pdf"]
        self.number = data["number"]
        self.paid = data["paid"]
        self.created_timestamp = data["created"]
        self.created_datetime = datetime.datetime.fromtimestamp(self.created_timestamp)

    def __str__(self):
        return f'Invoice number {self.number}, created on {self.created_datetime}'

    def isPaid(self):
        return self.paid

def get_date_input(message):
    date = ''
    while True:
        date = input(f'{message}\nFormat \'MM/DD/YY\'\n→ ')
        if date.lower() == 'now':
            return int(datetime.datetime.now().timestamp())
        if len(date) == 8:
            break
        else:
            print('Please input a valid date!')
    
    [month, day, year] = date.split('/')
    date = datetime.datetime(2000 + int(year), int(month), int(day))

    return int(date.timestamp())

def get_all_customers():
    print('Getting all customers. This may take a while...')
    customers = list(stripe.Customer.list(limit=100))
    while len(customers) % 100 == 0:
        customers += list(stripe.Customer.list(limit=100, starting_after=customers[-1]))
    return customers

def get_all_invoices(customer_id):    
    invoices = list(stripe.Invoice.list(customer=customer_id, limit=100))
    if len(invoices) == 0:
        return []
    while len(invoices) % 100 == 0:
        invoices += list(stripe.Customer.list(customer=customer_id, limit=100, starting_after=invoices[-1]))
    return invoices

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


print('''
  ____ _____ ____  ___ ____  _____   ____    ____  ____  _____ 
 / ___|_   _|  _ \|_ _|  _ \| ____| |___ \  |  _ \|  _ \|  ___|
 \___ \ | | | |_) || || |_) |  _|     __) | | |_) | | | | |_   
  ___) || | |  _ < | ||  __/| |___   / __/  |  __/| |_| |  _|  
 |____/ |_| |_| \_\___|_|   |_____| |_____| |_|   |____/|_|    
''')

print('--------------------------------------------------------------------')
stripe.api_key = open("stripe-secret.txt", "r").read().strip()
if stripe.api_key == '':
    print('ERROR - No Stripe API key provided.')
    exit()
    
all_invoices = input('Download ALL invoices?\n→ ')
if not all_invoices.lower().startswith('y'):
    #TODO
    # from_date = get_date_input('FROM what date do you want to download?\n→ ')
    # to_date = get_date_input('TO what date do you want to download?\n→ ')
    # customers = stripe.Customer.list(created={
    #     'gte': from_date,
    #     'lte': to_date
    # })
    print('Alright! Restart me whenever you\'re ready to download them all.')
    exit()
else:
    customers = get_all_customers()
print('--------------------------------------------------------------------')
confirm = input(f'I am about to download invoices from {len(customers)} customer(s), sound good? (y/n)\n→ ')
if not confirm.lower().startswith('y'):
    print('Fine! Restart me and say \'Yes\' whenever you\'re ready.')
    exit()

print('--------------------------------------------------------------------')
customer_ids = list(map(lambda x: x['id'], customers))

create_directory('./invoices')
total_bar = ChargingBar('[PDF SAVING] Download in progress', max=len(customer_ids))
for customer in customer_ids:
    invoice_jsons = get_all_invoices(customer)
    # Download PDFs
    for invoice in invoice_jsons:
        invoice_pretty = Invoice(invoice)
        if not invoice_pretty.isPaid():
            continue
        if not invoice_pretty.pdf:
            print(f'NO URL for {invoice_pretty.number} exists')
            continue
        r = requests.get(invoice_pretty.pdf, stream=True)
        with open(f'./invoices/{invoice_pretty.number}.pdf', 'wb') as f:
            f.write(r.content)
    total_bar.next()
print()
print('--------------------------------------------------------------------')
print('Done! Please consider giving it a star on GitHub if this helped you.')