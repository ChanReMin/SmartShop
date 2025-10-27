import threading
import requests

URL = "http://localhost:5000/api/order"

access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2MTI5OTc5MiwianRpIjoiMGIzNTc3YmItZTg1ZS00NmVlLWFkMDgtYjliZDNiMTExZjgzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3NjEyOTk3OTIsImV4cCI6MTc2MTMwMzM5MiwiaXNfYWRtaW4iOmZhbHNlfQ.GduxaL8ymDVtuyAUfWxxvVmmDl34DaNeJhEhyA5emmw'
headers = {
    "Authorization": f"Bearer {access_token}"
}
payload = {
    "user_id": 1,
    "items": [{"product_id": 3, "quantity": 4}],
    "payment_method": "creditcard"
}

def place_order():
    try:
        response = requests.post(URL, json=payload, headers=headers)
        # In thêm thông tin chi tiết
        print("Status Code:", response.status_code)
        try:
            print("Response JSON:", response.json())
        except ValueError:
            print("Response Text:", response.text)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

def test_concurrent_orders():
    threads = [threading.Thread(target=place_order) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
