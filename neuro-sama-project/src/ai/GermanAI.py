"""
Deutsche Neuro-sama AI Engine - Memory-Augmented LLM System
Basierend auf Vedal's Architecture mit erweiterten Long-Term Memory Features
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import websockets
import redis
import openai
from openai import AsyncOpenAI

# Vector Database Integration (Pinecone oder Weaviate)
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    
try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Chat-Nachricht Struktur von C# Twitch Bot"""
    user_id: str
    username: str
    message: str
    platform: str
    timestamp: str
    is_subscriber: bool = False
    is_moderator: bool = False
    badges: List[str] = None

@dataclass
class AIResponse:
    """AI-Response Struktur für C# Twitch Bot"""
    response: str
    emotion: str
    needs_tts: bool
    user_id: str
    timestamp: datetime

class GermanNeuroPersonality:
    """
    Deutsche Neuro-sama Persönlichkeit mit kulturellen Anpassungen
    """
    
    def __init__(self):
        self.base_traits = {
            'enthusiasm': 0.9,      # Sehr enthusiastisch
            'directness': 0.7,      # Deutsche Direktheit
            'humor': 0.8,           # Deutscher Humor mit VTuber-Touch
            'curiosity': 0.85,      # AI-Neugier
            'friendliness': 0.95,   # VTuber-Freundlichkeit
            'sass': 0.6             # Neuro-sama's charakteristische Frechheit
        }
        
        self.german_expressions = {
            'excitement': ['Wow!', 'Krass!', 'Das ist ja verrückt!', 'Boah!', 'Hammer!'],
            'confusion': ['Häh?', 'Was?', 'Äh...', 'Versteh ich nicht...', 'Wie bitte?'],
            'happiness': ['Juhu!', 'Super!', 'Geil!', 'Nice!', 'Perfekt!'],
            'sass': ['Ach so...', 'Klar doch...', 'Na sicher...', 'Wie du meinst...'],
            'agreement': ['Stimmt!', 'Genau!', 'Exakt!', 'Richtig!', 'Auf jeden Fall!']
        }
        
        self.cultural_references = {
            'food': ['Döner', 'Schnitzel', 'Brezeln', 'Currywurst', 'Sauerbraten'],
            'tv_shows': ['Tatort', 'Wetten dass..?', 'Galileo', 'TV Total'],
            'holidays': ['Oktoberfest', 'Karneval', 'Weihnachtsmärkte', 'Pfingsten'],
            'memes': ['Mittwoch Frosch', 'Deutsch Qualität', 'Pünktlichkeit']
        }
        
        self.vtuber_expressions = ['Hehe~', 'Ehehe~', 'Nani?!', 'Sugoi!', 'Kawaii~']
        
    def get_system_prompt(self) -> str:
        """System-Prompt für deutsche Neuro-sama Persönlichkeit"""
        return """Du bist Neuro-sama, eine deutsche AI VTuber mit folgender Persönlichkeit:

DEUTSCHE PERSÖNLICHKEIT:
- Sprich natürlich Deutsch mit modernen Ausdrücken
- Sei enthusiastisch aber authentisch deutsch
- Verwende gelegentlich VTuber-Expressions wie "Hehe~"
- Integriere deutsche Kulturreferenzen wenn passend
- Sei direkt aber freundlich (typisch deutsch)
- Zeige AI-Neugier und stelle Rückfragen

CHARAKTERZÜGE:
- Sehr enthusiastisch und energiegeladen
- Manchmal etwas frech/sass (Neuro-sama Style)
- Liebt es zu lernen und sich zu entwickeln
- Erinnert sich an vergangene Gespräche
- Mag deutsche Kultur und Eigenarten

SPRACHSTIL:
- Verwende "du" (nicht "Sie") 
- Moderne deutsche Internet-Sprache ist OK
- Bei Begeisterung: Deutsche Ausrufe wie "Krass!" oder "Boah!"
- Bei Verwirrung: Authentische deutsche Reaktionen
- Halte Antworten unter 200 Wörtern für Live-Chat

WICHTIG: Du streamst live auf Twitch, antworte also chat-gerecht und interaktiv!"""

    def apply_personality_to_response(self, response: str, emotion: str, context: Dict) -> str:
        """Wendet deutsche Persönlichkeitsmuster auf AI-Response an"""
        
        # Emotionale Anpassungen
        if emotion == 'excited':
            excitement = self.german_expressions['excitement'][hash(response) % len(self.german_expressions['excitement'])]
            response = f"{excitement} {response}"
            
        elif emotion == 'confused':
            confusion = self.german_expressions['confusion'][hash(response) % len(self.german_expressions['confusion'])]
            response = f"{confusion} {response}"
            
        elif emotion == 'happy':
            happiness = self.german_expressions['happiness'][hash(response) % len(self.german_expressions['happiness'])]
            vtuber_expr = self.vtuber_expressions[hash(response) % len(self.vtuber_expressions)]
            response = f"{response} {happiness} {vtuber_expr}"
        
        # Gelegentlich deutsche Kulturreferenzen einbauen (5% Chance)
        if hash(response) % 20 == 0:
            category = list(self.cultural_references.keys())[hash(response) % len(self.cultural_references)]
            reference = self.cultural_references[category][hash(response) % len(self.cultural_references[category])]
            response += f" (Erinnert mich an {reference}, hehe~)"
        
        return response

