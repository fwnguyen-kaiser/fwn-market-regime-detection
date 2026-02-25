from fastapi.testclient import TestClient
from app.main import app 

client = TestClient(app)

def test_root_endpoint():
    """Kiểm tra server có thực sự 'UP' như bro viết không"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Server is UP"}

def test_prediction_endpoint_exists():
    # Thử gọi vào root của market router xem nó có nhận không
    response = client.get("/api/v1/market/?ticker=AAPL") 
    
    # Nếu vẫn 404, thử bỏ dấu / ở cuối: "/api/v1/market?ticker=AAPL"
    if response.status_code == 404:
        response = client.get("/api/v1/market?ticker=AAPL")

    assert response.status_code != 404