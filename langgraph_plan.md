# LangGraph Chatbot with Short and Long-Term Memory - Complete Implementation Guide

## Overview

This document provides a comprehensive guide for implementing a conversational agent using LangGraph with dual memory systems (short-term and long-term) using PostgreSQL with PgVector, integrated with Google Generative AI and MCP tools.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   LangGraph     │───▶│  Google GenAI   │
└─────────────────┘    │   Workflow      │    │   (Gemini)      │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Memory System  │    │   MCP Tools     │
                       │                 │    │                 │
                       │ Short-term:     │    │ HTTP Server     │
                       │ - Chronological │    │ Integration     │
                       │ - Recent N msgs │    └─────────────────┘
                       │                 │
                       │ Long-term:      │
                       │ - Embeddings    │
                       │ - Similarity    │
                       │ - PgVector      │
                       └─────────────────┘
```

## Key Features

- **Dual Memory System**: Short-term (chronological) and long-term (semantic) memory
- **Session Management**: Per-user and per-session isolation with `user_id` and `session_id`
- **Natural Language Memory Query**: Agent can search long-term memory using natural language
- **MCP Tools Integration**: Access to external tools via HTTP MCP server
- **Memory Tool**: Agent can explicitly query long-term memories as a tool
- **Configurable Limits**: `short_term_limit` and `long_term_limit` parameters
- **New Session Handling**: Clear short-term memory, retain long-term memory

## Database Schema

### Core Tables

```sql
-- Short-term memory (chronological)
CREATE TABLE langgraph_memory_short_term (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    content_raw JSONB, -- Raw response data
    type VARCHAR(50) DEFAULT 'history',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_user_session (user_id, session_id),
    INDEX idx_created_at (created_at)
);

-- Long-term memory (semantic)
CREATE TABLE langgraph_memory_long_term (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    embedding VECTOR(768), -- Google textembedding-gecko dimension
    type VARCHAR(50) DEFAULT 'embedding',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_user_session (user_id, session_id),
    INDEX idx_embedding USING ivfflat (embedding vector_cosine_ops)
);
```

## Implementation Components

### 1. Memory Models (SQLAlchemy)

```python
from sqlalchemy import String, Text, func, TIMESTAMP, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
import datetime
from src.db.database import Base

class ShortTermMemory(Base):
    __tablename__ = 'langgraph_memory_short_term'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_raw: Mapped[dict] = mapped_column(JSON, nullable=True)
    type: Mapped[str] = mapped_column(String(50), default='history', nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

class LongTermMemory(Base):
    __tablename__ = 'langgraph_memory_long_term'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(768))
    type: Mapped[str] = mapped_column(String(50), default='embedding', nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )
```

### 2. Memory Repository

```python
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, union_all, literal_column
from src.services.lang_graph.models import ShortTermMemory, LongTermMemory
from typing import Optional, List, Dict, Any

class MemoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_message(
        self, 
        user_id: str, 
        session_id: str,
        content: str, 
        content_type: str, 
        embedding: list[float], 
        content_raw: Optional[Dict[str, Any]] = None
    ):
        # Add to short-term memory
        short_term = ShortTermMemory(
            user_id=user_id,
            session_id=session_id,
            content=content, 
            content_type=content_type, 
            content_raw=content_raw
        )
        
        # Add to long-term memory
        long_term = LongTermMemory(
            user_id=user_id,
            session_id=session_id,
            content=content,
            content_type=content_type,
            embedding=embedding,
        )
        
        self.session.add_all([short_term, long_term])
        self.session.commit()

    def get_unified_memory(
        self, 
        user_id: str, 
        session_id: str,
        query_embedding: list[float], 
        short_term_limit: int = 10, 
        long_term_limit: int = 5
    ) -> List[Dict[str, Any]]:
        
        # Query for long-term memory (embeddings)
        embedding_query = (
            select(
                LongTermMemory.content,
                LongTermMemory.content_type,
                literal_column("'embedding'").label("type"),
                LongTermMemory.created_at
            )
            .where(
                LongTermMemory.user_id == user_id,
                LongTermMemory.session_id == session_id
            )
            .order_by(LongTermMemory.embedding.cosine_distance(query_embedding))
            .limit(long_term_limit)
        )

        # Query for short-term memory (chronological)
        history_query = (
            select(
                ShortTermMemory.content,
                ShortTermMemory.content_type,
                literal_column("'history'").label("type"),
                ShortTermMemory.created_at
            )
            .where(
                ShortTermMemory.user_id == user_id,
                ShortTermMemory.session_id == session_id
            )
            .order_by(desc(ShortTermMemory.created_at))
            .limit(short_term_limit)
        )
        
        # Unify queries
        unified_query = union_all(embedding_query, history_query)
        result = self.session.execute(unified_query)
        
        return [row._asdict() for row in result.all()]

    def search_long_term_memory(
        self, 
        user_id: str, 
        session_id: str,
        query_embedding: list[float], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search long-term memory with natural language query"""
        query = (
            select(
                LongTermMemory.content,
                LongTermMemory.content_type,
                LongTermMemory.created_at
            )
            .where(
                LongTermMemory.user_id == user_id,
                LongTermMemory.session_id == session_id
            )
            .order_by(LongTermMemory.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        result = self.session.execute(query)
        return [row._asdict() for row in result.all()]

    def clear_session_short_term_memory(
        self, 
        user_id: str, 
        session_id: str
    ):
        """Clear short-term memory for a specific session"""
        self.session.query(ShortTermMemory).filter(
            ShortTermMemory.user_id == user_id,
            ShortTermMemory.session_id == session_id
        ).delete()
        self.session.commit()
```

### 3. Embedding Service

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.config import env

class EmbeddingService:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=env.GOOGLE_API_KEY
        )
    
    def get_embedding(self, text: str) -> list[float]:
        """Get embedding for text"""
        return self.embeddings.embed_query(text)
    
    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for multiple texts"""
        return self.embeddings.embed_documents(texts)
```

### 4. Chat Model Factory

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import BaseTool
from typing import Optional, List

class ChatModelFactory:
    @staticmethod
    def create(
        model_name: str = "gemini-1.5-pro",
        temperature: float = 0.7,
        tools: Optional[List[BaseTool]] = None
    ) -> ChatGoogleGenerativeAI:
        """Create ChatGoogleGenerativeAI instance with optional tools"""
        model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=env.GOOGLE_API_KEY
        )
        
        if tools:
            model = model.bind_tools(tools)
        
        return model
```

### 5. MCP Tools Integration

```python
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from src.config import env
import asyncio

async def get_mcp_tools() -> List[BaseTool]:
    """Initialize MCP client and get available tools"""
    client = MultiServerMCPClient(
        {
            "mcp_server": {
                "transport": "streamable_http",
                "url": env.MCP_SERVER_URL,
                "headers": {
                    "Authorization": f"Bearer {env.MCP_API_TOKEN}",
                },
            },
        }
    )
    tools = await client.get_tools()
    return tools

class MemorySearchTool(BaseTool):
    name = "search_long_term_memory"
    description = "Search long-term memory for relevant information using natural language query"
    
    def __init__(self, memory_repo: MemoryRepository, embedding_service: EmbeddingService):
        super().__init__()
        self.memory_repo = memory_repo
        self.embedding_service = embedding_service
    
    def _run(self, query: str, user_id: str, session_id: str, limit: int = 5) -> str:
        """Search long-term memory with natural language query"""
        try:
            query_embedding = self.embedding_service.get_embedding(query)
            results = self.memory_repo.search_long_term_memory(
                user_id, session_id, query_embedding, limit
            )
            
            if not results:
                return "No relevant memories found."
            
            formatted_results = []
            for result in results:
                formatted_results.append(
                    f"[{result['content_type']}] {result['content']}"
                )
            
            return "\n\n".join(formatted_results)
        except Exception as e:
            return f"Error searching memory: {str(e)}"
```

### 6. LangGraph State and Nodes

```python
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

class ConversationState(TypedDict):
    user_id: str
    session_id: str
    messages: List[BaseMessage]
    final_response: dict
    memory_context: str

def load_and_prepare_context_node(state: ConversationState, config: dict):
    """Load and prepare context from both memory systems"""
    user_id = state["user_id"]
    session_id = state["session_id"]
    
    # Get original user message
    original_user_message = None
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            original_user_message = msg
            break

    if not original_user_message or not original_user_message.content.strip():
        raise ValueError("User message not found or empty")

    user_prompt = original_user_message.content.strip()

    configurable = config.get("configurable", {})
    short_term_limit = configurable.get("short_term_limit", 10)
    long_term_limit = configurable.get("long_term_limit", 5)
    system_prompt = configurable.get(
        "system_prompt",
        "You are a helpful AI assistant with access to conversation history and long-term memory."
    )

    try:
        with get_db_session() as session:
            repo = MemoryRepository(session)
            query_embedding = embedding_service.get_embedding(user_prompt)
            memories = repo.get_unified_memory(
                user_id, session_id, query_embedding, short_term_limit, long_term_limit
            )
    except Exception as e:
        print(f"Error loading memories: {e}")
        memories = []

    # Process memories
    history_mems = sorted(
        [m for m in memories if m["type"] == "history"], 
        key=lambda x: x["created_at"]
    )
    embedding_mems = [m for m in memories if m["type"] == "embedding"]

    # Build context
    context_parts = []

    if embedding_mems:
        embedding_context = "\n".join(
            [
                f"- {mem.get('content_type', 'information').capitalize()}: {mem.get('content', '')}"
                for mem in embedding_mems
                if mem.get("content")
            ]
        )
        if embedding_context:
            context_parts.append(f"## Contextual Information\n{embedding_context}")

    if history_mems:
        history_context = "\n".join(
            [
                f"- {mem.get('content_type', 'message').capitalize()}: {mem.get('content', '')}"
                for mem in history_mems
                if mem.get("content")
            ]
        )
        if history_context:
            context_parts.append(f"## Recent History\n{history_context}")

    # Build final prompt
    if context_parts:
        context_message_content = "\n\n".join(context_parts)
        full_user_prompt = (
            f"{context_message_content}\n\n"
            f"---\n\n"
            f"User question: {user_prompt}"
        )
    else:
        full_user_prompt = user_prompt

    # Build messages
    messages = []
    if system_prompt and system_prompt.strip():
        messages.append(SystemMessage(content=system_prompt.strip()))
    messages.append(HumanMessage(content=full_user_prompt.strip()))

    state["messages"] = messages
    state["memory_context"] = context_message_content if context_parts else ""
    return state

async def call_llm_node(state: ConversationState, config: dict):
    """Call LLM with tools and handle tool execution"""
    configurable = config.get("configurable", {})
    chat_model = configurable.get("chat_model")

    if not chat_model:
        raise ValueError("ChatModel instance not found in configuration.")

    # Filter valid messages
    valid_messages = []
    for msg in state["messages"]:
        if (
            isinstance(msg, (SystemMessage, HumanMessage, AIMessage))
            and msg.content
            and msg.content.strip()
        ):
            valid_messages.append(msg)

    if not valid_messages:
        raise ValueError("No valid messages found")

    try:
        response = chat_model.invoke(valid_messages)
        state["messages"].append(response)

        # Handle tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            print(f"Model requested {len(response.tool_calls)} tool(s)")

            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})
                print(f"Executing tool: {tool_name} with args: {tool_args}")

                result = await execute_tool_call(tool_name, tool_args)
                tool_results.append(f"Tool '{tool_name}' result:\n{result}")

            # Add tool results as new message
            if tool_results:
                combined_results = "\n\n".join(tool_results)
                tool_message = HumanMessage(
                    content=f"Tool execution results:\n\n{combined_results}"
                )
                state["messages"].append(tool_message)

                # Call model again to process tool results
                print("Calling model again to process tool results...")
                final_response = chat_model.invoke(state["messages"])
                state["messages"].append(final_response)

        return state
    except Exception as e:
        print(f"Error calling model: {e}")
        import traceback
        traceback.print_exc()
        raise

def save_memory_node(state: ConversationState, config: dict):
    """Save conversation to both memory systems"""
    user_id = state["user_id"]
    session_id = state["session_id"]

    try:
        # Find user and AI messages
        user_message_content = ""
        ai_message_content = ""

        # Get last AI message (final response)
        for msg in reversed(state["messages"]):
            if isinstance(msg, AIMessage):
                ai_message_content = msg.content
                break

        # Get original user question
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage) and not msg.content.startswith(
                "Tool execution results"
            ):
                content = msg.content
                if "User question:" in content:
                    user_message_content = content.split("User question:")[-1].strip()
                else:
                    user_message_content = content
                break

        # Save to memory
        if user_message_content.strip() and ai_message_content.strip():
            try:
                user_embedding = embedding_service.get_embedding(user_message_content)
                ai_embedding = embedding_service.get_embedding(ai_message_content)

                with get_db_session() as session:
                    repo = MemoryRepository(session)
                    repo.add_message(
                        user_id, session_id, user_message_content, "user", user_embedding
                    )
                    repo.add_message(
                        user_id, session_id, ai_message_content, "assistant", ai_embedding
                    )

                print(
                    f"Saved memories - User: {user_message_content[:50]}... | AI: {ai_message_content[:50]}..."
                )
            except Exception as e:
                print(f"Error saving memories: {e}")

        # Prepare final response
        response_messages = []
        for msg in state["messages"]:
            if not (
                isinstance(msg, HumanMessage)
                and msg.content.startswith("Tool execution results")
            ):
                response_messages.append(msg)

        state["final_response"] = messages_to_dict(response_messages)

    except Exception as e:
        print(f"Error in save_memory_node: {e}")
        import traceback
        traceback.print_exc()
        state["final_response"] = {"error": str(e)}

    return state
```

### 7. Graph Construction

```python
def create_memory_graph():
    """Create LangGraph with memory capabilities"""
    workflow = StateGraph(ConversationState)

    # Add nodes
    workflow.add_node("load_and_prepare_context", load_and_prepare_context_node)
    workflow.add_node("call_llm", call_llm_node)
    workflow.add_node("save_memory", save_memory_node)

    # Define linear flow
    workflow.set_entry_point("load_and_prepare_context")
    workflow.add_edge("load_and_prepare_context", "call_llm")
    workflow.add_edge("call_llm", "save_memory")
    workflow.add_edge("save_memory", END)

    # Compile graph
    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)
```

### 8. Main Service Function

```python
async def run_chatbot(
    user_id: str, 
    session_id: str,
    message: str, 
    agent_config: Dict[str, Any]
):
    """Main function to run the chatbot with memory"""
    global GLOBAL_TOOLS

    if not user_id or not session_id or not message or not message.strip():
        raise ValueError("user_id, session_id, and message are required and cannot be empty")

    try:
        # Load MCP tools
        GLOBAL_TOOLS = await get_mcp_tools()
        print(f"Loaded {len(GLOBAL_TOOLS)} MCP tools")
    except Exception as e:
        print(f"Error loading MCP tools: {e}")
        GLOBAL_TOOLS = []

    # Add memory search tool
    memory_search_tool = MemorySearchTool(memory_repo, embedding_service)
    GLOBAL_TOOLS.append(memory_search_tool)

    try:
        # Create chat model instance with tools
        chat_model_instance = ChatModelFactory.create(
            provider=agent_config.get("provider", "google"),
            model_name=agent_config.get("model_name", "gemini-1.5-pro"),
            temperature=agent_config.get("temperature", 0.7),
            tools=GLOBAL_TOOLS if GLOBAL_TOOLS else None,
        )
    except Exception as e:
        print(f"Error creating chat model: {e}")
        raise ValueError(f"Failed to initialize chat model: {e}")

    # Create graph
    app = create_memory_graph()

    config = {
        "configurable": {
            "thread_id": f"user_{user_id}_session_{session_id}",
            "chat_model": chat_model_instance,
            "system_prompt": agent_config.get(
                "system_prompt", 
                "You are a helpful AI assistant with access to conversation history and long-term memory. You can search your long-term memory using the search_long_term_memory tool when needed."
            ),
            "short_term_limit": agent_config.get("short_term_limit", 10),
            "long_term_limit": agent_config.get("long_term_limit", 5),
        }
    }

    initial_state = {
        "user_id": user_id,
        "session_id": session_id,
        "messages": [HumanMessage(content=message.strip())],
        "final_response": {},
        "memory_context": "",
    }

    try:
        # Invoke graph
        final_state = await app.ainvoke(initial_state, config=config)
        return final_state.get("final_response", {})
    except Exception as e:
        print(f"Error during chatbot execution: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Internal error: {str(e)}"}
```

### 9. Session Management

```python
class SessionManager:
    def __init__(self, memory_repo: MemoryRepository):
        self.memory_repo = memory_repo
    
    def start_new_session(self, user_id: str, session_id: str):
        """Start a new session - clears short-term memory but keeps long-term"""
        try:
            self.memory_repo.clear_session_short_term_memory(user_id, session_id)
            print(f"Started new session for user {user_id}, session {session_id}")
            return True
        except Exception as e:
            print(f"Error starting new session: {e}")
            return False
    
    def get_session_info(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        # Implementation to get session statistics
        pass
```

## New Session Behavior

When a user starts a new session:

1. **Short-term memory is cleared** - Recent chronological messages are removed
2. **Long-term memory is preserved** - Semantic embeddings remain available
3. **Context retrieval continues** - Long-term memory can still be queried for relevant information
4. **Fresh conversation flow** - The agent starts with a clean slate but maintains semantic knowledge

## Configuration Parameters

```python
DEFAULT_CONFIG = {
    "provider": "google",
    "model_name": "gemini-1.5-pro",
    "temperature": 0.7,
    "system_prompt": "You are a helpful AI assistant with access to conversation history and long-term memory.",
    "short_term_limit": 10,  # Number of recent messages to include
    "long_term_limit": 5,    # Number of similar memories to retrieve
    "memory_search_limit": 10,  # Limit for memory search tool
}
```

## Environment Variables

```bash
# Google AI
GOOGLE_API_KEY=your_google_api_key

# Database
PG_URI=postgresql://user:password@host:port/database

# MCP Server
MCP_SERVER_URL=http://localhost:8000
MCP_API_TOKEN=your_mcp_token
```

## Usage Example

```python
# Initialize services
embedding_service = EmbeddingService()
memory_repo = MemoryRepository(session)
session_manager = SessionManager(memory_repo)

# Configuration
agent_config = {
    "model_name": "gemini-1.5-pro",
    "temperature": 0.7,
    "short_term_limit": 10,
    "long_term_limit": 5,
    "system_prompt": "You are a helpful assistant..."
}

# Start new session
session_manager.start_new_session("user123", "session456")

# Run conversation
response = await run_chatbot(
    user_id="user123",
    session_id="session456", 
    message="Hello, how are you?",
    agent_config=agent_config
)

print(response)
```

## Memory Tool Usage

The agent can use the memory search tool in two ways:

1. **Automatic**: When the agent determines it needs to search long-term memory
2. **Explicit**: When the user asks the agent to search for specific information

Example tool call:
```python
{
    "name": "search_long_term_memory",
    "args": {
        "query": "What did we discuss about project deadlines?",
        "user_id": "user123",
        "session_id": "session456",
        "limit": 5
    }
}
```

## Performance Considerations

1. **Embedding Caching**: Cache embeddings for frequently accessed content
2. **Batch Operations**: Use batch operations for multiple memory operations
3. **Connection Pooling**: Implement proper database connection pooling
4. **Index Optimization**: Ensure proper indexes on user_id, session_id, and embedding columns
5. **Memory Limits**: Monitor memory usage and implement cleanup for old sessions

## Monitoring and Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add logging to key operations
logger.info(f"Loading context for user {user_id}, session {session_id}")
logger.info(f"Retrieved {len(memories)} memories")
logger.info(f"Saved memories for user {user_id}")
```

This implementation provides a robust foundation for a conversational agent with sophisticated memory management, tool integration, and session handling capabilities. 