#!/bin/bash

# Generate self-signed SSL certificate for localhost development
cd /Users/christian/Repos/f.insight.AI\ Advanced/backend

echo "Generating self-signed SSL certificate for localhost..."

# Create SSL directory
mkdir -p ssl

# Generate private key
openssl genrsa -out ssl/key.pem 2048

# Generate certificate signing request
openssl req -new -key ssl/key.pem -out ssl/cert.csr -subj "/C=US/ST=CA/L=San Francisco/O=FInsightAI/OU=Development/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem -days 365

echo "SSL certificate generated successfully!"
echo "Files created:"
echo "  - ssl/key.pem (private key)"
echo "  - ssl/cert.pem (certificate)"
echo "  - ssl/cert.csr (certificate signing request)"
