#!/usr/bin/env python3
"""
Quick test script for debugging individual components
Use this to test specific parts without the full MCP protocol
"""

import asyncio
import json
import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import mcp
        print("✅ MCP library imported")
    except ImportError as e:
        print(f"❌ MCP import failed: {e}")
        return False
    
    try:
        import httpx
        print("✅ HTTPX library imported")
    except ImportError as e:
        print(f"❌ HTTPX import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic library imported")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        from aap_client import AAPClient, AAPConfig
        print("✅ AAP client imported")
    except ImportError as e:
        print(f"❌ AAP client import failed: {e}")
        return False
    
    try:
        import server
        print("✅ MCP server imported")
    except ImportError as e:
        print(f"❌ MCP server import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['AAP_URL', 'AAP_TOKEN', 'AAP_PROJECT_ID']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'TOKEN' in var:
                display_value = f"{'*' * min(len(value), 8)}...{value[-4:]}" if len(value) > 8 else '*' * len(value)
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

async def test_aap_client():
    """Test AAP client directly"""
    print("\n🔍 Testing AAP client...")
    
    try:
        from aap_client import AAPClient
        
        # Test client creation
        client = AAPClient()
        print(f"✅ Client created for URL: {client.config.url}")
        
        # Test connection
        async with client:
            print("🔗 Testing connection...")
            connection_ok = await client.test_connection()
            
            if connection_ok:
                print("✅ Connection successful!")
                
                # Test template listing
                print("📋 Getting job templates...")
                templates = await client.get_job_templates()
                print(f"✅ Found {len(templates)} templates")
                
                if templates:
                    print("Sample templates:")
                    for i, template in enumerate(templates[:3]):
                        print(f"  {i+1}. {template.name} (ID: {template.id})")
                        print(f"      Playbook: {template.playbook}")
                
                return True
            else:
                print("❌ Connection failed!")
                return False
                
    except Exception as e:
        print(f"❌ AAP client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_tools():
    """Test MCP tool definitions"""
    print("\n🔍 Testing MCP tools...")
    
    try:
        import server
        
        # Get tool definitions
        tools = await server.list_tools()
        print(f"✅ Found {len(tools)} MCP tools:")
        
        for tool in tools:
            print(f"  📋 {tool.name}")
            print(f"     Description: {tool.description}")
            
            # Validate schema
            if tool.inputSchema:
                try:
                    json.dumps(tool.inputSchema)
                    print(f"     ✅ Schema is valid JSON")
                except:
                    print(f"     ❌ Schema is invalid")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_tool_call():
    """Test a simple tool call"""
    print("\n🔍 Testing tool call...")
    
    try:
        import server
        
        # Test the connection test tool
        result = await server.call_tool("test_aap_connection", {})
        
        if result and result.content:
            print("✅ Tool call successful!")
            for content in result.content:
                print(f"Response: {content.text}")
            return True
        else:
            print("❌ Tool call failed - no content")
            return False
            
    except Exception as e:
        print(f"❌ Tool call test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def interactive_test():
    """Interactive testing mode"""
    print("\n🎮 Interactive testing mode")
    print("Available commands:")
    print("  1 - Test imports")
    print("  2 - Test environment")
    print("  3 - Test AAP client")
    print("  4 - Test MCP tools")
    print("  5 - Test tool call")
    print("  6 - Run all tests")
    print("  q - Quit")
    
    while True:
        try:
            command = input("\nEnter command: ").strip()
            
            if command == "q":
                break
            elif command == "1":
                test_imports()
            elif command == "2":
                test_environment()
            elif command == "3":
                await test_aap_client()
            elif command == "4":
                await test_mcp_tools()
            elif command == "5":
                await test_tool_call()
            elif command == "6":
                await run_all_tests()
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def run_all_tests():
    """Run all tests"""
    print("🧪 Running all tests...")
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("AAP Client", test_aap_client),
        ("MCP Tools", test_mcp_tools),
        ("Tool Call", test_tool_call)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your MCP server is ready!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

async def main():
    """Main function"""
    print("🔧 Quick Test for MCP Ansible AAP Server")
    print("=" * 45)
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1]
        
        if command == "imports":
            test_imports()
        elif command == "env":
            test_environment()
        elif command == "aap":
            await test_aap_client()
        elif command == "tools":
            await test_mcp_tools()
        elif command == "call":
            await test_tool_call()
        elif command == "all":
            await run_all_tests()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: imports, env, aap, tools, call, all")
    else:
        # Interactive mode
        await interactive_test()

if __name__ == "__main__":
    asyncio.run(main()) 