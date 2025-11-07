import requests
import sys

try:
    # Отправляем запрос на корневой маршрут /
    response = requests.get("http://127.0.0.1:5000/")
    print("Response:", response.text)
    print("Status code:", response.status_code)
    
    # Проверяем, что код ответа 200
    if response.status_code != 200:
        print("❌ Test failed: Expected status code 200")
        sys.exit(1)
    
    if "Wrong expected text" not in response.text:
        print("❌ Test failed: Expected text 'Wrong expected text' not found in response")
        sys.exit(1)
    
    print("✅ Test passed")
except Exception as e:
    print("❌ Error:", e)
    sys.exit(1)
