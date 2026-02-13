import json
from typing import List, Dict, Any, Optional


class ToolRegistry:
    """Tool registry for discovering and managing tools."""
    
    def __init__(self, registry_path: str = "tool_registry.json"):
        with open(registry_path, 'r') as f:
            self.registry = json.load(f)
        self.tools = self.registry['tools']
    
    def list_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """List all tools in a specific category."""
        return [tool for tool in self.tools if tool['category'] == category]
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search tools by name or description."""
        query_lower = query.lower()
        return [
            tool for tool in self.tools
            if query_lower in tool['name'].lower() or 
               query_lower in tool['description'].lower()
        ]
    
    def filter_tools_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Filter tools by a specific tag."""
        return [tool for tool in self.tools if tag in tool['tags']]
    
    def filter_tools_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Filter tools by status (active, deprecated, experimental)."""
        return [tool for tool in self.tools if tool['status'] == status]
    
    def get_tool_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific tool by name."""
        for tool in self.tools:
            if tool['name'] == name:
                return tool
        return None
    
    def list_all_categories(self) -> Dict[str, str]:
        """List all available categories with descriptions."""
        return self.registry['categories']
    
    def list_all_tags(self) -> Dict[str, str]:
        """List all available tags with descriptions."""
        return self.registry['tags']
    
    def get_tools_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the tool registry."""
        return {
            'total_tools': len(self.tools),
            'categories': len(self.registry['categories']),
            'tags': len(self.registry['tags']),
            'by_category': {
                cat: len(self.list_tools_by_category(cat))
                for cat in self.registry['categories'].keys()
            },
            'by_status': {
                status: len(self.filter_tools_by_status(status))
                for status in ['active', 'deprecated', 'experimental']
            }
        }


def print_tool(tool: Dict[str, Any], detailed: bool = False):
    """Pretty print tool information."""
    print(f"\n{tool['name']} (v{tool['version']})")
    print(f"  Category: {tool['category']}")
    print(f"  Status: {tool['status']}")
    print(f"  Tags: {', '.join(tool['tags'])}")
    if detailed:
        print(f"  Description: {tool['description']}")
        print(f"  Dependencies: {', '.join(tool['dependencies'])}")


if __name__ == "__main__":
    registry = ToolRegistry()
    
    print("=" * 70)
    print("TOOL REGISTRY DISCOVERY TESTS")
    print("=" * 70)
    
    # Test 1: List tools by category
    print("\n1. Tools by Category:")
    for category in registry.list_all_categories().keys():
        tools = registry.list_tools_by_category(category)
        print(f"\n  {category.upper()} ({len(tools)} tools):")
        for tool in tools:
            print(f"    - {tool['name']}")
    
    # Test 2: Search tools
    print("\n2. Search for 'email':")
    results = registry.search_tools("email")
    for tool in results:
        print(f"    - {tool['name']}: {tool['description']}")
    
    # Test 3: Filter by tag
    print("\n3. Tools with 'read-only' tag:")
    results = registry.filter_tools_by_tag("read-only")
    for tool in results:
        print(f"    - {tool['name']}")
    
    print("\n4. Tools with 'rate-limited' tag:")
    results = registry.filter_tools_by_tag("rate-limited")
    for tool in results:
        print(f"    - {tool['name']}")
    
    # Test 4: Filter by status
    print("\n5. Active tools:")
    results = registry.filter_tools_by_status("active")
    print(f"    Found {len(results)} active tools")
    
    # Test 5: Get specific tool metadata
    print("\n6. Metadata for 'query_database':")
    metadata = registry.get_tool_metadata("query_database")
    if metadata:
        print_tool(metadata, detailed=True)
    
    # Test 6: Summary
    print("\n7. Registry Summary:")
    summary = registry.get_tools_summary()
    print(f"    Total tools: {summary['total_tools']}")
    print(f"    Categories: {summary['categories']}")
    print(f"    Tags: {summary['tags']}")
    print(f"    By category: {summary['by_category']}")
    print(f"    By status: {summary['by_status']}")
    
    print("\n" + "=" * 70)
    print("✓ All discovery functions tested successfully")
    print("=" * 70)
