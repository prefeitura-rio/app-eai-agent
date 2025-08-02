
**Objective:** Generate a comprehensive planning that details the architecture and implementation of a LangGraph-based conversational agent. This agent must integrate short-term and long-term memory, utilize Google Generative AI, and access external tools, all managed within a PostgreSQL database using `PgVector`.
USE THE SEARCH TOOL!!!

### 1. Core Requirements & Technology Stack

*   **Platform:** LangGraph for state management and orchestration.
*   **LLM:** `ChatGoogleGenerativeAI` and `GoogleGenerativeAIEmbeddings`.
*   **Database:** GCP Cloud SQL PostgreSQL.
*   **Vector Store:** `PgVector` via LangChain.
*   **External Tools:** `langchain_mcp_adapters` for accessing an HTTP MCP server.
*   **Agent Count:** A single conversational agent.

### 2. Memory Architecture and Management

The chatbot must maintain distinct types of memory, both stored in the PostgreSQL database.

**Short-Term Memory (STM):**
*   **Type:** Chronological history of the current session.
*   **Storage:** Managed by `session_id`.
*   **Retrieval:** Limited by the `short_term_limit` parameter (N recent messages).
*   **Session Reset:** STM is cleared when a new session is initiated.

**Long-Term Memory (LTM):**
*   **Type:** Semantic (vector-based) history across all sessions.
*   **Storage:** Managed by `user_id`.
*   **Retrieval:** Uses semantic similarity (embeddings), limited by the `long_term_limit` parameter (N relevant messages).
*   **Usage:** LTM provides contextual grounding. It is *not* cleared upon session restart.

**Memory Retrieval Flow:**
For every user query, the agent should automatically retrieve **both** STM (chronological history of the current session) and LTM (semantically similar history across all sessions) as part of the initial context.

**Session Management:**
*   Implement `user_id` to manage user identity and `session_id` to manage specific conversations (`tred_id` should be used as the `session_id`).

### 3. Agent Capabilities and Tooling

**Core Conversational Agent:**
*   The primary agent, powered by Google Generative AI.
*   Must utilize both STM and LTM in its decision-making process.

**Tools:**
1.  **MCP Server Tools:** Access to tools provided by the `langchain_mcp_adapters`. Include the provided asynchronous initialization snippet in the plan.

```python
from langchain_mcp_adapters.tools import load_mcp_tools
from src.config import env
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

async def get_mcp_tools():
    """
    Initializes the MCP client and fetches available tools asynchronously.
    """
    client = MultiServerMCPClient(
        {
            "rio_mcp": {
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
```

2.  **Long-Term Memory Retrieval Tool:**
    *   The agent must have an explicit tool it can choose to use to perform a deeper, specific search against its LTM (PgVector). This is in addition to the automatic LTM loading in the context.

### 4. Implementation Plan Structure 

*   **Database Schema:** Define the PostgreSQL table structure, including columns for `user_id`, `session_id`, `message_content`, `timestamp`, and the `embedding` vector (PgVector).
*   **Initialization:** Steps to configure the LangChain components (`ChatGoogleGenerativeAI`, `GoogleGenerativeAIEmbeddings`, `PgVector`).
*   **LangGraph State & Nodes:** Define the graph's state schema and core nodes (e.g., `RetrieveMemory`, `AgentDecision`, `ToolExecution`).
*   **Memory Management Logic:** Detailed steps on how STM (chronological) and LTM (semantic) are retrieved and presented to the LLM for each interaction, adhering to `short_term_limit` and `long_term_limit`.
*   **Tool Integration:** How the MCP tools and the LTM retrieval tool are integrated into the LangGraph state machine.
*   **Session Handling:** A clear definition of what happens when a new `session_id` is detected (STM clear, LTM persistent).





----


# LangGraph Chatbot with Short & Long-Term Memory - Implementation Plan

## Overview

This document outlines the implementation plan for creating a conversational agent using LangGraph with integrated short-term and long-term memory capabilities. The system will use Google Generative AI models, PostgreSQL with PgVector for memory storage, and MCP tools for external functionality.

## Architecture Overview

### Core Components

1. **LangGraph State Management**
   - Conversation state with user_id and session_id
   - Message history management
   - Memory retrieval and storage

2. **Unified Memory System**
   - Single table storage with embeddings
   - Short-term memory (chronological retrieval)
   - Long-term memory (semantic similarity via embeddings)
   - PostgreSQL with PgVector for vector storage

3. **LLM Integration**
   - ChatGoogleGenerativeAI for conversation
   - GoogleGenerativeAIEmbeddings for semantic search
   - Tool integration with MCP server

4. **Session Management**
   - User-based session isolation
   - Session persistence across conversations
   - Memory retrieval based on session context

## Detailed Implementation Plan

### 1. Database Schema Enhancement

#### Current Schema Analysis
The existing schema uses a unified memory table:
- `langgraph_memory_short_term`: Unified memory storage with embeddings
- Retrieval strategies:
  - **Short-term**: Chronological retrieval (recent messages)
  - **Long-term**: Semantic similarity using embeddings

#### Required Enhancements

```sql
-- Enhanced schema with session management
ALTER TABLE langgraph_memory_short_term 
ADD COLUMN session_id VARCHAR(255) NOT NULL DEFAULT 'default',
ADD INDEX idx_user_session (user_id, session_id);

-- Add memory retrieval tool table
CREATE TABLE memory_retrieval_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    retrieved_memories JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Enhanced State Management

#### ConversationState Enhancement

```python
class ConversationState(TypedDict):
    user_id: str
    session_id: str
    messages: List[BaseMessage]
    short_term_memory: List[Dict[str, Any]]  # Recent messages (chronological)
    long_term_memory: List[Dict[str, Any]]   # Semantic memories (similarity)
    memory_tool_results: List[Dict[str, Any]]  # Memory tool usage
    final_response: dict
    config: Dict[str, Any]  # Memory limits and settings
