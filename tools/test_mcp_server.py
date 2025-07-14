#!/usr/bin/env python3
"""
Test script for the MCP Ansible Automation Platform server
Run this to validate your server setup before integrating with Claude Desktop
"""

import asyncio
import json
import sys
from aap_client import AAPClient

async def test_aap_connection():
    """Test basic AAP connection"""
    print("🔍 Testing AAP Connection...")
    try:
        async with AAPClient() as client:
            result = await client.test_connection()
            if result:
                print("✅ AAP connection successful!")
                print(f"   URL: {client.config.url}")
                print(f"   Project ID: {client.config.project_id}")
                return True
            else:
                print("❌ AAP connection failed!")
                return False
    except Exception as e:
        print(f"❌ AAP connection error: {e}")
        return False

async def test_template_extraction():
    """Test template extraction"""
    print("\n🔍 Testing Template Extraction...")
    try:
        async with AAPClient() as client:
            templates = await client.get_job_templates()
            print(f"✅ Found {len(templates)} job templates:")
            for i, template in enumerate(templates[:3]):  # Show first 3
                print(f"   {i+1}. {template.name} (ID: {template.id})")
                print(f"      Playbook: {template.playbook}")
            
            if len(templates) > 3:
                print(f"   ... and {len(templates) - 3} more templates")
            
            return len(templates) > 0
    except Exception as e:
        print(f"❌ Template extraction error: {e}")
        return False

async def test_mcp_server_import():
    """Test MCP server import"""
    print("\n🔍 Testing MCP Server Import...")
    try:
        import server
        print("✅ MCP server module imported successfully!")
        return True
    except Exception as e:
        print(f"❌ MCP server import error: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking Environment Configuration...")
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    required_vars = ['AAP_URL', 'AAP_TOKEN', 'AAP_PROJECT_ID']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * min(len(value), 10)}...")
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file or environment configuration")
        return False
    
    print("✅ All required environment variables are set!")
    return True

async def main():
    """Run all tests"""
    print("🚀 Testing MCP Ansible Automation Platform Server")
    print("=" * 50)
    
    tests = [
        ("Environment Check", check_environment),
        ("MCP Server Import", test_mcp_server_import),
        ("AAP Connection", test_aap_connection),
        ("Template Extraction", test_template_extraction)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your MCP server is ready for Claude Desktop!")
        print("\nNext steps:")
        print("1. Configure Claude Desktop with the provided configuration")
        print("2. Restart Claude Desktop")
        print("3. Test the integration by asking Claude about available Ansible templates")
    else:
        print("⚠️  Some tests failed. Please fix the issues before using with Claude Desktop.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 