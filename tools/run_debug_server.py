#!/usr/bin/env python3
"""
Run MCP server with debug logging
This helps debug the server startup and operation
"""

import asyncio
import logging
import sys
import os

# Setup comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),  # Log to stderr so it doesn't interfere with MCP protocol
        logging.FileHandler('mcp_server_debug.log')  # Also log to file
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check and log environment configuration"""
    logger.info("🔍 Checking environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['AAP_URL', 'AAP_TOKEN', 'AAP_PROJECT_ID']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var:
                display_value = f"{'*' * min(len(value), 8)}...{value[-4:]}" if len(value) > 8 else '*' * len(value)
            else:
                display_value = value
            logger.info(f"✅ {var}: {display_value}")
        else:
            logger.warning(f"❌ {var}: Not set")
    
    optional_vars = ['AAP_VERIFY_SSL', 'AAP_TIMEOUT', 'AAP_MAX_RETRIES']
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"ℹ️  {var}: {value}")

def setup_debug_logging():
    """Setup debug logging for all components"""
    loggers = [
        'aap_client',
        'mcp.server',
        'mcp.client',
        'httpx',
        'asyncio'
    ]
    
    for logger_name in loggers:
        debug_logger = logging.getLogger(logger_name)
        debug_logger.setLevel(logging.DEBUG)
        logger.info(f"🔧 Enabled debug logging for: {logger_name}")

async def test_aap_connection():
    """Test AAP connection before starting server"""
    logger.info("🔍 Testing AAP connection before starting server...")
    
    try:
        from aap_client import AAPClient
        
        async with AAPClient() as client:
            logger.info(f"Connecting to: {client.config.url}")
            logger.info(f"Project ID: {client.config.project_id}")
            logger.info(f"SSL Verification: {client.config.verify_ssl}")
            
            # Test connection
            connection_ok = await client.test_connection()
            if connection_ok:
                logger.info("✅ AAP connection successful!")
                
                # Test template listing
                templates = await client.get_job_templates()
                logger.info(f"✅ Found {len(templates)} job templates")
                
                if templates:
                    logger.info("Sample templates:")
                    for i, template in enumerate(templates[:3]):
                        logger.info(f"  {i+1}. {template.name} (ID: {template.id})")
                        
                return True
            else:
                logger.error("❌ AAP connection failed!")
                return False
                
    except Exception as e:
        logger.error(f"❌ AAP connection test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def run_server():
    """Run the MCP server with debug logging"""
    logger.info("🚀 Starting MCP Ansible AAP Server in DEBUG mode")
    logger.info("=" * 60)
    
    # Check environment
    check_environment()
    
    # Setup debug logging
    setup_debug_logging()
    
    # Test AAP connection
    connection_ok = await test_aap_connection()
    
    if not connection_ok:
        logger.warning("⚠️  AAP connection test failed, but starting server anyway...")
        logger.warning("Server will return errors for AAP operations until connection is fixed")
    
    logger.info("🎯 Starting MCP server...")
    logger.info("Server will communicate via stdin/stdout")
    logger.info("Debug logs will be written to: mcp_server_debug.log")
    logger.info("=" * 60)
    
    # Import and run the server
    try:
        import server
        await server.main()
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def main():
    """Main entry point"""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 