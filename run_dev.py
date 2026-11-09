import sys
from app import app

if __name__ == '__main__':
    print("🦅 FALK BACKEND RUNTIME READY ON PORT 5001")
    app.run(host='127.0.0.1', port=5001, debug=True)
