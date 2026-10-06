from typing import Protocol, Any, Dict

class ToolRegistryInterface(Protocol):
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        ...
    
    def has_tool(self, tool_name: str) -> bool:
        ...
