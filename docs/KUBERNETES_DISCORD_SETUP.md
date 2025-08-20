# Kubernetes Deployment Update for Discord Notifications

This document shows how to update your Kubernetes production deployment to include Discord notification environment variables.

## Option 1: Update the Secret (Recommended)

### Step 1: Update the existing secret
```bash
# Get current secret values
kubectl get secret eai-agent-secrets -o yaml > eai-agent-secrets-backup.yaml

# Create a new secret with Discord variables
kubectl create secret generic eai-agent-secrets-new \
  --from-literal=DISCORD_WEBHOOK_URL="YOUR_DISCORD_WEBHOOK_URL_HERE" \
  --from-literal=ENVIRONMENT="production" \
  --from-env-file=<(kubectl get secret eai-agent-secrets -o go-template='{{range $k,$v := .data}}{{printf "%s=%s\n" $k ($v | base64decode)}}{{end}}') \
  --dry-run=client -o yaml | kubectl apply -f -

# Rename the secret
kubectl delete secret eai-agent-secrets
kubectl create secret generic eai-agent-secrets \
  --from-literal=DISCORD_WEBHOOK_URL="YOUR_DISCORD_WEBHOOK_URL_HERE" \
  --from-literal=ENVIRONMENT="production" \
  --from-env-file=<(kubectl get secret eai-agent-secrets-new -o go-template='{{range $k,$v := .data}}{{printf "%s=%s\n" $k ($v | base64decode)}}{{end}}')

kubectl delete secret eai-agent-secrets-new
```

### Step 2: Restart deployment to pick up new environment variables
```bash
kubectl rollout restart deployment eai-agent
```

## Option 2: Use External Secret Management

If you're using external secret management (like Google Secret Manager, AWS Secrets Manager, etc.), add the Discord configuration there and ensure it's synced to your Kubernetes secret.

## Option 3: Direct Environment Variables (Not Recommended for Production)

You can also add environment variables directly to the deployment, but this is not recommended for sensitive data like webhook URLs.

```yaml
# Add to k8s/prod/resources.yaml under containers env section
env:
  - name: DISCORD_WEBHOOK_URL
    value: "YOUR_DISCORD_WEBHOOK_URL_HERE"
  - name: ENVIRONMENT
    value: "production"
```

## Verification

After updating the deployment, verify the configuration:

```bash
# Check if environment variables are set in the pod
kubectl exec -it deployment/eai-agent -- env | grep -E "(DISCORD|ENVIRONMENT)"

# Check application logs for Discord configuration
kubectl logs deployment/eai-agent | grep -i discord

# Test the notification system by uploading a prompt version
# (Use the admin interface or API)
```

## Important Security Notes

1. **Never commit webhook URLs to version control**
2. **Use Kubernetes secrets for sensitive data**
3. **Rotate webhook URLs periodically**
4. **Limit access to production secrets**

## Rollback Plan

If you need to rollback:

```bash
# Restore from backup
kubectl apply -f eai-agent-secrets-backup.yaml
kubectl rollout restart deployment eai-agent
```

## Testing the Integration

1. Update the production deployment with Discord configuration
2. Upload a new prompt version through the admin interface
3. Check your Discord channel for the notification
4. Verify logs show successful notification sending

```bash
# Monitor logs for Discord notifications
kubectl logs -f deployment/eai-agent | grep -E "(Discord|notification)"
```
