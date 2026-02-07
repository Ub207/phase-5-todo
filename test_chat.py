#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test chat functionality (simple command mode)"""
import sys
import io
import requests
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    """Login and get token"""
    data = {"email": "test@example.com", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    return response.json()["token"]

def send_chat_message(token, message):
    """Send a chat message"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    response = requests.post(f"{BASE_URL}/api/chat", json=data, headers=headers)
    return response.json()

def test_chat_commands(token):
    """Test various chat commands"""
    print("\n=== Testing Chat Simple Command Mode ===\n")

    test_commands = [
        ("add Write documentation", "Adding a task"),
        ("add Call dentist tomorrow", "Adding another task"),
        ("show list", "Listing all tasks"),
        ("list tasks", "Alternative list command"),
        ("complete Write documentation", "Completing a task"),
        ("delete Call dentist", "Deleting a task"),
        ("show list", "Final task list"),
        ("hello", "Non-command (should get help message)"),
    ]

    for command, description in test_commands:
        print(f"\n📤 {description}: '{command}'")
        result = send_chat_message(token, command)
        print(f"💬 Reply: {result['reply']}")

def test_chat_history(token):
    """Test chat history endpoints"""
    print("\n\n=== Testing Chat History ===\n")
    headers = {"Authorization": f"Bearer {token}"}

    # Get history
    response = requests.get(f"{BASE_URL}/api/chat/history", headers=headers)
    history = response.json()
    print(f"Chat history entries: {len(history.get('messages', []))}")

    # Clear history
    response = requests.delete(f"{BASE_URL}/api/chat/history", headers=headers)
    print(f"Clear history: {response.json()['message']}")

    # Verify cleared
    response = requests.get(f"{BASE_URL}/api/chat/history", headers=headers)
    history = response.json()
    print(f"After clear: {len(history.get('messages', []))} entries")

if __name__ == "__main__":
    try:
        print("Getting authentication token...")
        token = get_auth_token()
        print("✅ Authenticated\n")

        test_chat_commands(token)
        test_chat_history(token)

        print("\n\n✅ All chat tests completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
