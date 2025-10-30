"""
Test Uplift AI connection
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_uplift():
    from uplift_client import UpliftWebSocketClient
    
    api_key = os.getenv("UPLIFT_API_KEY")
    print(f"API Key: {api_key[:20]}...")
    
    client = UpliftWebSocketClient(api_key)
    
    try:
        print("Connecting to Uplift AI...")
        await client.connect()
        print("[OK] Connected successfully!")
        
        print("Testing synthesis...")
        audio = await client.synthesize_complete("Hello world", "v_meklc281")
        print(f"[OK] Synthesis successful! Got {len(audio)} bytes")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_uplift())

