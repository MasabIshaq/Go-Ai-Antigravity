import asyncio
import httpx
import json
import os
import sys

# Change standard output encoding
sys.stdout.reconfigure(encoding='utf-8')

async def test():
    client = httpx.AsyncClient(timeout=10.0)
    payload = {
        'model': 'glm-4.5-flash',
        'messages': [{'role': 'user', 'content': 'hi'}],
        'stream': True
    }
    headers = {
        'Authorization': 'Bearer e3d3cd01b5cf46b6bc67f9c196717e6a.HwMXVlZAqdPYIV0p',
        'Content-Type': 'application/json'
    }
    try:
        async with client.stream('POST', 'https://open.bigmodel.cn/api/paas/v4/chat/completions', headers=headers, json=payload) as response:
            print(f'Status: {response.status_code}')
            body = await response.aread()
            print(f'Body: {body.decode("utf-8")}')
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(test())
