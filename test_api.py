#!/usr/bin/env python3
"""Test script for the Todo Phase5 API"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_register():
    print("Testing user registration...")
    data = {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.json().get("token")

def test_login():
    print("Testing user login...")
    data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}\n")
    return result.get("token"), result.get("user", {}).get("id")

def test_create_task(token, user_id):
    print("Testing task creation...")
    data = {
        "title": "Test Task 1",
        "description": "This is a test task",
        "due_date": "2026-02-10"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/tasks/{user_id}", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}\n")
    return result.get("id")

def test_get_tasks(token, user_id):
    print("Testing get tasks...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/tasks/{user_id}", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_complete_task(token, user_id, task_id):
    print("Testing complete task...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(f"{BASE_URL}/api/tasks/{user_id}/{task_id}/complete", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_unauthorized_access(token):
    print("Testing unauthorized access (user accessing other user's tasks)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/tasks/999", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    try:
        test_root()
        test_health()

        # Register and login
        token = test_register()
        token, user_id = test_login()

        if token and user_id:
            # Test tasks
            task_id = test_create_task(token, user_id)
            test_get_tasks(token, user_id)

            if task_id:
                test_complete_task(token, user_id, task_id)
                test_get_tasks(token, user_id)

            # Test authorization
            test_unauthorized_access(token)

        print("All tests completed!")
    except Exception as e:
        print(f"Error: {e}")
