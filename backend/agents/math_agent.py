from groq import Groq
from knowledge_base.kb_manager import KnowledgeBaseManager
from mcp.math_client_search import MathSearchMCPClient
from guardrails.input_guard import InputGuardrail
from guardrails.output_guard import OutputGuardrail
import os
from dotenv import load_dotenv

load_dotenv()

class MathRoutingAgent:
    def __init__(self):
        # Configure Groq API
        groq_key = os.getenv("GROQ_API_KEY")
        
        if groq_key:
            try:
                self.llm = Groq(api_key=groq_key)
                self.use_llm = True
                print("✅ Groq API configured successfully")
            except Exception as e:
                print(f"⚠️ Groq API error: {e}")
                self.use_llm = False
                self.llm = None
        else:
            print("⚠️ Groq API not configured - using fallback mode")
            self.use_llm = False
            self.llm = None
        
        self.kb = KnowledgeBaseManager()
        
        # Initialize MCP Client
        try:
            self.mcp_search = MathSearchMCPClient()
            print("✅ MCP Search Client initialized")
        except Exception as e:
            print(f"⚠️ MCP Client initialization error: {e}")
            self.mcp_search = None
        
        self.input_guard = InputGuardrail()
        self.output_guard = OutputGuardrail()
        
        self.system_prompt = """You are an expert mathematics professor. 
Generate a clear, step-by-step solution that a student can easily understand.

Format your response as:
**Understanding the Problem:**
[Brief explanation]

**Step-by-Step Solution:**
Step 1: [First step with explanation]
Step 2: [Second step with explanation]
...

**Final Answer:**
[Clear final answer]

**Key Concepts:**
[List important concepts used]
"""
    
    def route_query(self, query: str) -> dict:
        """Main routing logic with MCP integration"""
        
        # Step 1: Input Guardrail
        is_valid, message = self.input_guard.validate(query)
        if not is_valid:
            return {
                'success': False,
                'source': 'guardrail',
                'message': message
            }
        
        # Step 2: Check Knowledge Base
        kb_results = self.kb.search(query, top_k=1)
        
        if kb_results and kb_results[0]['score'] > 0.70:
            result = kb_results[0]
            solution = self._format_kb_solution(result)
            
            return {
                'success': True,
                'source': 'knowledge_base',
                'solution': solution,
                'confidence': round(result['score'], 2),
                'routing_path': 'Input → Guardrails → Knowledge Base → Response'
            }
        
        # Step 3: Web Search via MCP
        if self.mcp_search:
            try:
                print(f"🔍 Routing through MCP for query: {query}")
                search_results = self.mcp_search.search_math_solution(query, "basic")
                
                if search_results.get('found') and search_results.get('results'):
                    context = self._extract_context(search_results['results'])
                    
                    if self.use_llm:
                        solution = self._generate_solution_with_llm(query, context)
                    else:
                        solution = self._format_web_search_solution(query, search_results['results'])
                    
                    return {
                        'success': True,
                        'source': 'mcp_web_search',
                        'solution': solution,
                        'references': search_results['results'][:2],
                        'routing_path': 'Input → Guardrails → KB (miss) → MCP Search → LLM → Response'
                    }
            except Exception as e:
                print(f"⚠️ MCP search error: {e}")
        
        # Step 4: Fallback - Use LLM directly
        if self.use_llm:
            solution = self._generate_solution_with_llm(
                query, 
                "Use your mathematical knowledge to solve this problem step by step."
            )
            return {
                'success': True,
                'source': 'llm_direct',
                'solution': solution,
                'routing_path': 'Input → Guardrails → KB (miss) → MCP (unavailable) → LLM Direct → Response'
            }
        else:
            solution = self._generate_fallback_solution(query)
            return {
                'success': True,
                'source': 'fallback',
                'solution': solution,
                'routing_path': 'Input → Guardrails → KB (miss) → MCP (unavailable) → LLM (not configured) → Fallback Resources'
            }
    
    # Keep all other methods the same...
    def _format_kb_solution(self, result: dict) -> str:
        """Format solution from knowledge base"""
        solution = f"""**Understanding the Problem:**
{result['question']}

**Step-by-Step Solution:**
"""
        for i, step in enumerate(result['steps'], 1):
            solution += f"Step {i}: {step}\n"
        
        solution += f"""
**Final Answer:**
{result['solution']}

**Key Concepts:**
- Topic: {result.get('topic', 'Mathematics').capitalize()}
- Difficulty: {result.get('difficulty', 'Medium').capitalize()}

**Source:** Knowledge Base (Confidence: {round(result['score'] * 100, 1)}%)
"""
        return solution
    
    def _format_web_search_solution(self, query: str, results: list) -> str:
        """Format solution from MCP web search"""
        solution = f"""**Understanding the Problem:**
{query}

**Information Retrieved via MCP (Model Context Protocol):**

"""
        for i, result in enumerate(results[:2], 1):
            title = result.get('title', 'Unknown Source')
            content = result.get('content', '')[:400]
            url = result.get('url', '')
            
            solution += f"""**Source {i}: {title}**
{content}...

🔗 Read more: {url}

"""
        
        solution += """
**Note:** This solution was retrieved using Model Context Protocol (MCP) for web search integration.
"""
        return solution
    
    def _generate_fallback_solution(self, query: str) -> str:
        """Generate fallback response"""
        return f"""**Problem:** {query}

**Status:** Not found in knowledge base. MCP search and LLM unavailable.

**Recommended Resources:**
1. **Khan Academy** - khanacademy.org
2. **Symbolab** - symbolab.com
3. **Wolfram Alpha** - wolframalpha.com
"""
    
    def _generate_solution_with_llm(self, question: str, context: str) -> str:
        """Generate solution using Groq"""
        try:
            chat_completion = self.llm.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Context from MCP Search:\n{context}\n\nQuestion: {question}\n\nProvide a detailed step-by-step solution."}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.3,
                max_tokens=1024,
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            return f"Error generating solution: {str(e)}"
    
    def _extract_context(self, search_results: list) -> str:
        """Extract context from MCP search results"""
        context_parts = []
        for result in search_results[:2]:
            title = result.get('title', 'Unknown')
            content = result.get('content', '')[:500]
            context_parts.append(f"Source: {title}\n{content}")
        return "\n\n".join(context_parts)