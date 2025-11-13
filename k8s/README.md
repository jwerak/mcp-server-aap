# MCP Server AAP - OpenShift Deployment

This directory contains Kubernetes manifests and Kustomize configurations for deploying the MCP Server for Ansible Automation Platform on OpenShift.

## Structure

```
k8s/
├── base/                          # Base Kubernetes resources
│   ├── deployment.yaml           # Application deployment
│   ├── service.yaml              # ClusterIP service
│   ├── route.yaml                # OpenShift HTTPS route
│   ├── configmap.yaml            # Non-sensitive configuration
│   ├── secret.yaml               # Sensitive configuration (AAP token)
│   └── kustomization.yaml        # Base kustomization
├── overlays/
│   ├── dev/                      # Development environment
│   │   └── kustomization.yaml
│   └── prod/                     # Production environment
│       └── kustomization.yaml
└── README.md                     # This file
```

## Prerequisites

1. **OpenShift cluster** with appropriate permissions
2. **kubectl/oc CLI** installed and configured
3. **Kustomize** installed (or use `kubectl -k` / `oc kustomize`)
4. **Container image** built and pushed to a registry

## Building the Container Image

Build and push the container image to your registry:

```bash
# Build the image
podman build -t quay.io/your-org/mcp-server-aap:latest -f Containerfile .

# Push to registry
podman push quay.io/your-org/mcp-server-aap:latest

# Tag for specific environments
podman tag quay.io/your-org/mcp-server-aap:latest quay.io/your-org/mcp-server-aap:dev
podman tag quay.io/your-org/mcp-server-aap:latest quay.io/your-org/mcp-server-aap:stable
```

## Configuration

### ConfigMap (Non-Sensitive)

Edit `base/configmap.yaml` or use overlay-specific configurations:

- `aap-url`: URL of your AAP controller
- `aap-project-id`: AAP project ID
- `aap-verify-ssl`: Whether to verify SSL certificates (true/false)
- `aap-timeout`: Request timeout in seconds
- `aap-max-retries`: Maximum number of API retries

### Secret (Sensitive)

**IMPORTANT**: Never commit actual tokens to version control!

Option 1: Edit the secret before applying:
```bash
# Edit base/secret.yaml and replace 'your-aap-token-here' with your actual token
vi k8s/base/secret.yaml
```

Option 2: Create the secret separately:
```bash
# Create namespace first
oc new-project mcp-server-aap-dev

# Create secret from command line
oc create secret generic mcp-server-aap-secret \
  --from-literal=aap-token='your-actual-token-here' \
  -n mcp-server-aap-dev

# Then remove the secret from kustomization.yaml resources
```

Option 3: Use OpenShift Sealed Secrets or External Secrets Operator for production.

## Deployment

### Deploy to Development

```bash
# Review the generated manifests
oc kustomize k8s/overlays/dev

# Create namespace (if it doesn't exist)
oc new-project mcp-server-aap-dev

# Apply the configuration
oc apply -k k8s/overlays/dev

# Check the deployment
oc get pods -n mcp-server-aap-dev
oc get route -n mcp-server-aap-dev
```

### Deploy to Production

```bash
# Review the generated manifests
oc kustomize k8s/overlays/prod

# Create namespace (if it doesn't exist)
oc new-project mcp-server-aap-prod

# Apply the configuration
oc apply -k k8s/overlays/prod

# Check the deployment
oc get pods -n mcp-server-aap-prod
oc get route -n mcp-server-aap-prod
```

### Deploy Base Configuration (without overlays)

```bash
# Review the generated manifests
oc kustomize k8s/base

# Create namespace
oc new-project mcp-server-aap

# Apply the configuration
oc apply -k k8s/base

# Check the deployment
oc get pods -n mcp-server-aap
oc get route -n mcp-server-aap
```

## Accessing the Application

After deployment, get the route URL:

```bash
# For dev environment
oc get route -n mcp-server-aap-dev

# For prod environment
oc get route -n mcp-server-aap-prod
```

The application will be accessible via HTTPS at the route URL.

## Updating Configuration

### Update ConfigMap

```bash
# Edit the configmap
oc edit configmap mcp-server-aap-config -n mcp-server-aap-prod

# Restart the deployment to pick up changes
oc rollout restart deployment/mcp-server-aap -n mcp-server-aap-prod
```

### Update Secret

```bash
# Update the secret
oc create secret generic mcp-server-aap-secret \
  --from-literal=aap-token='new-token-here' \
  --dry-run=client -o yaml | oc apply -f - -n mcp-server-aap-prod

# Restart the deployment to pick up changes
oc rollout restart deployment/mcp-server-aap -n mcp-server-aap-prod
```

## Monitoring

### Check Logs

```bash
# View logs
oc logs -f deployment/mcp-server-aap -n mcp-server-aap-prod

# View logs from all pods
oc logs -l app=mcp-server-aap -n mcp-server-aap-prod --tail=100 -f
```

### Connection details

```bash
oc get route/mcp-server-aap -n mcp-server-aap-prod -o jsonpath='{.spec.host}'
```

### Health Checks

The deployment includes liveness and readiness probes:
- Liveness probe: `/health` endpoint
- Readiness probe: `/health` endpoint

## Troubleshooting

### Pod not starting

```bash
# Check pod status
oc describe pod <pod-name> -n mcp-server-aap-dev

# Check logs
oc logs <pod-name> -n mcp-server-aap-dev

# Check events
oc get events -n mcp-server-aap-dev --field-selector involvedObject.name=<pod-name>
```

### Connection issues

```bash
# Test service connectivity from another pod
oc run test-pod --image=curlimages/curl --rm -it --restart=Never -n mcp-server-aap-dev \
  -- curl http://mcp-server-aap:8000/health

# Check route
oc get route -n mcp-server-aap-dev
```

### Configuration issues

```bash
# Verify ConfigMap
oc get configmap mcp-server-aap-config -o yaml -n mcp-server-aap-dev

# Verify Secret (don't show values)
oc get secret mcp-server-aap-secret -n mcp-server-aap-dev

# Check environment variables in pod
oc exec <pod-name> -n mcp-server-aap-dev -- env | grep AAP
```

## Cleanup

### Remove deployment

```bash
# Dev environment
oc delete -k k8s/overlays/dev
oc delete project mcp-server-aap-dev

# Prod environment
oc delete -k k8s/overlays/prod
oc delete project mcp-server-aap-prod

# Base (if deployed without overlay)
oc delete -k k8s/base
oc delete project mcp-server-aap
```

## Security Considerations

1. **Never commit secrets** to version control
2. Use **OpenShift's RBAC** to control access to secrets
3. Consider using **Sealed Secrets** or **External Secrets Operator** for production
4. Enable **SSL verification** in production (`AAP_VERIFY_SSL=true`)
5. Use **private container registries** with pull secrets
6. Review and adjust **security contexts** as needed
7. Implement **network policies** to restrict traffic

## Customization

### Add Network Policy

Create `base/networkpolicy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mcp-server-aap
spec:
  podSelector:
    matchLabels:
      app: mcp-server-aap
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
  - to:
    - podSelector: {}
```

Add it to `base/kustomization.yaml` resources.

### Add Resource Quotas

Create `overlays/prod/resourcequota.yaml`:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: mcp-server-aap-quota
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 2Gi
    limits.cpu: "4"
    limits.memory: 4Gi
    pods: "5"
```

Add it to `overlays/prod/kustomization.yaml` resources.

## Additional Resources

- [Kustomize Documentation](https://kustomize.io/)
- [OpenShift Documentation](https://docs.openshift.com/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
