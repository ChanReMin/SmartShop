import threading
import requests

URL = "http://localhost:5000/api/order"

# Thay bằng token hợp lệ của bạn (user_id trong token nên khớp với user_id trong payload nếu backend kiểm tra)
access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2MTI5MzY3OCwianRpIjoiZGY1ZTJiNGUtMTc3NS00MmQwLWE0MDktN2NlOGVmNzE0ZjhlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3NjEyOTM2NzgsImV4cCI6MTc2MTI5NzI3OCwiaXNfYWRtaW4iOmZhbHNlfQ.x3JNfcaa_eEso0W9Lbl_xnURGjgaY6zMqvbsv3WBqTQ'

headers = {
    "Authorization": f"Bearer {access_token}"
}

payload = {
    "user_id": 3,
    "items": [{"product_id": 3, "quantity": 1}],
    "payment": "pending"
}

def create_pending_order():
    try:
        response = requests.post(URL, json=payload, headers=headers)
        print("Status Code:", response.status_code)
        try:
            print("Response JSON:", response.json())
        except ValueError:
            print("Response Text:", response.text)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

def test_create_multiple_pending_orders():
    """Tạo 2 đơn PENDING đồng thời để test."""
    threads = [threading.Thread(target=create_pending_order) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()