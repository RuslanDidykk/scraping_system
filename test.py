import requests

r = requests.post('http://carmudi.ae/api/show_number', data = {"product_id":"64513"})
print r.text