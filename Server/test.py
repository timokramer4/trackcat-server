import requests
#res = requests.post('http://localhost:5000/login', json={"username":"krypto", "password":"koffer"})
res = requests.post('http://localhost:5000/deleteRecordAPI', json={"recordId":"3"})

if res.ok:
    print(res.text)