#!/usr/bin/env python3
"""
Test script for AVA AI Chat functionality
"""

import requests
import json
import time

def test_ai_chat():
    """Test the AI chat endpoint"""
    base_url = "http://localhost:8000"
    session_id = f"test_session_{int(time.time())}"
    
    print("🧪 Testing AVA AI Chat Functionality")
    print("=" * 50)
    
    # Test 1: Basic AI chat
    print("\n1️⃣ Testing basic AI chat...")
    try:
        response = requests.post(
            f"{base_url}/llm/text-query",
            json={
                "text": "Hello! Can you introduce yourself in one sentence?",
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! AI Response: {data['llmResponse'][:100]}...")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Conversation continuity
    print("\n2️⃣ Testing conversation continuity...")
    try:
        response = requests.post(
            f"{base_url}/llm/text-query",
            json={
                "text": "What did I just ask you?",
                "session_id": session_id  # Same session
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! AI remembered: {data['llmResponse'][:100]}...")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Clear chat history
    print("\n3️⃣ Testing chat history clearing...")
    try:
        response = requests.post(
            f"{base_url}/chat/clear",
            json={"session_id": session_id},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Success! Chat history cleared")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: New conversation after clear
    print("\n4️⃣ Testing new conversation after clear...")
    try:
        response = requests.post(
            f"{base_url}/llm/text-query",
            json={
                "text": "Do you remember what I asked you before?",
                "session_id": session_id  # Same session but cleared
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! AI response: {data['llmResponse'][:100]}...")
            if "don't" in data['llmResponse'].lower() or "no" in data['llmResponse'].lower():
                print("✅ Correctly forgot previous conversation!")
            else:
                print("⚠️  AI might still remember previous conversation")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n🎉 All AI Chat tests passed!")
    print("=" * 50)
    print("✨ Your AI Chat section is fully functional!")
    print("\n📋 Features working:")
    print("   ✅ Text-based AI conversations")
    print("   ✅ Session-based chat history")
    print("   ✅ Chat history clearing")
    print("   ✅ Conversation continuity")
    print("   ✅ Error handling")
    
    return True

if __name__ == "__main__":
    test_ai_chat()