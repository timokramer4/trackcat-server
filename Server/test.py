import requests
res = requests.post('http://localhost:5000/login', json={"username":"krypto", "password":"koffer"})
if res.ok:
    print(res.text)