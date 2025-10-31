# 🧮 Math Routing Agent

An AI-powered mathematics tutoring system that uses Agentic RAG architecture with guardrails, knowledge base, web search via MCP, and human-in-the-loop feedback.

## 🎯 Features

- **Input & Output Guardrails**: Ensures only math-related queries are processed
- **Knowledge Base**: Vector database with 20+ pre-indexed math problems
- **MCP Integration**: Model Context Protocol for standardized web search
- **Human-in-the-Loop**: Feedback mechanism for continuous improvement
- **Multi-source Routing**: KB → MCP Search → LLM with intelligent fallbacks
- **Real-time API**: FastAPI backend with React frontend

## 🏗️ Architecture
```
User Input
    ↓
Input Guardrails
    ↓
Knowledge Base Search (ChromaDB)
    ↓ (if not found)
MCP Web Search (Tavily)
    ↓
LLM Processing (Groq/Gemini)
    ↓
Output Guardrails
    ↓
Response to User
    ↓
Human Feedback Loop
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI
- LangChain
- ChromaDB (Vector Database)
- Groq API (LLM)
- Tavily API (Web Search)
- Model Context Protocol (MCP)

**Frontend:**
- React
- Axios
- Lucide Icons

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys:
  - Groq API Key (free tier available)
  - Tavily API Key (free tier available)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/math-agent-project.git
cd math-agent-project
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# Windows:
env\Scripts\activate
# Mac/Linux:
source env/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**Get API Keys:**
- Groq: https://console.groq.com/keys
- Tavily: https://app.tavily.com/

### 4. Frontend Setup
```bash
cd frontend/math-agent-ui
npm install
```

## 🎮 Running the Application

### Start Backend Server
```bash
cd backend
python main.py
```

Backend runs on: `http://localhost:8000`

### Start Frontend
```bash
cd frontend/math-agent-ui
npm start
```

Frontend runs on: `http://localhost:3000`

## 📊 API Endpoints

- `POST /api/solve` - Solve math problems
- `POST /api/feedback` - Submit feedback
- `GET /api/feedback/stats` - Get feedback statistics
- `GET /api/health` - Health check

## 🧪 Testing

### Test Backend
```bash
cd backend
python test_api.py
```

### Test MCP
```bash
cd backend
python test_mcp.py
```

## 📁 Project Structure
```
math-agent-project/
├── backend/
│   ├── agents/
│   │   ├── math_agent.py          # Main routing agent
│   │   └── feedback_agent.py
│   ├── guardrails/
│   │   ├── input_guard.py         # Input validation
│   │   └── output_guard.py        # Output validation
│   ├── knowledge_base/
│   │   ├── kb_manager.py          # Vector DB manager
│   │   └── math_dataset.json     # Math problems dataset
│   ├── mcp_tools/
│   │   ├── mcp_protocol.py        # MCP base classes
│   │   ├── math_search_server.py  # MCP server
│   │   └── math_search_client.py  # MCP client
│   ├── main.py                    # FastAPI app
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   └── App.css
│   └── package.json
├── .gitignore
└── README.md
```

## 🎯 Sample Questions

**Knowledge Base Questions:**
- "What is the derivative of x^2?"
- "Solve x^2 - 5x + 6 = 0"
- "What is the Pythagorean theorem?"
- "Find the area of a circle with radius 5"

**Web Search Questions:**
- "Explain Euler's formula"
- "What is Taylor series expansion?"
- "How to solve differential equations?"

## 🔒 Guardrails

**Input Guardrails:**
- Validates math-related queries only
- Blocks non-educational content
- Length validation (5-500 characters)

**Output Guardrails:**
- Ensures step-by-step format
- Validates educational content
- Checks for completeness

## 📈 Human-in-the-Loop

Users can rate solutions (1-5 stars) to help improve the system:
- Ratings < 3 trigger improvement flags
- Feedback stored for analysis
- Statistics available via API

## 🎓 Assignment Requirements Met

✅ Input & Output Guardrails (Privacy & Quality)  
✅ Knowledge Base with Vector DB (ChromaDB)  
✅ MCP Implementation (Model Context Protocol)  
✅ Web Search Integration (Tavily via MCP)  
✅ Human-in-the-Loop Feedback Mechanism  
✅ FastAPI Backend + React Frontend  
✅ Intelligent Routing Pipeline  

## 📝 License

MIT License

## 👨‍💻 Author

Your Name - [GitHub](https://github.com/farhan2806)

## 🙏 Acknowledgments

- Anthropic for MCP specification
- LangChain for agent framework
- Groq for fast LLM inference

- Tavily for web search API
