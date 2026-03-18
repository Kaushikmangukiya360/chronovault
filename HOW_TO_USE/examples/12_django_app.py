"""Django integration sketch using chronovault backend."""

# settings.py
DATABASES = {
    "default": {
        "ENGINE": "chronovault.integrations.django",
        "TOKEN": "your-token",
        "ORG_ID": "acme-corp",
        "BASE_PATH": "/var/lib/chronovault",
    }
}

# In your Django view/serializer layer, use model APIs as usual once backend is enabled.
