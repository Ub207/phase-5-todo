#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for advanced features"""
import sys
import io
import requests
import json
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

# First, login to get token
def get_auth_token():
    data = {"email": "test@example.com", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    return response.json()["token"], response.json()["user"]["id"]

def test_create_multiple_tasks(token, user_id):
    """Create multiple tasks with different priorities and due dates"""
    print("\n=== Creating Multiple Tasks ===")
    headers = {"Authorization": f"Bearer {token}"}

    tasks_data = [
        {"title": "High priority urgent task", "description": "Must do ASAP", "priority": "high", "due_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")},
        {"title": "Medium priority task", "description": "Regular task", "priority": "medium", "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")},
        {"title": "Low priority task", "description": "Can wait", "priority": "low", "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")},
        {"title": "Buy groceries", "description": "Milk, eggs, bread", "priority": "medium", "due_date": datetime.now().strftime("%Y-%m-%d")},
        {"title": "Finish project report", "description": "Q4 analytics", "priority": "high", "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")},
    ]

    created_tasks = []
    for task_data in tasks_data:
        response = requests.post(f"{BASE_URL}/api/tasks", json=task_data, headers=headers)
        if response.status_code == 201:
            created_tasks.append(response.json())
            print(f"✅ Created: {task_data['title']} (priority: {task_data['priority']})")
        else:
            print(f"❌ Failed: {response.status_code}")

    return created_tasks

def test_filter_by_priority(token):
    """Test filtering by priority"""
    print("\n=== Testing Priority Filter ===")
    headers = {"Authorization": f"Bearer {token}"}

    for priority in ["high", "medium", "low"]:
        response = requests.get(f"{BASE_URL}/api/tasks?priority={priority}", headers=headers)
        tasks = response.json()
        print(f"\n{priority.upper()} priority tasks ({len(tasks)}):")
        for task in tasks:
            print(f"  - {task['title']}")

def test_search_tasks(token):
    """Test search functionality"""
    print("\n=== Testing Search ===")
    headers = {"Authorization": f"Bearer {token}"}

    search_queries = ["project", "buy", "urgent"]
    for query in search_queries:
        response = requests.get(f"{BASE_URL}/api/tasks?q={query}", headers=headers)
        tasks = response.json()
        print(f"\nSearch '{query}': {len(tasks)} results")
        for task in tasks:
            print(f"  - {task['title']}")

def test_overdue_filter(token):
    """Test overdue filter"""
    print("\n=== Testing Overdue Filter ===")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/api/tasks?overdue=true", headers=headers)
    tasks = response.json()
    print(f"Overdue tasks: {len(tasks)}")
    for task in tasks:
        print(f"  - {task['title']} (due: {task['due_date']})")

def test_sorting(token):
    """Test sorting options"""
    print("\n=== Testing Sorting ===")
    headers = {"Authorization": f"Bearer {token}"}

    # Sort by due date ascending
    response = requests.get(f"{BASE_URL}/api/tasks?sort_by=due_date&sort_order=asc", headers=headers)
    tasks = response.json()
    print(f"\nSorted by due date (ascending):")
    for task in tasks[:3]:  # Show first 3
        print(f"  - {task['title']}: {task['due_date']}")

def test_update_task(token, user_id, task_id):
    """Test updating a task"""
    print("\n=== Testing Task Update ===")
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {
        "title": "Updated task title",
        "priority": "high",
        "description": "Updated description"
    }

    response = requests.put(f"{BASE_URL}/api/tasks/{user_id}/{task_id}", json=update_data, headers=headers)
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Updated task #{task_id}")
        print(f"   Title: {task['title']}")
        print(f"   Priority: {task['priority']}")
    else:
        print(f"❌ Update failed: {response.status_code}")

def test_delete_task(token, user_id, task_id):
    """Test deleting a task"""
    print("\n=== Testing Task Delete ===")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(f"{BASE_URL}/api/tasks/{user_id}/{task_id}", headers=headers)
    if response.status_code == 204:
        print(f"✅ Deleted task #{task_id}")
    else:
        print(f"❌ Delete failed: {response.status_code}")

if __name__ == "__main__":
    try:
        print("Getting authentication token...")
        token, user_id = get_auth_token()
        print(f"✅ Logged in as user #{user_id}")

        # Create test tasks
        tasks = test_create_multiple_tasks(token, user_id)

        # Test filtering
        test_filter_by_priority(token)
        test_search_tasks(token)
        test_overdue_filter(token)
        test_sorting(token)

        # Test update and delete
        if len(tasks) >= 2:
            test_update_task(token, user_id, tasks[0]["id"])
            test_delete_task(token, user_id, tasks[1]["id"])

        print("\n✅ All advanced feature tests completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
