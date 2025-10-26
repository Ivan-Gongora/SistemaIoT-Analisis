import aiohttp
import json
import logging
import asyncio
from datetime import datetime, timedelta
from app.configuracion import configuracion

logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self):
        self.api_key = configuracion.DEEPSEEK_API_KEY
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.modelo = "deepseek-chat"
        
        # 🎯 OPTIMIZACIONES FREE TIER
        self.max_tokens = 1500  # Reducido para ahorrar tokens
        self.temperature = 0.2  # Más determinístico = menos variación = menos tokens
        self.timeout = 20  # Reducido timeout
        
        # 🛡️ RATE LIMITING básico
        self.last_request_time = None
        self.min_request_interval = 2  # 2 segundos entre requests
        
        # 💾 Cache simple para consultas repetitivas
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos
        
        if not self.api_key:
            raise ValueError("❌ DeepSeek API Key no configurada")
    
    async def _wait_rate_limit(self):
        """Esperar entre requests para evitar rate limiting"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.min_request_interval:
                wait_time = self.min_request_interval - elapsed
                await asyncio.sleep(wait_time)
        self.last_request_time = datetime.now()
    
    def _get_cache_key(self, prompt: str, contexto: str) -> str:
        """Generar clave única para cache"""
        return f"{hash(prompt)}:{hash(contexto)}"
    
    def _get_cached_response(self, cache_key: str) -> str:
        """Obtener respuesta del cache si existe y es válida"""
        if cache_key in self._cache:
            timestamp, response = self._cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self._cache_ttl):
                logger.info("💾 Respuesta obtenida de cache")
                return response
            else:
                # Limpiar cache expirado
                del self._cache[cache_key]
        return None
    
    def _set_cached_response(self, cache_key: str, response: str):
        """Guardar respuesta en cache"""
        # Limitar tamaño del cache (últimas 10 consultas)
        if len(self._cache) >= 10:
            # Eliminar el más antiguo
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            del self._cache[oldest_key]
        
        self._cache[cache_key] = (datetime.now(), response)
    
    async def consultar_ia(self, prompt: str, contexto: str = "") -> str:
        """Consultar la API de DeepSeek optimizada para free tier"""
        
        # 🎯 OPTIMIZAR CONTEXTO Y PROMPT
        contexto_optimizado = self._optimizar_contexto(contexto)
        prompt_optimizado = self._optimizar_prompt(prompt)
        
        cache_key = self._get_cache_key(prompt_optimizado, contexto_optimizado)
        cached_response = self._get_cached_response(cache_key)
        
        if cached_response:
            return cached_response
        
        try:
            # 🛡️ Rate limiting
            await self._wait_rate_limit()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 🎯 SYSTEM MESSAGE OPTIMIZADA (más corta)
            system_message = """Experto en eficiencia energética industrial México. 
            Especialista tarifas CFE GDMTH. Análisis preciso y recomendaciones prácticas."""
            
            payload = {
                "model": self.modelo,
                "messages": [
                    {
                        "role": "system", 
                        "content": system_message  # ← Reducida 60%
                    },
                    {
                        "role": "user",
                        "content": f"Contexto:{contexto_optimizado}\nPregunta:{prompt_optimizado}"  # ← Formato compacto
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }
            
            logger.info("🔍 Consultando API DeepSeek (optimizado)...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, 
                    json=payload, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        respuesta = result['choices'][0]['message']['content']
                        
                        # 💾 Guardar en cache
                        self._set_cached_response(cache_key, respuesta)
                        
                        # 📊 Log de uso (sin saturar)
                        tokens_usados = result.get('usage', {}).get('total_tokens', 0)
                        logger.info(f"✅ DeepSeek: {tokens_usados} tokens usados")
                        
                        return respuesta
                    
                    elif response.status == 429:  # Rate Limit
                        logger.warning("⚠️ Rate limit alcanzado, esperando...")
                        await asyncio.sleep(10)  # Esperar 10 segundos
                        return "⚠️ Límite de uso temporal alcanzado. Intenta en unos segundos."
                    
                    elif response.status == 402:  # Insufficient Balance
                        logger.error("❌ Sin saldo en cuenta DeepSeek")
                        return "❌ Cuenta DeepSeek sin saldo. Verifica tu plan gratuito."
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ API Error {response.status}: {error_text[:100]}...")
                        return f"Error API: {response.status}"
                        
        except asyncio.TimeoutError:
            logger.warning("⏰ Timeout en consulta DeepSeek")
            return "⏰ Timeout en consulta. Intenta nuevamente."
            
        except Exception as e:
            logger.error(f"❌ Error consultando DeepSeek: {str(e)}")
            return f"Error de conexión: {str(e)}"
    
    def _optimizar_contexto(self, contexto: str) -> str:
        """Optimizar contexto para reducir tokens"""
        if not contexto:
            return ""
        
        # 🎯 Estrategias de optimización:
        # 1. Eliminar espacios múltiples
        # 2. Acortar textos muy largos
        # 3. Mantener solo información esencial
        
        lines = contexto.strip().split('\n')
        lines_optimizadas = []
        
        for line in lines:
            line = ' '.join(line.split())  # Normalizar espacios
            if len(line) > 150:  # Acortar líneas muy largas
                line = line[:147] + "..."
            if line and not line.isspace():
                lines_optimizadas.append(line)
        
        return '\n'.join(lines_optimizadas[:15])  # Máximo 15 líneas
    
    def _optimizar_prompt(self, prompt: str) -> str:
        """Optimizar prompt para ser más eficiente"""
        prompt = ' '.join(prompt.split())  # Normalizar espacios
        
        # 🎯 Prompts pre-optimizados para casos comunes
        prompts_optimizados = {
            "analisis general": "Analiza patrones principales y da 3 recomendaciones clave con ahorro estimado",
            "optimizacion costos": "Estrategias para reducir costos manteniendo operaciones",
            "demanda maxima": "Cómo optimizar demanda máxima y reducir penalizaciones",
            "factor potencia": "Recomendaciones para mejorar factor de potencia >90%"
        }
        
        # Buscar prompt optimizado por keywords
        prompt_lower = prompt.lower()
        for key, optimized in prompts_optimizados.items():
            if key in prompt_lower:
                return optimized
        
        # Si no coincide, acortar prompt original
        if len(prompt) > 200:
            return prompt[:197] + "..."
        
        return prompt
    
    async def analizar_datos_energeticos(self, df_summary: str, pregunta_especifica: str = "") -> str:
        """Método especializado OPTIMIZADO para free tier"""
        
        # 🎯 CONTEXTO MÁS COMPACTO
        contexto = f"Datos:{self._optimizar_contexto(df_summary)}"
        
        # 🎯 PROMPT OPTIMIZADO
        if pregunta_especifica:
            prompt = self._optimizar_prompt(pregunta_especifica)
        else:
            prompt = "Analiza patrones principales y da 3 recomendaciones clave con ahorro estimado"
        
        return await self.consultar_ia(prompt, contexto)