```

### 3. Memory Management System

#### Memory Repository Enhancement

```python
class EnhancedMemoryRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def add_message(self, user_id: str, session_id: str, content: str, 
                   content_type: str, embedding: list[float], 
                   content_raw: Optional[Dict[str, Any]] = None):
        """Add message to unified memory storage"""
        memory = ShortTermMemory(
            user_id=user_id,
            session_id=session_id,
            content=content,
            content_type=content_type,
            content_raw=content_raw,
            embedding=embedding
        )
        
        self.session.add(memory)
        self.session.commit()
    
    def get_short_term_memory(self, user_id: str, session_id: str, 
                             limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent messages chronologically from unified table"""
        query = (
            select(ShortTermMemory)
            .where(
                ShortTermMemory.user_id == user_id,
                ShortTermMemory.session_id == session_id
            )
            .order_by(desc(ShortTermMemory.created_at))
            .limit(limit)
        )
        
        results = self.session.execute(query).scalars().all()
        return [self._memory_to_dict(memory) for memory in results]
    
    def get_long_term_memory(self, user_id: str, session_id: str, 
                            query_embedding: list[float], 
                            limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve semantically similar memories from unified table"""
        query = (
            select(ShortTermMemory)
            .where(
                ShortTermMemory.user_id == user_id,
                ShortTermMemory.session_id == session_id
            )
            .order_by(ShortTermMemory.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        results = self.session.execute(query).scalars().all()
        return [self._memory_to_dict(memory) for memory in results]
    
    def search_memories_by_query(self, user_id: str, session_id: str,
                                query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories using natural language query"""
        query_embedding = self.embedding_service.get_embedding(query_text)
        return self.get_long_term_memory(user_id, session_id, query_embedding, limit)
```

### 4. Memory Tools Integration

#### Memory Retrieval Tool

```python
from langchain_core.tools import BaseTool
from typing import Optional

class MemoryRetrievalTool(BaseTool):
    name = "search_memories"
    description = "Search through user's conversation history and memories using natural language queries"
    
    def __init__(self, memory_repository: EnhancedMemoryRepository):
        super().__init__()
        self.memory_repository = memory_repository
    
    def _run(self, query: str, user_id: str, session_id: str, 
             limit: int = 5) -> str:
        """Search memories using natural language query"""
        try:
            memories = self.memory_repository.search_memories_by_query(
                user_id, session_id, query, limit
            )
            
            if not memories:
                return "No relevant memories found for this query."
            
            formatted_memories = []
            for memory in memories:
                formatted_memories.append(
                    f"- {memory['content_type'].capitalize()}: {memory['content']}"
                )
            
            return f"Found {len(memories)} relevant memories:\n" + "\n".join(formatted_memories)
            
        except Exception as e:
            return f"Error searching memories: {str(e)}"
    
    async def _arun(self, query: str, user_id: str, session_id: str, 
                    limit: int = 5) -> str:
        return self._run(query, user_id, session_id, limit)
```

### 5. Enhanced LangGraph Nodes

#### Context Loading Node

```python
def load_context_node(state: ConversationState, config: dict):
    """Load both short-term and long-term memory context"""
    user_id = state["user_id"]
    session_id = state["session_id"]
    
    # Get user's original message
    original_message = None
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            original_message = msg.content
            break
    
    if not original_message:
        raise ValueError("No user message found")
    
    # Configuration
    short_term_limit = config.get("short_term_limit", 10)
    long_term_limit = config.get("long_term_limit", 5)
    
    try:
        with get_db_session() as session:
            repo = EnhancedMemoryRepository(session)
            
            # Get short-term memory (chronological)
            short_term_memories = repo.get_short_term_memory(
                user_id, session_id, short_term_limit
            )
            
            # Get long-term memory (semantic similarity)
            query_embedding = embedding_service.get_embedding(original_message)
            long_term_memories = repo.get_long_term_memory(
                user_id, session_id, query_embedding, long_term_limit
            )
            
            state["short_term_memory"] = short_term_memories
            state["long_term_memory"] = long_term_memories
            
            # Build context message
            context_parts = []
            
            if short_term_memories:
                short_context = "\n".join([
                    f"- Recent ({mem['content_type']}): {mem['content']}"
                    for mem in short_term_memories
                ])
                context_parts.append(f"## Recent Conversation History\n{short_context}")
            
            if long_term_memories:
                long_context = "\n".join([
                    f"- Related ({mem['content_type']}): {mem['content']}"
                    for mem in long_term_memories
                ])
                context_parts.append(f"## Related Memories\n{long_context}")
            
            if context_parts:
                context_message = "\n\n".join(context_parts)
                enhanced_message = f"{context_message}\n\n---\n\nUser: {original_message}"
                state["messages"] = [HumanMessage(content=enhanced_message)]
            
    except Exception as e:
        print(f"Error loading context: {e}")
        # Continue without context if there's an error
    
    return state
```

#### Memory Tool Integration Node

```python
async def call_llm_with_memory_tools_node(state: ConversationState, config: dict):
    """Call LLM with memory tools and MCP tools"""
    configurable = config.get("configurable", {})
    chat_model = configurable.get("chat_model")
    
    if not chat_model:
        raise ValueError("Chat model not found in configuration")
    
    # Prepare tools
    tools = []
    
    # Add MCP tools
    try:
        mcp_tools = await get_mcp_tools()
        tools.extend(mcp_tools)
    except Exception as e:
        print(f"Error loading MCP tools: {e}")
    
    # Add memory retrieval tool
    try:
        with get_db_session() as session:
            memory_repo = EnhancedMemoryRepository(session)
            memory_tool = MemoryRetrievalTool(memory_repo)
            tools.append(memory_tool)
    except Exception as e:
        print(f"Error creating memory tool: {e}")
    
    # Bind tools to model
    if tools:
        chat_model = chat_model.bind_tools(tools)
    
    # Call LLM
    try:
        response = chat_model.invoke(state["messages"])
        state["messages"].append(response)
        
        # Handle tool calls
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})
                
                # Add user_id and session_id to memory tool calls
                if tool_name == "search_memories":
                    tool_args["user_id"] = state["user_id"]
                    tool_args["session_id"] = state["session_id"]
                
                result = await execute_tool_call(tool_name, tool_args)
                tool_results.append(f"Tool '{tool_name}' result: {result}")
            
            if tool_results:
                tool_message = HumanMessage(
                    content=f"Tool results:\n\n" + "\n\n".join(tool_results)
                )
                state["messages"].append(tool_message)
                
                # Call LLM again with tool results
                final_response = chat_model.invoke(state["messages"])
                state["messages"].append(final_response)
        
        return state
        
    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise
```

### 6. Session Management

#### Session Handling Strategy

**New Session Behavior:**
- When a new session is started, short-term memory is **reset** (new conversation)
- Long-term memory is **preserved** and can be retrieved based on semantic similarity
- The system maintains user context across sessions while allowing fresh conversation starts

**Implementation:**

```python
class SessionManager:
    def __init__(self):
        self.active_sessions = {}
    
    def start_new_session(self, user_id: str) -> str:
        """Start a new session for a user"""
        session_id = f"{user_id}_{int(time.time())}"
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "created_at": time.time(),
            "message_count": 0
        }
        return session_id
    
    def get_session_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Get session context including memory limits"""
        return {
            "user_id": user_id,
            "session_id": session_id,
            "short_term_limit": 10,  # Recent messages
            "long_term_limit": 5,    # Semantic memories
            "is_new_session": session_id not in self.active_sessions
        }
```

### 7. Enhanced Graph Construction

```python
def create_enhanced_memory_graph():
    """Create LangGraph with enhanced memory capabilities"""
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("load_context", load_context_node)
    workflow.add_node("call_llm_with_tools", call_llm_with_memory_tools_node)
    workflow.add_node("save_memory", save_memory_node)
    
    # Define flow
    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "call_llm_with_tools")
    workflow.add_edge("call_llm_with_tools", "save_memory")
    workflow.add_edge("save_memory", END)
    
    # Compile with memory saver
    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)
```

### 8. Main Service Function

```python
async def run_enhanced_chatbot(
    user_id: str, 
    session_id: str, 
    message: str, 
    agent_config: Dict[str, Any]
):
    """Run enhanced chatbot with memory capabilities"""
    
    if not user_id or not message.strip():
        raise ValueError("user_id and message are required")
    
    # Create chat model
    chat_model_instance = ChatModelFactory.create(
        provider=agent_config.get("provider", "google"),
        model_name=agent_config.get("model_name"),
        temperature=agent_config.get("temperature", 0.7)
    )
    
    # Create graph
    app = create_enhanced_memory_graph()
    
    # Configuration
    config = {
        "configurable": {
            "thread_id": f"{user_id}_{session_id}",
            "chat_model": chat_model_instance,
            "system_prompt": agent_config.get("system_prompt"),
            "short_term_limit": agent_config.get("short_term_limit", 10),
            "long_term_limit": agent_config.get("long_term_limit", 5)
        }
    }
    
    # Initial state
    initial_state = {
        "user_id": user_id,
        "session_id": session_id,
        "messages": [HumanMessage(content=message.strip())],
        "short_term_memory": [],
        "long_term_memory": [],
        "memory_tool_results": [],
        "final_response": {},
        "config": config["configurable"]
    }
    
    try:
        final_state = await app.ainvoke(initial_state, config=config)
        return final_state.get("final_response", {})
    except Exception as e:
        print(f"Error in enhanced chatbot: {e}")
        return {"error": str(e)}
```

## Memory Behavior Specifications

### Unified Memory Storage
- **Storage**: Single table (`langgraph_memory_short_term`) with embeddings
- **Data Structure**: All messages stored with embeddings for semantic search
- **Session Behavior**: Session-based isolation with user_id and session_id

### Short-Term Memory (Chronological Retrieval)
- **Retrieval Strategy**: Last N messages by creation time
- **Session Behavior**: Reset when new session starts (filtered by session_id)
- **Purpose**: Maintain conversation flow and immediate context
- **Configuration**: `short_term_limit` parameter

### Long-Term Memory (Semantic Retrieval)
- **Retrieval Strategy**: Similarity-based search using embeddings
- **Session Behavior**: Preserved across sessions (can search across all user sessions)
- **Purpose**: Provide relevant historical context based on semantic similarity
- **Configuration**: `long_term_limit` parameter

### Memory Tool Integration
- **Natural Language Queries**: Users can search memories using natural language
- **Tool Access**: Model can access memories as a tool during conversation
- **Contextual Loading**: Relevant long-term memories loaded with each query

## Configuration Parameters

```python
DEFAULT_CONFIG = {
    "provider": "google",
    "model_name": "gemini-2.5-pro-lite",
    "temperature": 0.7,
    "system_prompt": "You are a helpful assistant with access to conversation history.",
    "short_term_limit": 10,  # Number of recent messages to include
    "long_term_limit": 5,    # Number of semantic memories to retrieve
    "embedding_model": "models/embedding-001",
    "memory_search_limit": 5  # Limit for memory tool searches
}
```

## Implementation Phases

### Phase 1: Database Schema Updates
1. Add session_id columns to existing tables
2. Create memory retrieval logs table
3. Update indexes for performance

### Phase 2: Enhanced Repository
1. Implement EnhancedMemoryRepository with unified table approach
2. Add session-aware memory retrieval (chronological and semantic)
3. Implement semantic search capabilities using embeddings

### Phase 3: Memory Tools
1. Create MemoryRetrievalTool
2. Integrate with MCP tools
3. Test tool functionality

### Phase 4: LangGraph Integration
1. Update ConversationState
2. Implement enhanced nodes
3. Create enhanced graph

### Phase 5: Session Management
1. Implement SessionManager
2. Add session context handling
3. Test session isolation

### Phase 6: Testing and Optimization
1. Unit tests for all components
2. Integration testing
3. Performance optimization

## Key Benefits

1. **Session Isolation**: Clean conversation starts while preserving relevant history
2. **Semantic Memory**: Context-aware memory retrieval
3. **Natural Language Search**: Intuitive memory access
4. **Scalable Architecture**: PostgreSQL with PgVector for production use
5. **Tool Integration**: Seamless MCP and memory tool access
6. **Configurable Limits**: Adjustable memory retrieval parameters

## Next Steps

1. Review and approve this planning document
2. Begin Phase 1 implementation
3. Set up development environment with PostgreSQL and PgVector
4. Create test cases for memory behavior
5. Implement components incrementally with testing at each phase 










----


# Short-Term vs. Long-Term Memory in LangGraph

LangGraph distinguishes **short-term memory** (conversation history within one session/thread) from **long-term memory** (persistent knowledge across sessions). Short-term memory is stored in the agent’s **state** (persists via checkpoints) and scoped to a single `thread_id`. In practice, this means the agent “remembers” recent messages in the current conversation. Long-term memory lives in an external store (database/vector store) and can span threads and users. For example, LangGraph’s docs note that *“short-term memory… resets when a new thread starts”* (per `thread_id`), while long-term memory is stored in a database (e.g. Postgres+pgvector) and can be loaded as needed. In other words, if you start a new conversation (new `thread_id`), the agent’s short-term context is cleared, but long-term memory remains available across sessions if queried explicitly.

# Key Tools and Integrations

* **Chat Model**: We use Google’s Gemini chat via LangChain. The class `ChatGoogleGenerativeAI` (from `langchain_google_genai`) provides access to Gemini-family models. For example:

  ```python
  from langchain_google_genai import ChatGoogleGenerativeAI
  llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
  ```

  requires setting `GOOGLE_API_KEY` and specifying a model name. The `invoke()` method takes a list of messages (system/human/AI) and returns a response.

* **Embeddings**: We use Google’s Gemini embeddings via LangChain’s `GoogleGenerativeAIEmbeddings`. For instance:

  ```python
  from langchain_google_genai import GoogleGenerativeAIEmbeddings
  embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
  vector = embeddings.embed_query("hello, world!")
  ```

  This produces a dense embedding (e.g. 3072 dims) suitable for semantic search.

* **Vector Store (PGVector)**: We store embeddings in Postgres using the `pgvector` extension. LangChain’s **PGVector** (in `langchain-postgres` package) is a vectorstore wrapper. For example, after enabling `CREATE EXTENSION IF NOT EXISTS vector` in Cloud SQL, you can do:

  ```python
  from langchain_postgres import PGVector
  vector_store = PGVector(
      embeddings=embeddings,
      collection_name="user_memories",
      connection="postgresql+psycopg://user:pass@host:port/dbname",
      use_jsonb=True,
  )
  results = vector_store.similarity_search("search query", k=3)
  ```

  as shown in LangChain docs. The `similarity_search` method returns the top-k semantically closest documents.

* **LangGraph Stores**: Alternatively (and integrally), LangGraph provides `PostgresStore` for long-term memory with built-in support for embeddings. You can configure it with an `index` to enable pgvector-based search. For example (from LangGraph examples):

  ```python
  from langgraph.store.postgres import PostgresStore
  store = PostgresStore(conn, index={"embed": embeddings, "dims": 3072})
  store.setup()
  ```

  This allows using `store.search(namespace, query=..., limit=k)` to retrieve similar memory items. This is analogous to PGVector but tightly integrated into LangGraph’s memory APIs.

* **MCP Tools**: We have an existing MCP server of tools accessible via HTTP. The LangChain **MCP adapters** make MCP tools compatible with LangChain. Using `MultiServerMCPClient` (from `langchain_mcp_adapters.client`), we can load tools asynchronously. For example:

  ```python
  from langchain_mcp_adapters.client import MultiServerMCPClient
  client = MultiServerMCPClient({
      "rio_mcp": {
          "transport": "streamable_http",
          "url": env.MCP_SERVER_URL,
          "headers": {"Authorization": f"Bearer {env.MCP_API_TOKEN}"},
      }
  })
  tools = await client.get_tools()
  ```

  This connects to the MCP server and retrieves all available tools. These tools can then be given to our agent so it can call them as needed.

# Database Setup (Cloud SQL Postgres + PGVector)

On Google Cloud SQL (Postgres), first enable the `pgvector` extension so that vector columns are supported:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Ensure your DB user has permission to install extensions. You can then connect via SQLAlchemy or `psycopg` to this database. The `langgraph-checkpoint-postgres` and `langchain-postgres` packages require a DSN like `"postgresql://user:pass@host:port/dbname"` (for LangGraph’s `PostgresSaver`) or `"postgresql+psycopg://..."` (for PGVector).

# Configuring Short-Term Memory

Short-term memory is the conversation history within a thread. In LangGraph you attach a **checkpointer** to your `StateGraph` to persist state. For production, use a Postgres-backed saver. For example:

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, MessagesState, START
from langchain_google_genai import ChatGoogleGenerativeAI

DB_URI = "postgresql://user:pass@host:port/dbname"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    builder = StateGraph(MessagesState)   # state holds a list of messages
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    def ChatNode(state: MessagesState) -> MessagesState:
        # Invoke the chat model on the accumulated messages
        response = llm.invoke({"messages": state["messages"]})
        state["messages"] = response  # response is a list of messages
        return state
    builder.add_node("chat", ChatNode)
    builder.add_edge(START, "chat")
    graph = builder.compile(checkpointer=checkpointer)
```

This sets up a single-node graph that appends the model’s response to `state["messages"]`. On each `graph.invoke(input_state, config)`, LangGraph automatically saves a checkpoint after the node runs. By using `config={"configurable": {"thread_id": session_id}}`, the same `thread_id` will resume history. In effect, the agent remembers prior turns within that thread.

To manage length, you can trim older messages manually. LangGraph provides utilities (e.g. `trim_messages`) to drop old messages once a `short_term_limit` is exceeded. For example, after each turn you might keep only the last N messages to avoid exceeding the LLM’s context window.

# Configuring Long-Term Memory

Long-term memory is stored externally (in the Postgres DB with pgvector). We use a **PostgresStore** (or PGVector) to save and retrieve facts or past conversation snippets. Typically you namespace memory by user (or session). For example:

```python
from psycopg import Connection
from langgraph.store.postgres import PostgresStore

conn = Connection.connect(DB_URI, autocommit=True, prepare_threshold=0)
store = PostgresStore(conn, index={"embed": embeddings, "dims": 3072})
store.setup()
user_id = "user_123"
namespace = (user_id, "memories")
```

Now you can **put** items into memory. For instance, if the user reveals personal info or a preference, a tool or node can store it:

```python
# Example: storing a user profile dict
profile = {"name": "Alice", "hobby": ["hiking"]}
store.put(namespace, "profile", profile)
```

And later you can **get** or **search** it. To retrieve by key:

```python
from langgraph.config import get_store
store = get_store()
val = store.get(namespace, key="profile")
print(val.value)  # e.g. {"name":"Alice",...}
```

.

For **semantic memory**, embed-rich content is useful. You can store arbitrary JSON or text under a key with embeddings. For example (from LangGraph examples) you can store a short memory entry:

```python
memory_entry = {"food_preference": "I love Italian cuisine", "context": "Dinner plans"}
store.put(namespace, key=str(uuid.uuid4()), data=memory_entry, index=["food_preference"])
```

Here `index=["food_preference"]` tells LangGraph to embed the `food_preference` field, using our Gemini embeddings behind the scenes. Later, to retrieve relevant memories given a new query:

```python
results = store.search(namespace, query="What does the user like to eat?", limit=3)
for memory in results:
    print(memory.value)
```

This returns up to 3 entries semantically similar to the query. In the example above, it would likely return the Italian cuisine memory since it answers the query.

# Putting It All Together: Agent Workflow

A typical conversation turn works as follows:

1. **Input**: User sends a message. We package it in `{"messages": [{"role":"user","content":...}]}` along with the `thread_id` (and `user_id`) in the config.
2. **Load Short-Term History**: LangGraph (via the `PostgresSaver`) automatically fetches the previous messages for this `thread_id` and includes them in `state["messages"]`.
3. **(Optional) Retrieve Long-Term Context**: Before or during the turn, you can query long-term memory for relevant info. For example, use the last user message to do a semantic search:

   ```python
   last_input = state["messages"][-1].content
   memories = store.search(namespace, query=last_input, limit=long_term_limit)
   context = " ".join(mem.value.get("text", str(mem.value)) for mem in memories)
   ```

   Then you might prepend `context` to the system prompt for the model. This way, the agent has both recent chat turns (short-term) and retrieved knowledge (long-term) as context.
4. **Execute Chat Node**: Pass the system prompt and chat history to `ChatGoogleGenerativeAI.invoke`. For example:

   ```python
   system_msg = f"You are a helpful assistant. Use this memory: {context}"
   response = llm.invoke({"messages": [{"role": "system", "content": system_msg}] + state["messages"]})
   state["messages"] = response
   ```
5. **(Optional) Write to Memory**: After generating a response, you might choose to store new facts. For example, if the user says “Remember that my project deadline is tomorrow,” you could have a tool detect this and call `store.put(...)` to save it in long-term memory. This can be done via LangGraph tools: write-memory tools can return a `state` update or use `get_store().put(...)` inside the tool.
6. **Return Output**: Stream or return the assistant’s reply to the user. The updated state (including the latest messages) is checkpointed automatically.

You can integrate the MCP tools and a memory-search tool into the agent’s capabilities. For example, using LangGraph’s **React agent** builder:

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool

# Example memory-search tool function
def search_memory_tool(query: str):
    results = store.search(namespace, query=query, limit=long_term_limit)
    return "\n".join(str(r.value) for r in results)
search_tool = Tool.from_function(func=search_memory_tool, name="MemorySearch", description="Search long-term memory")

agent = create_react_agent(
    model=llm,
    tools=tools_from_mcp + [search_tool],
    store=store,
    checkpointer=PostgresSaver.from_conn_string(DB_URI),
    state_schema=MessagesState
)
```

This makes the memory search available as a tool the LLM can invoke. LangGraph ensures `get_store()` inside the tool refers to our `store`. The agent can then call it with a natural language query, just as it would call any other tool.

# New Sessions and Memory Limits

If the user **starts a new session or thread** (i.e. we use a new `thread_id`), the short-term memory (state) is effectively reset. The agent will no longer have the previous conversation in context. However, long-term memory (in the database) is unaffected. If continuity is needed, the agent could explicitly query the memory store for relevant past information (e.g. “Recall what I said earlier.”) to rebuild context. By default, though, LangGraph treats each new `thread_id` as a fresh conversation with no history.

We control how much memory to use via parameters. For example, set `short_term_limit = N` to keep only the last N messages in state (trimming older turns). Set `long_term_limit = M` to fetch at most M memories on each query. Tuning these parameters balances context depth vs. performance. The state (short-term) is chronological, whereas the long-term retrieval is similarity-based.

# Example Code Snippet

Below is a sketch combining these ideas (simplified):

```python
import asyncio
from psycopg import Connection
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.tools import Tool

# 1. Initialize model and embeddings
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 2. Connect to Cloud SQL Postgres (with pgvector enabled)
conn = Connection.connect("postgresql://user:pass@host:5432/dbname", autocommit=True)
store = PostgresStore(conn, index={"embed": embeddings, "dims": 3072})
store.setup()
namespace = ("user_123", "memories")

# 3. Short-term memory saver
checkpointer = PostgresSaver.from_conn_string("postgresql://user:pass@host:5432/dbname")

# 4. Load MCP tools
async def get_mcp_tools():
    client = MultiServerMCPClient({
        "rio_mcp": {"transport": "streamable_http", "url": env.MCP_SERVER_URL,
                    "headers": {"Authorization": f"Bearer {env.MCP_API_TOKEN}"}}
    })
    return await client.get_tools()
tools_from_mcp = asyncio.run(get_mcp_tools())

# 5. Define a memory-search tool
def memory_search(query: str):
    results = store.search(namespace, query=query, limit=5)
    return "\n".join(str(r.value) for r in results)
mem_tool = Tool.from_function(
    func=memory_search, name="MemorySearch",
    description="Search user's long-term memory"
)

# 6. Build the LangGraph state machine
builder = StateGraph(MessagesState)
def chat_node(state):
    # Optionally inject long-term memory context here
    last_msg = state["messages"][-1].content
    memories = store.search(namespace, query=last_msg, limit=5)
    context = " ".join(str(m.value) for m in memories)
    system_msg = f"You are an assistant. Context from memory: {context}"
    resp = llm.invoke({"messages": [{"role": "system", "content": system_msg}] + state["messages"]})
    state["messages"] = resp
    return state

builder.add_node("Chat", chat_node)
builder.add_edge(START, "Chat")
agent = builder.compile(checkpointer=checkpointer, store=store)

# 7. Conversation loop (simplified)
config = {"configurable": {"thread_id": "session_1", "user_id": "user_123"}}
state = {"messages": [{"role": "user", "content": "Hi, I love Italian food."}]}
result_state = agent.invoke(state, config=config)
print(result_state["messages"][-1].content)  # Assistant reply
```

This example shows: (a) setting up `PostgresSaver` so state persists per `thread_id`, (b) using `PostgresStore` with Gemini embeddings for long-term memory, and (c) retrieving similar memories (`store.search`) on each turn. If a new `thread_id` is used, the saved state is not automatically loaded (short-term resets), but you could still query `store` by user to reconstruct context.

# Sources

This guide is based on LangGraph and LangChain documentation and examples. These illustrate how to implement short-term (thread-scoped) memory with `PostgresSaver` and long-term semantic memory with `PostgresStore`/PGVector, using Google’s GenAI models and embeddings in a cloud Postgres (Cloud SQL) setup.




----


Great. I’ll create a detailed guide on building a single-threaded conversational agent in LangGraph that integrates both short-term and long-term memory using PostgreSQL with PgVector via LangChain. The bot will be backed by ChatGoogleGenerativeAI and GoogleGenerativeAIEmbeddings, access long-term memory using natural language queries, and interact with a MCP server as a tool.

I'll walk through memory management by `user_id` and `session_id`, usage of `short_term_limit` and `long_term_limit`, and how the system behaves when a new session is started. I’ll also show how to wrap memory access as a tool callable by the agent.

I’ll get started and update you shortly.


# Short-Term vs. Long-Term Memory in LangGraph

LangGraph distinguishes **short-term memory** (conversation history within one session/thread) from **long-term memory** (persistent knowledge across sessions). Short-term memory is stored in the agent’s **state** (persists via checkpoints) and scoped to a single `thread_id`. In practice, this means the agent “remembers” recent messages in the current conversation. Long-term memory lives in an external store (database/vector store) and can span threads and users. For example, LangGraph’s docs note that *“short-term memory… resets when a new thread starts”* (per `thread_id`), while long-term memory is stored in a database (e.g. Postgres+pgvector) and can be loaded as needed. In other words, if you start a new conversation (new `thread_id`), the agent’s short-term context is cleared, but long-term memory remains available across sessions if queried explicitly.

# Key Tools and Integrations

* **Chat Model**: We use Google’s Gemini chat via LangChain. The class `ChatGoogleGenerativeAI` (from `langchain_google_genai`) provides access to Gemini-family models. For example:

  ```python
  from langchain_google_genai import ChatGoogleGenerativeAI
  llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
  ```

  requires setting `GOOGLE_API_KEY` and specifying a model name. The `invoke()` method takes a list of messages (system/human/AI) and returns a response.

* **Embeddings**: We use Google’s Gemini embeddings via LangChain’s `GoogleGenerativeAIEmbeddings`. For instance:

  ```python
  from langchain_google_genai import GoogleGenerativeAIEmbeddings
  embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
  vector = embeddings.embed_query("hello, world!")
  ```

  This produces a dense embedding (e.g. 3072 dims) suitable for semantic search.

* **Vector Store (PGVector)**: We store embeddings in Postgres using the `pgvector` extension. LangChain’s **PGVector** (in `langchain-postgres` package) is a vectorstore wrapper. For example, after enabling `CREATE EXTENSION IF NOT EXISTS vector` in Cloud SQL, you can do:

  ```python
  from langchain_postgres import PGVector
  vector_store = PGVector(
      embeddings=embeddings,
      collection_name="user_memories",
      connection="postgresql+psycopg://user:pass@host:port/dbname",
      use_jsonb=True,
  )
  results = vector_store.similarity_search("search query", k=3)
  ```

  as shown in LangChain docs. The `similarity_search` method returns the top-k semantically closest documents.

* **LangGraph Stores**: Alternatively (and integrally), LangGraph provides `PostgresStore` for long-term memory with built-in support for embeddings. You can configure it with an `index` to enable pgvector-based search. For example (from LangGraph examples):

  ```python
  from langgraph.store.postgres import PostgresStore
  store = PostgresStore(conn, index={"embed": embeddings, "dims": 3072})
  store.setup()
  ```

  This allows using `store.search(namespace, query=..., limit=k)` to retrieve similar memory items. This is analogous to PGVector but tightly integrated into LangGraph’s memory APIs.

* **MCP Tools**: We have an existing MCP server of tools accessible via HTTP. The LangChain **MCP adapters** make MCP tools compatible with LangChain. Using `MultiServerMCPClient` (from `langchain_mcp_adapters.client`), we can load tools asynchronously. For example:

  ```python
  from langchain_mcp_adapters.client import MultiServerMCPClient
  client = MultiServerMCPClient({
      "rio_mcp": {
          "transport": "streamable_http",
          "url": env.MCP_SERVER_URL,
          "headers": {"Authorization": f"Bearer {env.MCP_API_TOKEN}"},
      }
  })
  tools = await client.get_tools()
  ```

  This connects to the MCP server and retrieves all available tools. These tools can then be given to our agent so it can call them as needed.

# Database Setup (Cloud SQL Postgres + PGVector)

On Google Cloud SQL (Postgres), first enable the `pgvector` extension so that vector columns are supported:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Ensure your DB user has permission to install extensions. You can then connect via SQLAlchemy or `psycopg` to this database. The `langgraph-checkpoint-postgres` and `langchain-postgres` packages require a DSN like `"postgresql://user:pass@host:port/dbname"` (for LangGraph’s `PostgresSaver`) or `"postgresql+psycopg://..."` (for PGVector).

# Configuring Short-Term Memory

Short-term memory is the conversation history within a thread. In LangGraph you attach a **checkpointer** to your `StateGraph` to persist state. For production, use a Postgres-backed saver. For example:

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, MessagesState, START
from langchain_google_genai import ChatGoogleGenerativeAI

DB_URI = "postgresql://user:pass@host:port/dbname"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    builder = StateGraph(MessagesState)   # state holds a list of messages
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    def ChatNode(state: MessagesState) -> MessagesState:
        # Invoke the chat model on the accumulated messages
        response = llm.invoke({"messages": state["messages"]})
        state["messages"] = response  # response is a list of messages
        return state
    builder.add_node("chat", ChatNode)
    builder.add_edge(START, "chat")
    graph = builder.compile(checkpointer=checkpointer)
```

This sets up a single-node graph that appends the model’s response to `state["messages"]`. On each `graph.invoke(input_state, config)`, LangGraph automatically saves a checkpoint after the node runs. By using `config={"configurable": {"thread_id": session_id}}`, the same `thread_id` will resume history. In effect, the agent remembers prior turns within that thread.

To manage length, you can trim older messages manually. LangGraph provides utilities (e.g. `trim_messages`) to drop old messages once a `short_term_limit` is exceeded. For example, after each turn you might keep only the last N messages to avoid exceeding the LLM’s context window.

# Configuring Long-Term Memory

Long-term memory is stored externally (in the Postgres DB with pgvector). We use a **PostgresStore** (or PGVector) to save and retrieve facts or past conversation snippets. Typically you namespace memory by user (or session). For example:

```python
from psycopg import Connection
from langgraph.store.postgres import PostgresStore

conn = Connection.connect(DB_URI, autocommit=True, prepare_threshold=0)
store = PostgresStore(conn, index={"embed": embeddings, "dims": 3072})
store.setup()
user_id = "user_123"
namespace = (user_id, "memories")
```

Now you can **put** items into memory. For instance, if the user reveals personal info or a preference, a tool or node can store it:

```python
# Example: storing a user profile dict
profile = {"name": "Alice", "hobby": ["hiking"]}
store.put(namespace, "profile", profile)
```

And later you can **get** or **search** it. To retrieve by key:

```python
from langgraph.config import get_store
store = get_store()
val = store.get(namespace, key="profile")
print(val.value)  # e.g. {"name":"Alice",...}
```

.

For **semantic memory**, embed-rich content is useful. You can store arbitrary JSON or text under a key with embeddings. For example (from LangGraph examples) you can store a short memory entry:

```python
memory_entry = {"food_preference": "I love Italian cuisine", "context": "Dinner plans"}
store.put(namespace, key=str(uuid.uuid4()), data=memory_entry, index=["food_preference"])
```

Here `index=["food_preference"]` tells LangGraph to embed the `food_preference` field, using our Gemini embeddings behind the scenes. Later, to retrieve relevant memories given a new query:

```python
results = store.search(namespace, query="What does the user like to eat?", limit=3)
for memory in results:
    print(memory.value)
```

This returns up to 3 entries semantically similar to the query. In the example above, it would likely return the Italian cuisine memory since it answers the query.

# Putting It All Together: Agent Workflow

A typical conversation turn works as follows:

1. **Input**: User sends a message. We package it in `{"messages": [{"role":"user","content":...}]}` along with the `thread_id` (and `user_id`) in the config.
2. **Load Short-Term History**: LangGraph (via the `PostgresSaver`) automatically fetches the previous messages for this `thread_id` and includes them in `state["messages"]`.
3. **(Optional) Retrieve Long-Term Context**: Before or during the turn, you can query long-term memory for relevant info. For example, use the last user message to do a semantic search:

   ```python
   last_input = state["messages"][-1].content
   memories = store.search(namespace, query=last_input, limit=long_term_limit)
   context = " ".join(mem.value.get("text", str(mem.value)) for mem in memories)
   ```

   Then you might prepend `context` to the system prompt for the model. This way, the agent has both recent chat turns (short-term) and retrieved knowledge (long-term) as context.
4. **Execute Chat Node**: Pass the system prompt and chat history to `ChatGoogleGenerativeAI.invoke`. For example:

   ```python
   system_msg = f"You are a helpful assistant. Use this memory: {context}"
   response = llm.invoke({"messages": [{"role": "system", "content": system_msg}] + state["messages"]})
   state["messages"] = response
   ```
5. **(Optional) Write to Memory**: After generating a response, you might choose to store new facts. For example, if the user says “Remember that my project deadline is tomorrow,” you could have a tool detect this and call `store.put(...)` to save it in long-term memory. This can be done via LangGraph tools: write-memory tools can return a `state` update or use `get_store().put(...)` inside the tool.
6. **Return Output**: Stream or return the assistant’s reply to the user. The updated state (including the latest messages) is checkpointed automatically.

You can integrate the MCP tools and a memory-search tool into the agent’s capabilities. For example, using LangGraph’s **React agent** builder:

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool

# Example memory-search tool function
def search_memory_tool(query: str):
    results = store.search(namespace, query=query, limit=long_term_limit)
    return "\n".join(str(r.value) for r in results)
search_tool = Tool.from_function(func=search_memory_tool, name="MemorySearch", description="Search long-term memory")

agent = create_react_agent(
    model=llm,
    tools=tools_from_mcp + [search_tool],
    store=store,
    checkpointer=PostgresSaver.from_conn_string(DB_URI),
    state_schema=MessagesState
)
```

This makes the memory search available as a tool the LLM can invoke. LangGraph ensures `get_store()` inside the tool refers to our `store`. The agent can then call it with a natural language query, just as it would call any other tool.

# New Sessions and Memory Limits

If the user **starts a new session or thread** (i.e. we use a new `thread_id`), the short-term memory (state) is effectively reset. The agent will no longer have the previous conversation in context. However, long-term memory (in the database) is unaffected. If continuity is needed, the agent could explicitly query the memory store for relevant past information (e.g. “Recall what I said earlier.”) to rebuild context. By default, though, LangGraph treats each new `thread_id` as a fresh conversation with no history.

We control how much memory to use via parameters. For example, set `short_term_limit = N` to keep only the last N messages in state (trimming older turns). Set `long_term_limit = M` to fetch at most M memories on each query. Tuning these parameters balances context depth vs. performance. The state (short-term) is chronological, whereas the long-term retrieval is similarity-based.

# Example Code Snippet

Below is a sketch combining these ideas (simplified):

```python
import asyncio
from psycopg import Connection
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.graph import StateGraph, MessagesState, START
from langchain_core.tools import Tool

# 1. Initialize model and embeddings
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 2. Connect to Cloud SQL Postgres (with pgvector enabled)
conn = Connection.connect("postgresql://user:pass@host:5432/dbname", autocommit=True)
store = PostgresStore(conn, index={"embed": embeddings, "dims": 3072})
store.setup()
namespace = ("user_123", "memories")

# 3. Short-term memory saver
checkpointer = PostgresSaver.from_conn_string("postgresql://user:pass@host:5432/dbname")

# 4. Load MCP tools
async def get_mcp_tools():
    client = MultiServerMCPClient({
        "rio_mcp": {"transport": "streamable_http", "url": env.MCP_SERVER_URL,
                    "headers": {"Authorization": f"Bearer {env.MCP_API_TOKEN}"}}
    })
    return await client.get_tools()
tools_from_mcp = asyncio.run(get_mcp_tools())

# 5. Define a memory-search tool
def memory_search(query: str):
    results = store.search(namespace, query=query, limit=5)
    return "\n".join(str(r.value) for r in results)
mem_tool = Tool.from_function(
    func=memory_search, name="MemorySearch",
    description="Search user's long-term memory"
)

# 6. Build the LangGraph state machine
builder = StateGraph(MessagesState)
def chat_node(state):
    # Optionally inject long-term memory context here
    last_msg = state["messages"][-1].content
    memories = store.search(namespace, query=last_msg, limit=5)
    context = " ".join(str(m.value) for m in memories)
    system_msg = f"You are an assistant. Context from memory: {context}"
    resp = llm.invoke({"messages": [{"role": "system", "content": system_msg}] + state["messages"]})
    state["messages"] = resp
    return state

builder.add_node("Chat", chat_node)
builder.add_edge(START, "Chat")
agent = builder.compile(checkpointer=checkpointer, store=store)

# 7. Conversation loop (simplified)
config = {"configurable": {"thread_id": "session_1", "user_id": "user_123"}}
state = {"messages": [{"role": "user", "content": "Hi, I love Italian food."}]}
result_state = agent.invoke(state, config=config)
print(result_state["messages"][-1].content)  # Assistant reply
```

This example shows: (a) setting up `PostgresSaver` so state persists per `thread_id`, (b) using `PostgresStore` with Gemini embeddings for long-term memory, and (c) retrieving similar memories (`store.search`) on each turn. If a new `thread_id` is used, the saved state is not automatically loaded (short-term resets), but you could still query `store` by user to reconstruct context.

# Sources

This guide is based on LangGraph and LangChain documentation and examples. These illustrate how to implement short-term (thread-scoped) memory with `PostgresSaver` and long-term semantic memory with `PostgresStore`/PGVector, using Google’s GenAI models and embeddings in a cloud Postgres (Cloud SQL) setup.



----


import os
import json
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    messages_to_dict,
)
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from src.services.lang_graph.llms import EmbeddingService, ChatModelFactory
from src.services.lang_graph.repository import MemoryRepository
from src.db.database import get_db_session
from src.services.lang_graph.tools import get_mcp_tools


# --- 1. Definição do Estado do Grafo (Minimalista) ---
class ConversationState(TypedDict):
    user_id: str
    messages: List[BaseMessage]
    final_response: dict


# --- 2. Inicialização de Serviços Globais ---
embedding_service = EmbeddingService()

# Variável global para armazenar ferramentas (evita serialização)
GLOBAL_TOOLS = []


# --- 3. Função auxiliar para executar ferramentas ---
async def execute_tool_call(tool_name: str, tool_args: dict) -> str:
    """Executa uma ferramenta específica e retorna o resultado como string"""
    global GLOBAL_TOOLS
    
    for tool in GLOBAL_TOOLS:
        if tool.name == tool_name:
            try:
                if hasattr(tool, 'ainvoke'):
                    result = await tool.ainvoke(tool_args)
                else:
                    result = tool.invoke(tool_args)
                return str(result)
            except Exception as e:
                return f"Erro ao executar {tool_name}: {str(e)}"
    
    return f"Ferramenta '{tool_name}' não encontrada"


# --- 4. Nós do Grafo ---
def load_and_prepare_context_node(state: ConversationState, config: dict):
    user_id = state["user_id"]
    
    # Pega a mensagem original do usuário
    original_user_message = None
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            original_user_message = msg
            break
    
    if not original_user_message or not original_user_message.content.strip():
        raise ValueError("Mensagem do usuário não encontrada ou está vazia")
    
    user_prompt = original_user_message.content.strip()

    configurable = config.get("configurable", {})
    history_limit = configurable.get("history_limit", 4)
    embedding_limit = configurable.get("embedding_limit", 2)
    system_prompt = configurable.get(
        "system_prompt",
        "Você é a EAI, assistente virtual da Prefeitura do Rio de Janeiro.",
    )

    try:
        with get_db_session() as session:
            repo = MemoryRepository(session)
            query_embedding = embedding_service.get_embedding(user_prompt)
            memories = repo.get_unified_memory(
                user_id, query_embedding, history_limit, embedding_limit
            )
    except Exception as e:
        print(f"Erro ao carregar memórias: {e}")
        memories = []

    # Processa as memórias
    history_mems = sorted(
        [m for m in memories if m["type"] == "history"], key=lambda x: x["created_at"]
    )
    embedding_mems = [m for m in memories if m["type"] == "embedding"]

    # Constrói o contexto
    context_parts = []
    
    if embedding_mems:
        embedding_context = "\n".join([
            f"- {mem.get('content_type', 'informação').capitalize()}: {mem.get('content', '')}"
            for mem in embedding_mems if mem.get('content')
        ])
        if embedding_context:
            context_parts.append(f"## Informações contextuais\n{embedding_context}")
    
    if history_mems:
        history_context = "\n".join([
            f"- {mem.get('content_type', 'mensagem').capitalize()}: {mem.get('content', '')}"
            for mem in history_mems if mem.get('content')
        ])
        if history_context:
            context_parts.append(f"## Histórico recente\n{history_context}")
    
    # Constrói o prompt final
    if context_parts:
        context_message_content = "\n\n".join(context_parts)
        full_user_prompt = (
            f"{context_message_content}\n\n"
            f"---\n\n"
            f"Pergunta do usuário: {user_prompt}"
        )
    else:
        full_user_prompt = user_prompt

    # Constrói as mensagens
    messages = []
    if system_prompt and system_prompt.strip():
        messages.append(SystemMessage(content=system_prompt.strip()))
    messages.append(HumanMessage(content=full_user_prompt.strip()))

    state["messages"] = messages
    return state


async def call_llm_node(state: ConversationState, config: dict):
    configurable = config.get("configurable", {})
    chat_model = configurable.get("chat_model")
    
    if not chat_model:
        raise ValueError("Instância do ChatModel não encontrada na configuração.")

    # Filtra apenas mensagens válidas
    valid_messages = []
    for msg in state["messages"]:
        if isinstance(msg, (SystemMessage, HumanMessage, AIMessage)) and msg.content and msg.content.strip():
            valid_messages.append(msg)

    if not valid_messages:
        raise ValueError("Nenhuma mensagem válida encontrada")

    print(f"Enviando {len(valid_messages)} mensagens para o modelo:")
    for i, msg in enumerate(valid_messages):
        print(f"  {i+1}. {type(msg).__name__}: {msg.content[:100]}...")

    try:
        response = chat_model.invoke(valid_messages)
        state["messages"].append(response)
        
        # Verifica se o modelo retornou tool_calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"Modelo solicitou {len(response.tool_calls)} ferramenta(s)")
            
            # Executa cada ferramenta
            tool_results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name", "")
                tool_args = tool_call.get("args", {})
                print(f"Executando ferramenta: {tool_name} com args: {tool_args}")
                
                result = await execute_tool_call(tool_name, tool_args)
                tool_results.append(f"Resultado da ferramenta '{tool_name}':\n{result}")
            
            # Adiciona os resultados como nova mensagem
            if tool_results:
                combined_results = "\n\n".join(tool_results)
                tool_message = HumanMessage(content=f"Resultados das ferramentas executadas:\n\n{combined_results}")
                state["messages"].append(tool_message)
                
                # Chama o modelo novamente para processar os resultados
                print("Chamando modelo novamente para processar resultados das ferramentas...")
                final_response = chat_model.invoke(state["messages"])
                state["messages"].append(final_response)
        
        return state
    except Exception as e:
        print(f"Erro ao chamar o modelo: {e}")
        import traceback
        traceback.print_exc()
        raise


def save_memory_node(state: ConversationState, config: dict):
    user_id = state["user_id"]

    try:
        # Encontra mensagens do usuário e da IA
        user_message_content = ""
        ai_message_content = ""
        
        # Pega a última mensagem da IA (resposta final)
        for msg in reversed(state["messages"]):
            if isinstance(msg, AIMessage):
                ai_message_content = msg.content
                break
        
        # Pega a pergunta original do usuário
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage) and not msg.content.startswith("Resultados das ferramentas"):
                content = msg.content
                if 'Pergunta do usuário:' in content:
                    user_message_content = content.split('Pergunta do usuário:')[-1].strip()
                else:
                    user_message_content = content
                break

        # Salva na memória
        if user_message_content.strip() and ai_message_content.strip():
            try:
                user_embedding = embedding_service.get_embedding(user_message_content)
                ai_embedding = embedding_service.get_embedding(ai_message_content)

                with get_db_session() as session:
                    repo = MemoryRepository(session)
                    repo.add_message(user_id, user_message_content, "user", user_embedding)
                    repo.add_message(user_id, ai_message_content, "eai", ai_embedding)
                    
                print(f"Salvou memórias - User: {user_message_content[:50]}... | AI: {ai_message_content[:50]}...")
            except Exception as e:
                print(f"Erro ao salvar memórias: {e}")

        # Prepara resposta final (filtra mensagens internas)
        response_messages = []
        for msg in state["messages"]:
            if not (isinstance(msg, HumanMessage) and msg.content.startswith("Resultados das ferramentas")):
                response_messages.append(msg)
        
        state["final_response"] = messages_to_dict(response_messages)
    
    except Exception as e:
        print(f"Erro no save_memory_node: {e}")
        import traceback
        traceback.print_exc()
        state["final_response"] = {"error": str(e)}

    return state


# --- 5. Construção do Grafo ---
def create_simple_graph():
    """Cria um grafo simples e linear."""
    workflow = StateGraph(ConversationState)

    # Adiciona os nós
    workflow.add_node("load_and_prepare_context", load_and_prepare_context_node)
    workflow.add_node("call_llm", call_llm_node)
    workflow.add_node("save_memory", save_memory_node)

    # Define o fluxo linear
    workflow.set_entry_point("load_and_prepare_context")
    workflow.add_edge("load_and_prepare_context", "call_llm")
    workflow.add_edge("call_llm", "save_memory")
    workflow.add_edge("save_memory", END)

    # Compila o grafo
    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)


# --- 6. Função de Invocação ---
async def run_chatbot(user_id: str, message: str, agent_config: Dict[str, Any]):
    """
    Executa o chatbot de forma simplificada para Gemini.
    """
    global GLOBAL_TOOLS
    
    if not user_id or not message or not message.strip():
        raise ValueError("user_id e message são obrigatórios e não podem estar vazios")
    
    try:
        # Carrega as ferramentas globalmente (evita serialização)
        GLOBAL_TOOLS = await get_mcp_tools()
        print(f"Carregadas {len(GLOBAL_TOOLS)} ferramentas MCP")
    except Exception as e:
        print(f"Erro ao carregar ferramentas MCP: {e}")
        GLOBAL_TOOLS = []

    try:
        # Cria a instância do modelo de chat com as ferramentas
        chat_model_instance = ChatModelFactory.create(
            provider=agent_config.get("provider", "google"),
            model_name=agent_config.get("model_name"),
            temperature=agent_config.get("temperature"),
            tools=GLOBAL_TOOLS if GLOBAL_TOOLS else None,
        )
    except Exception as e:
        print(f"Erro ao criar modelo de chat: {e}")
        raise ValueError(f"Falha ao inicializar o modelo de chat: {e}")

    # Cria o grafo simples
    app = create_simple_graph()

    config = {
        "configurable": {
            "thread_id": f"user_{user_id}",
            "chat_model": chat_model_instance,
            "system_prompt": agent_config.get("system_prompt", "Você é um assistente útil."),
            "history_limit": agent_config.get("history_limit", 4),
            "embedding_limit": agent_config.get("embedding_limit", 2),
        }
    }

    initial_state = {
        "user_id": user_id,
        "messages": [HumanMessage(content=message.strip())],
        "final_response": {},
    }

    try:
        # Invoca o grafo
        final_state = await app.ainvoke(initial_state, config=config)
        return final_state.get("final_response", {})
    except Exception as e:
        print(f"Erro durante a execução do chatbot: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Erro interno: {str(e)}"}

----


### Planning: Conversational Agent with Short/Long-Term Memory using LangGraph

#### **Objective**
Build a conversational agent using LangGraph that:
1. Uses Google Generative AI models (`ChatGoogleGenerativeAI`, `GoogleGenerativeAIEmbeddings`)
2. Implements dual memory systems (short-term and long-term) via GCP Cloud SQL (PostgreSQL + PgVector)
3. Integrates with an MCP HTTP server for external tools
4. Supports session-based conversations with `user_id` and `session_id`
5. Allows explicit long-term memory queries via a dedicated tool

---

### **Architecture Overview**
```mermaid
graph TD
    A[User Input] --> B[Memory Retrieval]
    B --> C{Agent Decision}
    C -->|Use Tool| D[MCP Tools]
    C -->|Query Memory| E[Long-Term Memory Tool]
    C --> F[Generate Response]
    D --> F
    E --> F
    F --> G[Update Memory]
    G --> H[Response]
```

---

### **Key Components**

#### 1. **Memory Systems**
- **Short-Term Memory**:
  - Stores recent messages chronologically
  - PostgreSQL table: `conversation_history`
  - Retrieved via `timestamp` (last `N` messages)
  - Controlled by `short_term_limit` parameter
  - **New Session Behavior**: Cleared when session restarts

- **Long-Term Memory**:
  - Stores message embeddings in PgVector
  - Retrieved via semantic similarity to current query
  - PostgreSQL table: `long_term_memory`
  - Controlled by `long_term_limit` parameter
  - Persists across sessions via `user_id`

#### 2. **Database Schema (Cloud SQL PostgreSQL)**
```sql
-- Conversation History (Short-Term)
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    message TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Long-Term Memory (Embeddings)
CREATE TABLE long_term_memory (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    message TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL,  -- 768-dim for GoogleEmbeddings
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ON long_term_memory USING ivfflat (embedding vector_cosine_ops);
```

#### 3. **Memory Workflow**
- **On User Input**:
  1. Retrieve last `short_term_limit` messages from `conversation_history`
  2. Embed query → find top `long_term_limit` similar entries in `long_term_memory`
  3. Combine memories into context
- **After Agent Response**:
  1. Store user input + agent response in both tables
  2. Generate embeddings for long-term storage

#### 4. **Tools**
- **MCP Tools**:
  ```python
  from langchain_mcp_adapters.tools import load_mcp_tools
  tools = await load_mcp_tools()  # Async initialization
  ```
- **Long-Term Memory Query Tool**:
  ```python
  from langchain_core.tools import tool
  @tool
  def search_long_term_memory(query: str) -> str:
      """Search long-term memory using natural language queries"""
      # Uses same retrieval as contextual memory
  ```

#### 5. **Agent State**
```python
from typing import TypedDict, List, Annotated
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    user_id: str
    session_id: str
    input: str
    chat_history: List[BaseMessage]
    context: str  # Combined short/long-term memories
    agent_outcome: AgentAction | AgentFinish | None
    intermediate_steps: Annotated[List[tuple[AgentAction, str]], operator.add]
```

---

### **Implementation Plan**

#### Step 1: Setup Dependencies
```python
# requirements.txt
langgraph
langchain-google-genai
langchain
pgvector
langchain_mcp_adapters
google-cloud-sql-python-connector
```

#### Step 2: Memory Manager Class
```python
from langchain_community.vectorstores.pgvector import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class MemoryManager:
    def __init__(self, conn_string: str):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.conn_string = conn_string
        self.store = PGVector(
            connection_string=conn_string,
            embedding_function=self.embeddings,
            collection_name="long_term_memory"
        )
    
    async def get_short_term_memory(
        self, 
        user_id: str, 
        session_id: str, 
        limit: int
    ) -> List[str]:
        # Query PostgreSQL for last N messages
        ...
    
    async def get_contextual_memory(
        self,
        user_id: str,
        query: str,
        limit: int
    ) -> List[str]:
        # Semantic search via PgVector
        docs = self.store.similarity_search(
            query=query,
            k=limit,
            filter={"user_id": user_id}
        )
        return [doc.page_content for doc in docs]
    
    async def save_memory(
        self,
        user_id: str,
        session_id: str,
        message: str,
        is_user: bool
    ):
        # Save to both tables
        ...
```

#### Step 3: Graph Construction
```python
from langgraph.graph import StateGraph, END

def build_agent(memory_manager: MemoryManager):
    # Define node logic
    async def retrieve_memory(state: AgentState):
        short_term = await memory_manager.get_short_term_memory(
            state['user_id'], state['session_id'], SHORT_TERM_LIMIT
        )
        long_term = await memory_manager.get_contextual_memory(
            state['user_id'], state['input'], LONG_TERM_LIMIT
        )
        return {"context": f"Short-term: {short_term}\nLong-term: {long_term}"}
    
    async def call_tools(state: AgentState):
        # Tool execution logic
        ...
    
    async def generate_response(state: AgentState):
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        # Use context+input to generate response
        ...
    
    # Build graph
    workflow = StateGraph(AgentState)
    workflow.add_node("retrieve_memory", retrieve_memory)
    workflow.add_node("call_tools", call_tools)
    workflow.add_node("generate", generate_response)
    ...
    return workflow.compile()
```

#### Step 4: Session Management
- **New Session Flow**:
  1. Generate new `session_id`
  2. Clear short-term memory buffer
  3. Retrieve relevant long-term memories using last interaction
  4. Initialize with: "New session started. Previous context: [...]"

#### Step 5: Main Entrypoint
```python
async def handle_message(user_id: str, session_id: str, input: str):
    # Initialize agent
    memory = MemoryManager(CONN_STRING)
    tools = await get_mcp_tools() + [search_long_term_memory]
    agent = build_agent(memory, tools)
    
    # Execute graph
    result = await agent.ainvoke({
        "user_id": user_id,
        "session_id": session_id,
        "input": input,
        "chat_history": []
    })
    
    # Save to DB
    await memory.save_memory(user_id, session_id, input, True)
    await memory.save_memory(user_id, session_id, result['output'], False)
    
    return result['output']
```

---

### **Key Design Decisions**

1. **Memory Separation**:
   - Short-term: Fast chronological lookup (PostgreSQL)
   - Long-term: Semantic search (PgVector)
   - Parameters: `SHORT_TERM_LIMIT=5`, `LONG_TERM_LIMIT=3`

2. **New Session Handling**:
   - Short-term memory reset
   - Long-term memory persists via `user_id`
   - Automatic retrieval of relevant history from long-term memory

3. **Explicit Memory Tool**:
   - Used when agent needs deeper historical context
   - Same retrieval mechanism as contextual memory

4. **Embedding Management**:
   - GoogleGenerativeAIEmbeddings for all vector operations
   - Async storage to avoid blocking

5. **Cloud SQL Optimization**:
   - IVFFlat indexes for fast similarity search
   - Connection pooling for high concurrency

---

### **Testing Plan**

1. **Memory Tests**:
   - Verify short-term memory reset on new session
   - Test long-term recall across sessions
   - Validate embedding storage/retrieval

2. **Tool Integration**:
   - Test MCP tool invocation
   - Verify memory query tool functionality

3. **Load Testing**:
   - Simulate 100+ concurrent sessions
   - Monitor Cloud SQL performance

4. **Edge Cases**:
   - Empty memory scenarios
   - Tool execution failures
   - Session collision edge cases

---

### **Deployment**

1. **GCP Infrastructure**:
   - Cloud SQL PostgreSQL + PgVector extension
   - Cloud Run for agent service
   - Memory-optimized machine type

2. **Environment Variables**:
   ```env
   PG_CONN_STRING=postgresql://user:pass@/db?host=/cloudsql/project:region:instance
   MCP_SERVER_URL=https://...
   GEMINI_API_KEY=...
   ```

---

This plan provides a comprehensive roadmap for building a production-ready conversational agent with dual memory systems using LangGraph and GCP technologies. Implementation should follow the outlined component structure and memory handling principles.

-----


Here is a complete and detailed guide to creating a chatbot using LangGraph that leverages both short-term and long-term memory with a GCP Cloud SQL PostgreSQL backend, `ChatGoogleGenerativeAI`, `GoogleGenerativeAIEmbeddings`, and MCP tool access.

### 1. Short and Long-Term Memory Functionality in LangGraph

LangGraph provides a flexible framework for managing memory in conversational agents. It distinguishes between two primary types of memory:

*   **Short-Term Memory:** This is the conversational history within a single session or thread. It's managed as part of the agent's state and is persisted using a "checkpointer." This allows the agent to maintain context within an ongoing conversation. In your case, with a `thread_id` acting as a `session_id`, a new session will mean a new `thread_id`, and thus a new, empty short-term memory. The previous conversation's short-term memory is not automatically carried over.

*   **Long-Term Memory:** This allows the agent to retain information across multiple sessions. It's ideal for storing user preferences, historical data, and other information that should persist over time. This memory is stored in a persistent database, like PostgreSQL with PgVector, and can be queried to provide context to the agent. When a new session starts, the long-term memory can be accessed to retrieve relevant information from past conversations.

### 2. Setting Up the Environment

Before building the chatbot, you need to set up the necessary infrastructure and install the required Python packages.

**A. Google Cloud SQL for PostgreSQL:**

1.  **Create a PostgreSQL instance in Google Cloud SQL.**
2.  **Create a database** within your instance.
3.  **Enable the `pgvector` extension.** You can do this by connecting to your database and running the following SQL command:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```
4.  **Obtain your database connection string.** It will be in the format: `postgresql+psycopg2://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>`.

**B. Install Python packages:**

```bash
pip install "langchain[google_genai]" langchain-core langchain-community langchain-postgres langgraph langchain_mcp_adapters psycopg2-binary pgvector
```

### 3. Building the Conversational Agent

Here’s a breakdown of the components and code to create your chatbot:

**A. Initial Setup and Configuration:**

First, you'll need to import the necessary libraries and configure your environment variables for your Google API key and database connection.

```python
import os
import uuid
from typing import TypedDict, Annotated, List

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import tool

# --- Environment Variables ---
os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"
DB_CONNECTION_STRING = "postgresql+psycopg2://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>"
MCP_SERVER_URL = "YOUR_MCP_SERVER_URL"
MCP_API_TOKEN = "YOUR_MCP_API_TOKEN"

# --- LLM and Embeddings ---
llm = ChatGoogleGenerativeAI(model="gemini-pro")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-002")
```

**B. Long-Term Memory as a Tool:**

To allow the agent to query its long-term memory, you can create a custom tool. This tool will connect to your PgVector store and retrieve relevant documents based on a natural language query.

```python
# --- Long-Term Memory Store ---
long_term_memory_store = PGVector(
    connection_string=DB_CONNECTION_STRING,
    embedding_function=embeddings,
    collection_name="long_term_memory"
)

@tool
def search_long_term_memory(query: str, user_id: str, session_id: str) -> str:
    """
    Searches the long-term memory for information relevant to the query.
    """
    results = long_term_memory_store.similarity_search(query, k=long_term_limit, filter={"user_id": user_id})
    return "\n".join([doc.page_content for doc in results])
```

**C. Short-Term and Long-Term Memory Management:**

You'll define the state for your LangGraph agent, which will include the conversational messages. The checkpointer will handle the persistence of this state, representing the short-term memory.

```python
# --- Agent State ---
class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]
    user_id: str
    session_id: str

# --- Memory Limits ---
short_term_limit = 10
long_term_limit = 5
```

When a user sends a message, you will first retrieve relevant long-term memories and then combine them with the recent short-term history to provide context to the LLM.

**D. Accessing MCP Tools:**

The `langchain_mcp_adapters` library makes it easy to integrate tools from an MCP server.

```python
async def get_mcp_tools():
    """
    Initializes the MCP client and fetches the available tools.
    """
    client = MultiServerMCPClient(
        {
            "rio_mcp": {
                "transport": "streamable_http",
                "url": MCP_SERVER_URL,
                "headers": {
                    "Authorization": f"Bearer {MCP_API_TOKEN}",
                },
            },
        }
    )
    tools = await client.get_tools()
    return tools

mcp_tools = asyncio.run(get_mcp_tools())
all_tools = mcp_tools + [search_long_term_memory]
```

**E. Creating the LangGraph:**

Now, you can define the nodes and edges of your graph. The main node will execute the agent with the combined tools.

```python
# --- LangGraph Definition ---
def agent_node(state: AgentState):
    # 1. Retrieve long-term memory
    last_user_message = state["messages"][-1].content
    long_term_context = search_long_term_memory.invoke(
        {"query": last_user_message, "user_id": state["user_id"], "session_id": state["session_id"]}
    )

    # 2. Construct prompt with short-term and long-term memory
    prompt = f"""You are a helpful assistant.
    Here is relevant information from past conversations (long-term memory):
    {long_term_context}

    Here is the recent conversation history (short-term memory):
    """
    
    # Apply short-term memory limit
    short_term_messages = state["messages"][-short_term_limit:]

    # 3. Invoke the agent
    agent_executor = create_react_agent(llm, all_tools, messages_modifier=prompt)
    response = agent_executor.invoke({"messages": short_term_messages})
    
    # 4. Save the user message and AI response to long-term memory
    long_term_memory_store.add_documents([
        HumanMessage(page_content=last_user_message, metadata={"user_id": state["user_id"], "session_id": state["session_id"]}),
        response["messages"][-1]
    ])

    return {"messages": [response["messages"][-1]]}

# --- Build the Graph ---
graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", agent_node)
graph_builder.set_entry_point("agent")
graph_builder.add_edge("agent", END)

# --- Add Checkpointer for Short-Term Memory ---
checkpointer = PostgresSaver.from_conn_string(DB_CONNECTION_STRING)
graph = graph_builder.compile(checkpointer=checkpointer)
```

### 4. Running the Chatbot

To interact with the chatbot, you'll invoke the graph with a `user_id` and a `thread_id` (as the `session_id`).

```python
def run_chatbot(user_id: str, session_id: str, message: str):
    config = {"configurable": {"thread_id": session_id}}
    response = graph.invoke(
        {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "session_id": session_id
        },
        config=config
    )
    return response["messages"][-1].content

# Example usage:
user_id = "user_123"
session_id = str(uuid.uuid4())

# First interaction
print(run_chatbot(user_id, session_id, "Hi, my name is Bob."))

# Second interaction in the same session
print(run_chatbot(user_id, session_id, "What is my name?"))

# Start a new session
new_session_id = str(uuid.uuid4())
print(run_chatbot(user_id, new_session_id, "Do you remember my name?"))
```

### What happens when a new session is initiated?

When a user starts a new session, a new `thread_id` is generated. This means:

*   **Short-Term Memory is Lost:** The new session will have an empty conversational history. The previous messages from the old session will not be in the immediate context of the new session.
*   **Long-Term Memory is Used:** The `search_long_term_memory` tool will be invoked with the user's query. Since the `user_id` is the same, the tool can retrieve relevant information from past conversations, including the user's name, and provide it as context to the agent. This allows the chatbot to have a sense of continuity across sessions, even though the direct conversational history is reset.

------



Of course. Here is the comprehensive `planing.md` file based on your specifications.

# Planing: LangGraph Conversational Agent with Advanced Memory

This document outlines the architecture and implementation plan for a conversational agent built with LangGraph. The agent will leverage Google Generative AI, maintain short-term and long-term memory in a PostgreSQL database via PgVector, and integrate with external tools.

## 1. Database Schema (PostgreSQL with PgVector)

The core of the memory system will be a single table in a GCP Cloud SQL for PostgreSQL database. The `pgvector` extension must be enabled on the database.

**Table: `conversation_history`**

This table will store every message, tagged with user and session identifiers. It will also store the vector embedding for each message to enable semantic search for LTM.

```sql
-- Enable the PgVector extension (must be done by a superuser)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the table to store conversation history and embeddings
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    message_content TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL, -- 'human' or 'ai'
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    embedding VECTOR(768) -- Dimension for GoogleGenerativeAIEmbeddings model 'models/embedding-001'
);

-- Create an index for the user_id for fast LTM filtering
CREATE INDEX idx_user_id ON conversation_history (user_id);

-- Create a HNSW index for efficient vector similarity search
CREATE INDEX idx_embedding_hnsw ON conversation_history USING hnsw (embedding vector_l2_ops);
```

---

## 2. Initialization and Configuration

This section details the setup of core LangChain components.

1.  **Google AI Components:**
    *   **Embeddings:** Initialize `GoogleGenerativeAIEmbeddings` to convert text messages into vector representations.
        ```python
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        ```
    *   **Chat Model:** Initialize `ChatGoogleGenerativeAI` as the core LLM for the agent.
        ```python
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        ```

2.  **PgVector Store:**
    *   Configure the `PGVector` store to connect to the GCP Cloud SQL database and use the `conversation_history` table. This object will be the primary interface for LTM retrieval and storage.
    ```python
    from langchain_community.vectorstores.pgvector import PGVector

    # Assumes standard PostgreSQL environment variables are set (PGHOST, PGUSER, PGPASSWORD, PGDATABASE)
    CONNECTION_STRING = "postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE"
    COLLECTION_NAME = "conversation_history"

    vector_store = PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings,
    )
    ```

---

## 3. LangGraph State & Nodes

The agent's logic will be orchestrated using a LangGraph state machine.

### 3.1. Graph State Schema

The state is a dictionary that holds all information passed between the nodes of the graph.

```python
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Input identifiers
    user_id: str
    session_id: str

    # The conversation history, managed by LangGraph
    messages: Annotated[List[BaseMessage], add_messages]

    # Context retrieved from memory for the current turn
    retrieved_stm: str
    retrieved_ltm: str

    # The outcome of the agent's decision (tool call or final answer)
    agent_outcome: any

    # The final, user-facing response
    final_answer: str
```

### 3.2. Core Nodes

*   **`retrieve_memory` (Entry Point):**
    *   Receives the initial request with `user_id`, `session_id`, and the new human message.
    *   Performs both STM and LTM retrieval as described in Section 4.
    *   Populates `retrieved_stm` and `retrieved_ltm` in the state.
    *   This node runs once per user interaction at the beginning of the graph.

*   **`agent` (Decision Engine):**
    *   Receives the conversation `messages` and the retrieved `retrieved_stm` and `retrieved_ltm` context.
    *   Its prompt will instruct it to use the provided context and its toolset to formulate a response or action.
    *   The output is an `AgentAction` (tool call) or `AgentFinish` (final answer).
    *   This node is the central reasoning loop.

*   **`execute_tools` (Tool Executor):**
    *   If the `agent` node outputs a tool call, this node executes it.
    *   It calls the appropriate tool (MCP or LTM search) with the provided arguments.
    *   The output of the tool is then passed back into the graph, typically looping back to the `agent` node for the next step.

*   **`store_memory` (Exit Point):**
    *   Before finishing, this node takes the latest human message and the final AI response.
    *   It generates embeddings for both messages.
    *   It saves both messages and their embeddings to the `conversation_history` table in PostgreSQL.

---

## 4. Memory Management Logic

Memory retrieval is the first critical step in processing any user query.

### 4.1. Short-Term Memory (STM)

*   **Type:** Chronological, session-specific history.
*   **Retrieval:** A direct SQL query on the `conversation_history` table.
*   **Logic:**
    1.  Get the `session_id` from the current state.
    2.  Query the table: `SELECT message_content, message_type FROM conversation_history WHERE session_id = :sid ORDER BY timestamp DESC LIMIT :limit`.
    3.  The `:limit` parameter will be `short_term_limit`.
    4.  Format the results chronologically as a string to be placed in `state['retrieved_stm']`.

### 4.2. Long-Term Memory (LTM)

*   **Type:** Semantic, user-specific history.
*   **Retrieval:** Vector similarity search using the `PgVector` store.
*   **Logic:**
    1.  Get the `user_id` and the latest user message from the state.
    2.  Generate an embedding for the user's message.
    3.  Use the `vector_store.similarity_search_with_relevance_scores` method.
    4.  The search will be filtered by `user_id` and limited by `long_term_limit`.
    5.  Format the results as a string to be placed in `state['retrieved_ltm']`.

### 4.3. Combined Memory Retrieval Flow

The `retrieve_memory` node will execute both STM and LTM retrieval in parallel. The combined context will be formatted and passed to the agent's prompt, for example:

```
Here is the context for the current conversation:

=== Recent Conversation History (Short-Term Memory) ===
Human: What was the last thing we talked about?
AI: We were discussing the new features for the platform.

=== Relevant Past Conversations (Long-Term Memory) ===
- (From 2 weeks ago) Human: Tell me more about the data analytics feature.
- (From 1 month ago) Human: How do I set up a new project?

Current Question: [User's latest message here]
```

---

## 5. Tool Integration

The agent will have access to a set of tools to enhance its capabilities. These tools will be passed to the `agent` node.

### 5.1. MCP Server Tools

External tools from the MCP server will be loaded asynchronously and provided to the agent.

*   **Initialization Snippet:** This function will be called during application startup to fetch the available tools.

    ```python
    from langchain_mcp_adapters.tools import load_mcp_tools
    from src.config import env
    from langchain_mcp_adapters.client import MultiServerMCPClient
    import asyncio

    async def get_mcp_tools():
        """
        Initializes the MCP client and fetches available tools asynchronously.
        """
        client = MultiServerMCPClient(
            {
                "rio_mcp": {
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
    ```
*   **Integration:** The list of tools returned by `get_mcp_tools` will be appended to the list of tools available to the agent.

### 5.2. Long-Term Memory Retrieval Tool

This is an explicit tool the agent can *choose* to use for a deeper, more specific search of its long-term memory.

*   **Definition:** The tool will be created using LangChain's `@tool` decorator.

    ```python
    from langchain_core.tools import tool

    @tool
    def search_long_term_memory(query: str, user_id: str) -> str:
        """
        Searches your long-term memory for information relevant to the user's query.
        Use this when you need to recall specific details from past conversations with this user that are not in the provided context.
        """
        # The vector_store is the initialized PGVector instance
        results = vector_store.similarity_search(
            query=query,
            k=5, # A fixed, deeper search limit
            filter={"user_id": user_id}
        )
        return "\n".join([doc.page_content for doc in results])
    ```
*   **Usage:** This tool allows the agent to self-correct if the initial automatic LTM retrieval was insufficient. For example, if the user asks "what did I say about project X last year?", the agent can use this tool to perform a targeted search for "project X".

---

## 6. Session Handling

Session management is key to distinguishing between STM and LTM.

*   **`user_id`:** This ID is persistent and links all of a user's conversations together. It is the primary key for LTM.
*   **`session_id`:** This ID (`tred_id`) represents a single, continuous conversation.
*   **New Session Logic:**
    1.  When a request arrives with a `session_id` that has not been seen before, the system treats it as a new session.
    2.  The STM retrieval query (`...WHERE session_id = ?...`) will return no results, correctly indicating that there is no recent history for *this specific session*.
    3.  The LTM retrieval, which is based only on `user_id`, will proceed as usual, providing the agent with relevant historical context from all previous sessions.
    4.  This flow ensures that STM is effectively "cleared" for each new session while LTM remains persistent, fulfilling the core memory architecture requirement.