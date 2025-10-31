from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

@dataclass
class MCPTool:
    """Represents an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, Any]

@dataclass
class MCPToolResult:
    """Result from an MCP tool call"""
    success: bool
    content: Any
    metadata: Optional[Dict[str, Any]] = None

class MCPServer:
    """Base MCP Server following Model Context Protocol"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools: Dict[str, MCPTool] = {}
    
    def register_tool(self, tool: MCPTool):
        """Register a tool with the server"""
        self.tools[tool.name] = tool
        print(f"✅ MCP Tool registered: {tool.name}")
    
    def list_tools(self) -> List[MCPTool]:
        """List all available tools"""
        return list(self.tools.values())
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Call a tool by name"""
        if tool_name not in self.tools:
            return MCPToolResult(
                success=False,
                content=f"Tool '{tool_name}' not found",
                metadata={"error": "tool_not_found"}
            )
        
        # This should be overridden by subclasses
        raise NotImplementedError("Subclass must implement call_tool")

class MCPClient:
    """Base MCP Client for connecting to servers"""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.connection_id = None
    
    def connect(self) -> bool:
        """Connect to the MCP server"""
        self.connection_id = f"conn_{id(self)}"
        print(f"✅ MCP Client connected to server: {self.server.name}")
        return True
    
    def list_tools(self) -> List[MCPTool]:
        """List available tools from server"""
        return self.server.list_tools()
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Call a tool on the server"""
        return self.server.call_tool(tool_name, arguments)