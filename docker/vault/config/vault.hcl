# =============================================================================
# HashiCorp Vault Configuration (Development Mode)
# =============================================================================
# This configuration is for development/testing purposes only.
# For production, use proper storage backends (Consul, etcd, etc.)
# and enable TLS.
# =============================================================================

# Storage backend - using file storage for development
storage "file" {
  path = "/vault/data"
}

# Listener configuration
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true  # Only for development!
}

# API address
api_addr = "http://127.0.0.1:8200"

# Disable mlock for development (container environments)
disable_mlock = true

# UI is enabled
ui = true

# =============================================================================
# Secret Engine Paths (configured at runtime)
# =============================================================================
# After Vault starts, configure secret engines:
#
#   vault secrets enable -path=secret kv-v2
#   vault kv put secret/mlops/api-keys openai=sk-xxx anthropic=sk-yyy
#   vault kv put secret/mlops/storage b2_key_id=xxx b2_key=yyy
#
# =============================================================================
