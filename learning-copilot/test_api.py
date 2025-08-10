#!/usr/bin/env python3
"""
Quick test script to verify OpenAI API connection and model compatibility
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test the OpenAI API connection with different models"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("MODEL_NAME", "gpt-5-mini")
    
    # Check API key
    if not api_key or api_key == "your-openai-api-key-here":
        print("❌ Error: Please set your actual OpenAI API key in .env file")
        print("   Get your key from: https://platform.openai.com/api-keys")
        return False
    
    print(f"✅ API key found")
    print(f"📦 Testing model: {model}")
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Test with correct parameters for GPT-5
        params = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API test successful' in 5 words or less."}
            ],
            "temperature": 0.7
        }
        
        # Use correct parameter based on model
        if model.startswith("gpt-5") or model.startswith("o1"):
            params["max_completion_tokens"] = 50
            print("   Using max_completion_tokens parameter")
        else:
            params["max_tokens"] = 50
            print("   Using max_tokens parameter")
        
        # Add GPT-5 specific parameters if applicable
        if model.startswith("gpt-5"):
            params["verbosity"] = "low"
            params["reasoning_effort"] = "low"
            print("   Added GPT-5 specific parameters")
        
        print("\n🔄 Testing API call...")
        response = client.chat.completions.create(**params)
        
        print(f"✅ Success! Response: {response.choices[0].message.content}")
        print(f"\n📊 Model used: {response.model}")
        print(f"📊 Tokens used: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API Error: {str(e)}")
        
        # Provide helpful error messages
        if "401" in str(e):
            print("\n💡 Fix: Your API key is invalid. Please check:")
            print("   1. You're using your actual API key (not the placeholder)")
            print("   2. The key is still active in your OpenAI account")
            print("   3. The key has the necessary permissions")
        elif "max_tokens" in str(e) and "max_completion_tokens" in str(e):
            print("\n💡 Fix: Parameter name issue detected.")
            print("   The script will automatically retry with the correct parameter.")
        elif "404" in str(e):
            print(f"\n💡 Fix: Model '{model}' not found. Try one of these:")
            print("   - gpt-5-mini (recommended)")
            print("   - gpt-5")
            print("   - gpt-4-turbo-preview")
            print("   - gpt-4")
        
        return False

if __name__ == "__main__":
    print("🚀 OpenAI API Connection Test")
    print("=" * 40)
    
    if test_api_connection():
        print("\n✨ All tests passed! Your API is ready to use.")
        print("   Run: streamlit run app.py")
    else:
        print("\n⚠️  Please fix the issues above before running the app.")
        sys.exit(1)