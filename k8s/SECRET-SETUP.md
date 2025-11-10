# Secret Setup Guide

## Overview

The MCP Server AAP application requires an Ansible Automation Platform (AAP) access token to function. This sensitive credential is stored in a Kubernetes Secret.

## Why Manual Secret Creation?

For security reasons, the actual secret with your AAP token is **NOT** included in the Git repository. You must create it manually before deploying the application.

## Quick Setup

### Development Environment

```bash
# Create namespace
oc new-project mcp-server-aap-dev

# Create secret with your AAP token
oc create secret generic dev-mcp-server-aap-secret \
  --from-literal=aap-token='YOUR_ACTUAL_AAP_TOKEN_HERE' \
  -n mcp-server-aap-dev

# Verify secret was created
oc get secret mcp-server-aap-secret -n mcp-server-aap-dev
```

### Production Environment

```bash
# Create namespace
oc new-project mcp-server-aap-prod

# Create secret with your AAP token
oc create secret generic mcp-server-aap-secret \
  --from-literal=aap-token='YOUR_ACTUAL_AAP_TOKEN_HERE' \
  -n mcp-server-aap-prod

# Verify secret was created
oc get secret mcp-server-aap-secret -n mcp-server-aap-prod
```

## Deployment Order

**IMPORTANT**: Create the secret **BEFORE** deploying the application!

```bash
# Step 1: Create namespace
oc new-project mcp-server-aap-prod

# Step 2: Create secret (THIS STEP!)
oc create secret generic mcp-server-aap-secret \
  --from-literal=aap-token='YOUR_TOKEN' \
  -n mcp-server-aap-prod

# Step 3: Deploy application
oc apply -k k8s/overlays/prod
```

If you deploy without creating the secret first, you'll get:
```
Error: secret "mcp-server-aap-secret" not found
```

## Secret Structure

The secret contains a single key-value pair:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mcp-server-aap-secret
  namespace: mcp-server-aap-prod
type: Opaque
stringData:
  aap-token: "YOUR_AAP_TOKEN_HERE"
```

## Obtaining an AAP Token

1. Log in to your Ansible Automation Platform Controller
2. Navigate to **Users** → **Your Username** → **Tokens**
3. Click **Add Token**
4. Set scope to appropriate permissions (read templates, launch jobs)
5. Copy the generated token
6. Use this token when creating the secret

For detailed instructions with screenshots, see the main [README.md](../README.md#aap-token-generation).