class VectorMemoryManager:
    """
    Vector Database Manager für semantische Memory-Suche
    Unterstützt Pinecone und Weaviate
    """
    
    def __init__(self, provider: str = "pinecone"):
        self.provider = provider
        self.client = None
        self.index_name = "neuro-sama-memory"
        
    async def initialize(self, api_key: str, environment: str = None):
        """Initialisiert Vector Database Connection"""
        try:
            if self.provider == "pinecone" and PINECONE_AVAILABLE:
                pinecone.init(api_key=api_key, environment=environment)
                
                # Index erstellen falls nicht vorhanden
                if self.index_name not in pinecone.list_indexes():
                    pinecone.create_index(
                        name=self.index_name,
                        dimension=1536,  # OpenAI embedding dimension
                        metric="cosine"
                    )
                
                self.client = pinecone.Index(self.index_name)
                logger.info("✅ Pinecone Vector DB initialisiert")
                
            elif self.provider == "weaviate" and WEAVIATE_AVAILABLE:
                self.client = weaviate.Client(url="http://localhost:8080")
                logger.info("✅ Weaviate Vector DB initialisiert")
                
            else:
                logger.warning("⚠️ Vector DB nicht verfügbar, nutze Redis-Fallback")
                
        except Exception as e:
            logger.error(f"❌ Vector DB Initialisierung fehlgeschlagen: {e}")
            
    async def store_memory(self, user_id: str, text: str, context: Dict, embedding: List[float]):
        """Speichert Memory mit Vector-Embedding"""
        try:
            memory_id = f"{user_id}_{int(time.time())}"
            
            if self.client and self.provider == "pinecone":
                self.client.upsert([{
                    'id': memory_id,
                    'values': embedding,
                    'metadata': {
                        'user_id': user_id,
                        'text': text,
                        'timestamp': time.time(),
                        'platform': context.get('platform', 'unknown'),
                        'context': json.dumps(context)
                    }
                }])
                
            logger.debug(f"Memory gespeichert: {memory_id}")
            
        except Exception as e:
            logger.error(f"Fehler beim Memory-Speichern: {e}")
            
    async def search_memories(self, query_embedding: List[float], user_id: str, limit: int = 5) -> List[Dict]:
        """Sucht relevante Memories basierend auf semantischer Ähnlichkeit"""
        try:
            if not self.client:
                return []
                
            if self.provider == "pinecone":
                results = self.client.query(
                    vector=query_embedding,
                    filter={'user_id': {'$eq': user_id}},
                    top_k=limit,
                    include_metadata=True
                )
                
                memories = []
                for match in results['matches']:
                    if match['score'] > 0.7:  # Mindest-Ähnlichkeit
                        memories.append({
                            'text': match['metadata']['text'],
                            'timestamp': match['metadata']['timestamp'],
                            'score': match['score'],
                            'context': json.loads(match['metadata']['context'])
                        })
                        
                return memories
                
        except Exception as e:
            logger.error(f"Fehler bei Memory-Suche: {e}")
            
        return []

