from src.tool_registry import get_tool_list

def main():
    tools = get_tool_list()
    for tool in tools:
        print(f"ID: {tool['id']}, 名稱: {tool['name']}, 說明: {tool['description']}")
        print(f"參數: {tool['parameters']}")
        print("------")

if __name__ == "__main__":
    main() 