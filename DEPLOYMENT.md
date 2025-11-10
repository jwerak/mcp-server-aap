# Quick Deployment Guide - MCP Server AAP on OpenShift

This guide provides quick commands to deploy the MCP Server for Ansible Automation Platform on OpenShift.

## Prerequisites

- OpenShift cluster access (`oc` CLI configured)
- Container image built and pushed to registry
- AAP access token ready

## Quick Start - Development Environment

```bash
# 1. Build and push container image
podman build -t quay.io/your-org/mcp-server-aap:dev -f Containerfile .
podman push quay.io/your-org/mcp-server-aap:dev

# 2. Update image name in kustomization (if different from quay.io/your-org/mcp-server-aap)
# Edit k8s/overlays/dev/kustomization.yaml

# 3. Update configuration values
# Edit k8s/overlays/dev/kustomization.yaml - update AAP URL and project ID

# 4. Create and configure secret with actual AAP token
oc new-project mcp-server-aap-dev
oc create secret generic dev-mcp-server-aap-secret \
  --from-literal=aap-token='YOUR_ACTUAL_AAP_TOKEN_HERE' \
  -n mcp-server-aap-dev

# 5. Deploy (will use the secret created above)
oc apply -k k8s/overlays/dev

# 6. Check status
oc get pods -n mcp-server-aap-dev
oc get route -n mcp-server-aap-dev

# 7. View logs
oc logs -f deployment/dev-mcp-server-aap -n mcp-server-aap-dev

# 8. Get the HTTPS URL
echo "Application URL: https://$(oc get route dev-mcp-server-aap -n mcp-server-aap-dev -o jsonpath='{.spec.host}')"
```

## Quick Start - Production Environment

```bash
# 1. Build and push container image
podman build -t quay.io/your-org/mcp-server-aap:stable -f Containerfile .
podman push quay.io/your-org/mcp-server-aap:stable

# 2. Update production configuration
# Edit k8s/overlays/prod/kustomization.yaml - update AAP URL, project ID, and route host

# 3. Create namespace and secret
oc new-project mcp-server-aap-prod
oc create secret generic prod-mcp-server-aap-secret \
  --from-literal=aap-token='YOUR_ACTUAL_PROD_AAP_TOKEN_HERE' \
  -n mcp-server-aap-prod

# 4. Deploy
oc apply -k k8s/overlays/prod

# 5. Check status
oc get pods -n mcp-server-aap-prod
oc get route -n mcp-server-aap-prod

# 6. Get the HTTPS URL
echo "Application URL: https://$(oc get route prod-mcp-server-aap -n mcp-server-aap-prod -o jsonpath='{.spec.host}')"
```

## Configuration Overview

### ConfigMap (Non-Sensitive)
Configured in `k8s/overlays/{env}/kustomization.yaml`:
- `aap-url`: AAP controller URL
- `aap-project-id`: AAP project ID
- `aap-verify-ssl`: SSL verification (true/false)
- `aap-timeout`: Request timeout (seconds)
- `aap-max-retries`: API retry attempts

### Secret (Sensitive)
Created via `oc create secret`:
- `aap-token`: AAP access token (Bearer token)

**IMPORTANT**: Never commit actual tokens to Git!

## Common Operations

### Update Configuration

```bash
# Update ConfigMap - edit the kustomization.yaml and reapply
oc apply -k k8s/overlays/dev

# Restart to pick up changes
oc rollout restart deployment/dev-mcp-server-aap -n mcp-server-aap-dev
```

### Update Secret

```bash
# Update with new token
oc create secret generic dev-mcp-server-aap-secret \
  --from-literal=aap-token='NEW_TOKEN_HERE' \
  --dry-run=client -o yaml | oc apply -f - -n mcp-server-aap-dev

# Restart deployment
oc rollout restart deployment/dev-mcp-server-aap -n mcp-server-aap-dev
```

### Scale Application

```bash
# Manual scaling
oc scale deployment/dev-mcp-server-aap --replicas=3 -n mcp-server-aap-dev

# Auto-scaling
oc autoscale deployment/dev-mcp-server-aap \
  --min=1 --max=5 --cpu-percent=80 \
  -n mcp-server-aap-dev
```

### View Logs

```bash
# Follow logs
oc logs -f deployment/dev-mcp-server-aap -n mcp-server-aap-dev

# All pods
oc logs -l app=mcp-server-aap -n mcp-server-aap-dev --tail=100 -f

# Previous crashed container
oc logs deployment/dev-mcp-server-aap -n mcp-server-aap-dev --previous
```

### Troubleshooting

```bash
# Check pod status
oc get pods -n mcp-server-aap-dev
oc describe pod <pod-name> -n mcp-server-aap-dev

# Check events
oc get events -n mcp-server-aap-dev --sort-by='.lastTimestamp'

# Check environment variables
oc exec deployment/dev-mcp-server-aap -n mcp-server-aap-dev -- env | grep AAP

# Test service connectivity
oc run test-curl --image=curlimages/curl --rm -it --restart=Never -n mcp-server-aap-dev \
  -- curl http://dev-mcp-server-aap:8000/health

# Port forward for local testing
oc port-forward deployment/dev-mcp-server-aap 8000:8000 -n mcp-server-aap-dev
# Then access: http://localhost:8000
```

## Cleanup

```bash
# Remove dev environment
oc delete -k k8s/overlays/dev
oc delete project mcp-server-aap-dev

# Remove prod environment
oc delete -k k8s/overlays/prod
oc delete project mcp-server-aap-prod
```

## Security Best Practices

1. **Secrets Management**: Use OpenShift Sealed Secrets or External Secrets Operator for production
2. **SSL Verification**: Always enable SSL verification in production (`aap-verify-ssl: "true"`)
3. **Image Registry**: Use private container registries with image pull secrets
4. **Network Policies**: Implement network policies to restrict traffic
5. **RBAC**: Configure appropriate role-based access control
6. **Resource Limits**: Set appropriate CPU/memory limits for pods

## Directory Structure

```
k8s/
├── base/                       # Base Kubernetes resources
│   ├── deployment.yaml        # Pod deployment with env vars from ConfigMap/Secret
│   ├── service.yaml           # ClusterIP service on port 8000
│   ├── route.yaml             # OpenShift HTTPS route with edge TLS
│   ├── configmap.yaml         # Non-sensitive config (URLs, timeouts, etc.)
│   ├── secret.yaml            # Template for sensitive data (AAP token)
│   └── kustomization.yaml     # Base kustomize config
└── overlays/
    ├── dev/                   # Development environment
    │   └── kustomization.yaml # Dev-specific config (1 replica, lower resources)
    └── prod/                  # Production environment
        └── kustomization.yaml # Prod-specific config (2 replicas, higher resources)
```

## Environment Differences

| Setting | Dev | Prod |
|---------|-----|------|
| Namespace | mcp-server-aap-dev | mcp-server-aap-prod |
| Replicas | 1 | 2 |
| Memory Request | 128Mi | 256Mi |
| Memory Limit | 256Mi | 1Gi |
| CPU Request | 100m | 200m |
| CPU Limit | 250m | 1000m |
| SSL Verify | false | true |
| Image Tag | dev | stable |

## Next Steps

- Set up CI/CD pipeline for automated deployments
- Configure monitoring and alerting
- Implement backup/restore procedures
- Set up multi-environment promotion workflow
- Configure horizontal pod autoscaling based on metrics

For detailed information, see [k8s/README.md](k8s/README.md)

