from src.tool_registry import get_tool_list

def test_tool_list_not_empty():
    tools = get_tool_list()
    assert isinstance(tools, list)
    assert len(tools) > 0
    for tool in tools:
        assert "id" in tool
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool
        assert "function" in tool

def main():
    tools = get_tool_list()
    for tool in tools:
        print(f"ID: {tool['id']}, 名稱: {tool['name']}, 說明: {tool['description']}")
        print(f"參數: {tool['parameters']}")
        print("------")

if __name__ == "__main__":
    main() 