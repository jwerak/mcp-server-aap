#!/usr/bin/env python3
"""
MCP Server for Ansible Automation Platform
Provides functions to extract templates and launch jobs
"""

import json
import logging
from typing import Any, Dict, Optional
from fastmcp import FastMCP
from aap_client import AAPClient, JobTemplate, JobLaunch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("ansible-aap-server")


@mcp.tool()
async def get_job_templates(project_id: Optional[str] = None) -> str:
    """Get available job templates from the configured AAP project with detailed descriptions and metadata"""
    try:
        async with AAPClient() as client:
            templates = await client.get_job_templates(project_id)

            # Format templates for display with enhanced descriptions
            if not templates:
                return "No job templates found in the specified project."

            # Create detailed template information
            template_details = []
            template_list = []

            for i, template in enumerate(templates, 1):
                # Detailed description for readable format
                template_detail = f"**{i}. {template.name}** (ID: {template.id})\n"
                template_detail += f"   📋 Description: {template.description or 'No description provided'}\n"
                template_detail += f"   📘 Playbook: {template.playbook}\n"
                template_detail += f"   📁 Project: {template.project}\n"

                if template.inventory:
                    template_detail += f"   🗂️  Inventory: {template.inventory}\n"
                if template.credential:
                    template_detail += f"   🔑 Credential: {template.credential}\n"

                template_detail += f"   📝 Survey Enabled: {'Yes' if template.survey_enabled else 'No'}\n"
                template_details.append(template_detail)

                # Also maintain JSON structure for programmatic use
                template_info = {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "playbook": template.playbook,
                    "project": template.project,
                    "survey_enabled": template.survey_enabled,
                }
                if template.inventory:
                    template_info["inventory"] = template.inventory
                if template.credential:
                    template_info["credential"] = template.credential
                template_list.append(template_info)

            # Create comprehensive response
            response_text = f"Found {len(templates)} job template{'s' if len(templates) != 1 else ''}:\n\n"
            response_text += "\n".join(template_details)
            response_text += "\n\n---\n\nJSON Data:\n```json\n"
            response_text += json.dumps(template_list, indent=2)
            response_text += "\n```"

            return response_text

    except Exception as e:
        logger.error(f"Error in get_job_templates: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def launch_job_template(
    template_id: int,
    extra_vars: Optional[Dict[str, Any]] = None,
    inventory: Optional[int] = None,
    credentials: Optional[list[int]] = None,
) -> str:
    """Launch an Ansible job template with optional parameters"""
    try:
        async with AAPClient() as client:
            launch_result = await client.launch_job_template(
                template_id=template_id,
                extra_vars=extra_vars,
                inventory=inventory,
                credentials=credentials,
            )

            return (
                f"Job launched successfully!\n\n"
                f"Job ID: {launch_result.job}\n"
                f"Launch ID: {launch_result.id}\n"
                f"URL: {launch_result.url}\n"
                f"Type: {launch_result.type}\n\n"
                "Use get_job_status to check the job progress."
            )

    except Exception as e:
        logger.error(f"Error in launch_job_template: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_job_status(job_id: int) -> str:
    """Get the status and details of a running or completed job"""
    try:
        async with AAPClient() as client:
            job_status = await client.get_job_status(job_id)

            # Extract key status information
            status_info = {
                "id": job_status.get("id"),
                "name": job_status.get("name"),
                "status": job_status.get("status"),
                "failed": job_status.get("failed"),
                "started": job_status.get("started"),
                "finished": job_status.get("finished"),
                "elapsed": job_status.get("elapsed"),
                "job_template": job_status.get("job_template"),
                "playbook": job_status.get("playbook"),
            }

            return f"Job Status:\n\n{json.dumps(status_info, indent=2)}"

    except Exception as e:
        logger.error(f"Error in get_job_status: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_job_output(job_id: int) -> str:
    """Get the output/logs of a job"""
    try:
        async with AAPClient() as client:
            job_output = await client.get_job_stdout(job_id)

            return f"Job Output (Job ID: {job_id}):\n\n```\n{job_output}\n```"

    except Exception as e:
        logger.error(f"Error in get_job_output: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def test_aap_connection() -> str:
    """Test the connection to Ansible Automation Platform"""
    try:
        async with AAPClient() as client:
            connection_ok = await client.test_connection()

            # Create simple result
            result_text = (
                f"AAP Connection Test: {'✅ SUCCESS' if connection_ok else '❌ FAILED'}\n\n"
                f"URL: {client.config.url}\n"
                f"Project ID: {client.config.project_id}\n"
                f"SSL Verification: {client.config.verify_ssl}"
            )

            return result_text

    except Exception as e:
        logger.error(f"Error in test_aap_connection: {str(e)}")
        return f"Error: {str(e)}"


if __name__ == "__main__":
    # Run the FastMCP server with HTTP transport
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