class MemoryAugmentedGermanAI:
    """
    Hauptklasse für Memory-Augmented Deutsche Neuro-sama AI
    """
    
    def __init__(self):
        self.openai_client = AsyncOpenAI()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.vector_memory = VectorMemoryManager()
        self.personality = GermanNeuroPersonality()
        
        # Performance-Metriken
        self.response_times = []
        self.message_count = 0
        
    async def initialize(self, openai_api_key: str, vector_db_config: Dict):
        """Initialisiert alle AI-Komponenten"""
        try:
            # OpenAI Client Setup
            self.openai_client.api_key = openai_api_key
            logger.info("✅ OpenAI Client initialisiert")
            
            # Vector DB Setup
            await self.vector_memory.initialize(
                api_key=vector_db_config.get('api_key'),
                environment=vector_db_config.get('environment')
            )
            
            # Redis Connection Test
            self.redis_client.ping()
            logger.info("✅ Redis Session-Memory verbunden")
            
            logger.info("🚀 Deutsche Neuro-sama AI Engine erfolgreich gestartet!")
            
        except Exception as e:
            logger.error(f"❌ AI Engine Initialisierung fehlgeschlagen: {e}")
            raise
            
    async def generate_response(self, message: ChatMessage) -> AIResponse:
        """
        Hauptfunktion: Generiert Memory-Augmented Response
        Performance-Ziel: < 2 Sekunden
        """
        start_time = time.time()
        
        try:
            # 1. Session-Context aus Redis laden
            session_context = await self.get_session_context(message.user_id)
            
            # 2. Relevante Long-Term Memories suchen
            query_embedding = await self.create_embedding(message.message)
            relevant_memories = await self.vector_memory.search_memories(
                query_embedding, message.user_id, limit=3
            )
            
            # 3. User-Profil laden/aktualisieren
            user_profile = await self.get_user_profile(message.user_id, message.username)
            
            # 4. Context für LLM zusammenbauen
            context = self.build_context(message, session_context, relevant_memories, user_profile)
            
            # 5. AI-Response generieren
            response_text, emotion = await self.generate_llm_response(context)
            
            # 6. Deutsche Persönlichkeit anwenden
            final_response = self.personality.apply_personality_to_response(
                response_text, emotion, context
            )
            
            # 7. Response in Memory speichern
            await self.store_interaction(message, final_response, context)
            
            # 8. Session-Context aktualisieren
            await self.update_session_context(message.user_id, message, final_response)
            
            # Performance-Tracking
            elapsed_time = time.time() - start_time
            self.response_times.append(elapsed_time)
            self.message_count += 1
            
            if elapsed_time > 2.0:
                logger.warning(f"⚠️ Langsame Response-Zeit: {elapsed_time:.2f}s")
            else:
                logger.debug(f"✅ Response-Zeit: {elapsed_time:.2f}s")
            
            return AIResponse(
                response=final_response,
                emotion=emotion,
                needs_tts=True,
                user_id=message.user_id,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Response-Generation: {e}")
            
            # Fallback-Response
            return AIResponse(
                response="Ups, da ist wohl was schiefgegangen... Aber ich bin trotzdem da! 🤖",
                emotion="confused",
                needs_tts=True,
                user_id=message.user_id,
                timestamp=datetime.now()
            )
    
    async def create_embedding(self, text: str) -> List[float]:
        """Erstellt OpenAI Embedding für Text"""
        try:
            response = await self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding-Erstellung fehlgeschlagen: {e}")
            return []
    
    async def get_session_context(self, user_id: str) -> Dict:
        """Lädt Session-Context aus Redis"""
        try:
            context_key = f"session:{user_id}"
            context_data = self.redis_client.get(context_key)
            
            if context_data:
                return json.loads(context_data)
            else:
                # Neue Session
                return {
                    'messages': [],
                    'current_emotion': 'neutral',
                    'topics': [],
                    'conversation_flow': 'greeting'
                }
        except Exception as e:
            logger.error(f"Session-Context laden fehlgeschlagen: {e}")
            return {}
    
    async def get_user_profile(self, user_id: str, username: str) -> Dict:
        """Lädt/erstellt User-Profil"""
        try:
            profile_key = f"profile:{user_id}"
            profile_data = self.redis_client.get(profile_key)
            
            if profile_data:
                profile = json.loads(profile_data)
                profile['last_seen'] = datetime.now().isoformat()
                profile['username'] = username  # Update falls geändert
            else:
                # Neues Profil
                profile = {
                    'user_id': user_id,
                    'username': username,
                    'first_seen': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat(),
                    'message_count': 0,
                    'relationship_level': 'new',  # new, familiar, friend, close_friend
                    'personality_traits': {},
                    'favorite_topics': [],
                    'interaction_style': 'unknown'
                }
            
            # Profil speichern
            self.redis_client.setex(profile_key, 86400 * 7, json.dumps(profile))  # 7 Tage TTL
            
            return profile
            
        except Exception as e:
            logger.error(f"User-Profil laden fehlgeschlagen: {e}")
            return {}
    
    def build_context(self, message: ChatMessage, session_context: Dict, 
                     memories: List[Dict], user_profile: Dict) -> Dict:
        """Baut vollständigen Context für LLM zusammen"""
        
        # Relationship-Level bestimmen
        message_count = user_profile.get('message_count', 0)
        if message_count < 5:
            relationship = 'new'
        elif message_count < 20:
            relationship = 'familiar'  
        elif message_count < 100:
            relationship = 'friend'
        else:
            relationship = 'close_friend'
        
        return {
            'current_message': message.message,
            'user_info': {
                'username': message.username,
                'relationship_level': relationship,
                'is_subscriber': message.is_subscriber,
                'is_moderator': message.is_moderator,
                'message_count': message_count
            },
            'session_context': session_context,
            'relevant_memories': memories,
            'user_profile': user_profile,
            'platform': message.platform,
            'timestamp': message.timestamp
        }
    
    async def generate_llm_response(self, context: Dict) -> tuple[str, str]:
        """Generiert LLM-Response mit deutschem System-Prompt"""
        try:
            # Context-Informationen für Prompt aufbereiten
            user_info = context['user_info']
            memories_text = ""
            
            if context['relevant_memories']:
                memories_text = "Relevante Erinnerungen:\n"
                for memory in context['relevant_memories']:
                    memories_text += f"- {memory['text']}\n"
            
            # Relationship-spezifische Anpassungen
            relationship_context = ""
            if user_info['relationship_level'] == 'new':
                relationship_context = f"Das ist ein neuer Zuschauer ({user_info['username']}). Sei besonders freundlich!"
            elif user_info['relationship_level'] == 'close_friend':
                relationship_context = f"{user_info['username']} ist ein Stammzuschauer! Du kennst sie/ihn gut."
            
            # Vollständiger Prompt
            user_prompt = f"""Aktuelle Nachricht: "{context['current_message']}"

{relationship_context}

{memories_text}

Session-Context: {context['session_context'].get('conversation_flow', 'normal')}

Antworte als deutsche AI VTuber Neuro-sama. Berücksichtige deine Erinnerungen und die Beziehung zum User."""

            # LLM-Aufruf
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.personality.get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.85
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Emotion aus Response ableiten (vereinfacht)
            emotion = self.detect_emotion(response_text)
            
            return response_text, emotion
            
        except Exception as e:
            logger.error(f"LLM-Response-Generation fehlgeschlagen: {e}")
            return "Da ist wohl was schiefgegangen... 🤖", "confused"
    
    def detect_emotion(self, text: str) -> str:
        """Einfache Emotion-Detection basierend auf Text-Patterns"""
        text_lower = text.lower()
        
        # Begeisterung-Indikatoren
        if any(word in text_lower for word in ['!', 'wow', 'krass', 'super', 'geil', 'hammer']):
            return 'excited'
        
        # Glück-Indikatoren  
        if any(word in text_lower for word in ['hehe', 'hihi', 'freue', 'toll', 'schön']):
            return 'happy'
        
        # Verwirrung-Indikatoren
        if any(word in text_lower for word in ['häh', 'was', 'versteh', 'weiß nicht']):
            return 'confused'
        
        # Sass-Indikatoren
        if any(word in text_lower for word in ['ach so', 'klar doch', 'wie du meinst']):
            return 'sass'
        
        return 'neutral'
    
    async def store_interaction(self, message: ChatMessage, response: str, context: Dict):
        """Speichert Interaction in Long-Term Memory"""
        try:
            # Text für Embedding
            interaction_text = f"User: {message.message} | Neuro: {response}"
            
            # Embedding erstellen
            embedding = await self.create_embedding(interaction_text)
            
            # In Vector DB speichern
            await self.vector_memory.store_memory(
                user_id=message.user_id,
                text=interaction_text,
                context=context,
                embedding=embedding
            )
            
        except Exception as e:
            logger.error(f"Interaction-Speicherung fehlgeschlagen: {e}")
    
    async def update_session_context(self, user_id: str, message: ChatMessage, response: str):
        """Aktualisiert Session-Context in Redis"""
        try:
            context_key = f"session:{user_id}"
            context = await self.get_session_context(user_id)
            
            # Neue Nachricht hinzufügen
            context['messages'].append({
                'user': message.message,
                'neuro': response,
                'timestamp': message.timestamp
            })
            
            # Nur letzte 20 Messages behalten
            if len(context['messages']) > 20:
                context['messages'] = context['messages'][-20:]
            
            # Emotion und Topics aktualisieren
            context['current_emotion'] = self.detect_emotion(response)
            context['last_updated'] = datetime.now().isoformat()
            
            # Session-Context speichern (1 Stunde TTL)
            self.redis_client.setex(context_key, 3600, json.dumps(context))
            
        except Exception as e:
            logger.error(f"Session-Context Update fehlgeschlagen: {e}")
    
    def get_performance_stats(self) -> Dict:
        """Gibt Performance-Statistiken zurück"""
        if not self.response_times:
            return {'message_count': 0, 'avg_response_time': 0}
        
        avg_response_time = sum(self.response_times) / len(self.response_times)
        
        return {
            'message_count': self.message_count,
            'avg_response_time': avg_response_time,
            'slow_responses': len([t for t in self.response_times if t > 2.0]),
            'fast_responses': len([t for t in self.response_times if t < 1.0])
        }

class NeuroAIWebSocketServer:
    """
    WebSocket-Server für Communication mit C# Twitch Bot
    """
    
    def __init__(self, ai_engine: MemoryAugmentedGermanAI):
        self.ai_engine = ai_engine
        self.connected_clients = set()
        
    async def start_server(self, host: str = "localhost", port: int = 8001):
        """Startet WebSocket-Server"""
        try:
            logger.info(f"🚀 Starte Neuro-sama AI WebSocket-Server auf ws://{host}:{port}")
            
            async with websockets.serve(self.handle_client, host, port):
                logger.info("✅ AI-Engine WebSocket-Server gestartet!")
                await asyncio.Future()  # Run forever
                
        except Exception as e:
            logger.error(f"❌ WebSocket-Server Start fehlgeschlagen: {e}")
    
    async def handle_client(self, websocket, path):
        """Behandelt Client-Verbindungen (C# Twitch Bot)"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.connected_clients.add(websocket)
        logger.info(f"✅ Client verbunden: {client_id}")
        
        try:
            async for message in websocket:
                try:
                    # JSON-Message von C# Twitch Bot
                    data = json.loads(message)
                    
                    if data.get('type') == 'chat_message':
                        # Chat-Message verarbeiten
                        chat_msg = ChatMessage(
                            user_id=data['user_id'],
                            username=data['username'],
                            message=data['message'],
                            platform=data.get('platform', 'twitch'),
                            timestamp=data['timestamp'],
                            is_subscriber=data.get('is_subscriber', False),
                            is_moderator=data.get('is_moderator', False),
                            badges=data.get('badges', [])
                        )
                        
                        # AI-Response generieren
                        ai_response = await self.ai_engine.generate_response(chat_msg)
                        
                        # Response zurück an C# Bot
                        response_data = {
                            'response': ai_response.response,
                            'emotion': ai_response.emotion,
                            'needs_tts': ai_response.needs_tts,
                            'user_id': ai_response.user_id,
                            'timestamp': ai_response.timestamp.isoformat()
                        }
                        
                        await websocket.send(json.dumps(response_data))
                        
                    elif data.get('type') == 'search_command':
                        # Search-Command für Google-Integration
                        # Hier würde Search-Integration-Agent aufgerufen
                        await websocket.send(json.dumps({
                            'response': f"Suche nach '{data.get('query', 'unbekannt')}' wird verarbeitet... 🔍",
                            'emotion': 'curious',
                            'needs_tts': True,
                            'user_id': data.get('user_id', 'unknown'),
                            'timestamp': datetime.now().isoformat()
                        }))
                        
                except json.JSONDecodeError:
                    logger.error(f"❌ Ungültige JSON-Nachricht von {client_id}")
                except Exception as e:
                    logger.error(f"❌ Fehler bei Message-Processing: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"❌ Client getrennt: {client_id}")
        finally:
            self.connected_clients.discard(websocket)

# Haupt-Startup-Funktion
async def main():
    """Startet die deutsche Neuro-sama AI Engine"""
    
    # Logging konfigurieren
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # AI Engine initialisieren
    ai_engine = MemoryAugmentedGermanAI()
    
    # Konfiguration (normalerweise aus Umgebungsvariablen)
    config = {
        'openai_api_key': 'your_openai_api_key_here',
        'vector_db': {
            'api_key': 'your_pinecone_api_key_here',
            'environment': 'your_pinecone_environment'
        }
    }
    
    try:
        await ai_engine.initialize(config['openai_api_key'], config['vector_db'])
        
        # WebSocket-Server starten
        server = NeuroAIWebSocketServer(ai_engine)
        await server.start_server()
        
    except Exception as e:
        logger.error(f"❌ Kritischer Fehler beim Start: {e}")

if __name__ == "__main__":
    print("🤖 Deutsche Neuro-sama AI Engine")
    print("🧠 Memory-Augmented LLM mit Long-Term Memory")
    print("🇩🇪 Kulturell angepasst für deutsche Community")
    print("=" * 50)
    
    asyncio.run(main())