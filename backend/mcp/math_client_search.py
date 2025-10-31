from .mcp_protocol import MCPClient
from .math_server_search import MathSearchMCPServer
from typing import Dict, Any

class MathSearchMCPClient:
    """Client for Math Search MCP Server"""
    
    def __init__(self):
        # Create server instance
        self.server = MathSearchMCPServer()
        
        # Create client connected to server
        self.client = MCPClient(self.server)
        
        # Connect
        self.client.connect()
        
        # List available tools
        tools = self.client.list_tools()
        print(f"📋 MCP Tools available: {[t.name for t in tools]}")
    
    def search_math_solution(self, query: str, search_depth: str = "basic") -> Dict[str, Any]:
        """Search for math solutions via MCP"""
        result = self.client.call_tool(
            "search_math_solution",
            {
                "query": query,
                "search_depth": search_depth
            }
        )
        
        if result.success:
            return result.content
        else:
            return {
                "error": result.content,
                "found": False,
                "results": []
            }
    
    def search_math_concept(self, concept: str) -> Dict[str, Any]:
        """Search for concept explanations via MCP"""
        result = self.client.call_tool(
            "search_math_concept",
            {
                "concept": concept
            }
        )
        
        if result.success:
            return result.content
        else:
            return {
                "error": result.content,
                "found": False,
                "results": []
            }