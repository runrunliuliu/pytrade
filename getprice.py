import requests
for line in open('data/holds.txt'):
    url = 'http://www.quchaogu.com/stock/batchinfo?code=' + line.strip() 
    r   = requests.get(url)
    js  =  r.json()
    print js['data'][0]['price']
