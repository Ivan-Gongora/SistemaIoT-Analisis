#!/usr/bin/env python3
"""
Script para verificar el estado de la cuenta DeepSeek
"""
import os
import aiohttp
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

async def test_deepseek_account():
    """Probar directamente la conexión con DeepSeek"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ No se encontró DEEPSEEK_API_KEY en .env")
        return
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-10:]}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "Responde solo con 'OK' si estás funcionando correctamente."
            }
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=10
            ) as response:
                
                print(f"📡 Status Code: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    respuesta = result['choices'][0]['message']['content']
                    print(f"✅ Respuesta API: {respuesta}")
                    print("🎉 ¡La cuenta DeepSeek está ACTIVA y FUNCIONANDO!")
                    
                elif response.status == 401:
                    print("❌ Error 401: API Key inválida o no autorizada")
                    print("💡 Verifica que la API Key sea correcta")
                    
                elif response.status == 402:
                    print("❌ Error 402: Insufficient Balance")
                    print("💡 La cuenta no tiene saldo o no está activada")
                    print("💡 Ve a https://platform.deepseek.com/billing")
                    
                elif response.status == 429:
                    print("⚠️ Error 429: Rate Limit Exceeded")
                    print("💡 Demasiadas requests, espera unos minutos")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Error {response.status}: {error_text}")
                    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("🔍 Verificando estado de cuenta DeepSeek...")
    asyncio.run(test_deepseek_account())