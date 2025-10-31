from .mcp_protocol import MCPServer, MCPTool, MCPToolResult
from tavily import TavilyClient
import os
from typing import Dict, Any

class MathSearchMCPServer(MCPServer):
    """MCP Server providing math search capabilities"""
    
    def __init__(self):
        super().__init__("math-search-server")
        
        # Initialize Tavily
        tavily_key = os.getenv("TAVILY_API_KEY")
        self.tavily_client = TavilyClient(api_key=tavily_key) if tavily_key else None
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        
        # Tool 1: Search Math Solution
        search_solution_tool = MCPTool(
            name="search_math_solution",
            description="Search the web for mathematical solutions, explanations, and step-by-step guides",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The mathematical question or problem to search for"
                    },
                    "search_depth": {
                        "type": "string",
                        "enum": ["basic", "advanced"],
                        "description": "How thorough the search should be",
                        "default": "basic"
                    }
                },
                "required": ["query"]
            }
        )
        self.register_tool(search_solution_tool)
        
        # Tool 2: Search Math Concept
        search_concept_tool = MCPTool(
            name="search_math_concept",
            description="Search for explanations of mathematical concepts, theorems, and definitions",
            parameters={
                "type": "object",
                "properties": {
                    "concept": {
                        "type": "string",
                        "description": "The mathematical concept to explain"
                    }
                },
                "required": ["concept"]
            }
        )
        self.register_tool(search_concept_tool)
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute a tool call"""
        
        if tool_name == "search_math_solution":
            return self._search_math_solution(arguments)
        elif tool_name == "search_math_concept":
            return self._search_math_concept(arguments)
        else:
            return MCPToolResult(
                success=False,
                content=f"Unknown tool: {tool_name}",
                metadata={"error": "unknown_tool"}
            )
    
    def _search_math_solution(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """Search for math solutions"""
        query = arguments.get("query", "")
        search_depth = arguments.get("search_depth", "basic")
        
        if not self.tavily_client:
            return MCPToolResult(
                success=False,
                content="Tavily API not configured",
                metadata={
                    "error": "api_not_configured",
                    "query": query
                }
            )
        
        try:
            # Enhanced query
            enhanced_query = f"how to solve {query} step by step mathematics"
            
            # Perform search
            results = self.tavily_client.search(
                query=enhanced_query,
                search_depth=search_depth,
                max_results=5,
                include_domains=[
                    "khanacademy.org",
                    "mathway.com",
                    "symbolab.com",
                    "math.stackexchange.com",
                    "brilliant.org",
                    "wolframalpha.com"
                ]
            )
            
            return MCPToolResult(
                success=True,
                content={
                    "query": query,
                    "enhanced_query": enhanced_query,
                    "results": results.get("results", []),
                    "found": len(results.get("results", [])) > 0
                },
                metadata={
                    "search_depth": search_depth,
                    "num_results": len(results.get("results", []))
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content=str(e),
                metadata={
                    "error": "search_failed",
                    "query": query
                }
            )
    
    def _search_math_concept(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """Search for concept explanations"""
        concept = arguments.get("concept", "")
        
        if not self.tavily_client:
            return MCPToolResult(
                success=False,
                content="Tavily API not configured",
                metadata={
                    "error": "api_not_configured",
                    "concept": concept
                }
            )
        
        try:
            enhanced_query = f"explain {concept} mathematics definition theorem"
            
            results = self.tavily_client.search(
                query=enhanced_query,
                search_depth="advanced",
                max_results=3,
                include_domains=[
                    "khanacademy.org",
                    "math.stackexchange.com",
                    "brilliant.org",
                    "mathworld.wolfram.com",
                    "wikipedia.org"
                ]
            )
            
            return MCPToolResult(
                success=True,
                content={
                    "concept": concept,
                    "enhanced_query": enhanced_query,
                    "results": results.get("results", []),
                    "found": len(results.get("results", [])) > 0
                },
                metadata={
                    "num_results": len(results.get("results", []))
                }
            )
            
        except Exception as e:
            return MCPToolResult(
                success=False,
                content=str(e),
                metadata={
                    "error": "search_failed",
                    "concept": concept
                }
            )