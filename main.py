import stripe
import requests
import datetime

from progress.bar import ChargingBar

class Invoice:
    def __init__(self, invoice_json):
        data = invoice_json["data"][0]

        self.pdf = data["invoice_pdf"]
        self.number = data["number"]
        self.created_timestamp = data["created"]
        self.created_datetime = datetime.datetime.fromtimestamp(self.created_timestamp)

    def __str__(self):
        return f'Invoice number {self.number}, created on {self.created_datetime}'

print('''
  ____ _____ ____  ___ ____  _____   ____    ____  ____  _____ 
 / ___|_   _|  _ \|_ _|  _ \| ____| |___ \  |  _ \|  _ \|  ___|
 \___ \ | | | |_) || || |_) |  _|     __) | | |_) | | | | |_   
  ___) || | |  _ < | ||  __/| |___   / __/  |  __/| |_| |  _|  
 |____/ |_| |_| \_\___|_|   |_____| |_____| |_|   |____/|_|    
''')

# stripe.api_key = "sk_test_YJPYzjpRthAq7pihh8xGiRNC00rKC5P7Vx"
print('--------------------------------------------------------------------')
stripe.api_key = open("stripe-secret.txt", "r").read().strip()
if stripe.api_key == '':
    print('ERROR - No Stripe API key provided.')
    exit()

customers = stripe.Customer.list()
print(f'Downloading Invoices from {len(customers)} customer(s).')

customer_ids = list(map(lambda x: x['id'], customers))


invoice_jsons = list(map(lambda customer_id: stripe.Invoice.list(customer=customer_id), customer_ids))

invoices_pretty = list(map(lambda json: Invoice(json), invoice_jsons))


# Download PDFs
print('--------------------------------------------------------------------')
total_bar = ChargingBar('Download in progress', max=len(invoices_pretty))
for invoice in invoices_pretty:
    total_bar.next()
    r = requests.get(invoice.pdf, stream=True)
    with open(f'./invoices/{invoice.number}-{invoice.created_timestamp}.pdf', 'wb') as f:
        f.write(r.content)
print()
print('--------------------------------------------------------------------')
print('Done! Please consider giving it a star on GitHub if this helped you!')