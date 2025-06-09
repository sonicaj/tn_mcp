# Certificate Plugin

## Overview
The certificate plugin manages SSL/TLS certificates, certificate authorities, and certificate signing requests for TrueNAS. It provides a complete PKI (Public Key Infrastructure) solution for system services and user applications.

## Architecture

### Service Structure
- **CertificateService** (CRUDService) - Main certificate management
- **CertificateAuthorityService** (CRUDService) - CA management  
- **CertificateSigningRequestService** - CSR handling
- **ACMEService** - Let's Encrypt integration

### Storage
- Certificates stored in system database
- Private keys encrypted at rest
- Automatic backup with system config

## Core Concepts

### Certificate Types
1. **Self-Signed**: Generated locally
2. **CA-Signed**: Signed by internal CA
3. **CSR**: For external signing
4. **ACME**: Let's Encrypt automated
5. **Imported**: User-provided certificates

### Certificate Components
- **Certificate**: Public certificate (PEM format)
- **Private Key**: RSA/EC private key
- **Chain**: Intermediate certificates
- **Root CA**: Certificate authority

## Key Methods

### Certificate Operations
- `certificate.create` - Generate new certificate
- `certificate.import` - Import existing cert
- `certificate.export` - Export with private key
- `certificate.renew` - Renew expiring cert

### CA Operations  
- `certificateauthority.create` - Create new CA
- `certificateauthority.sign` - Sign CSRs
- `certificateauthority.export` - Export CA bundle

### ACME Operations
- `acme.register` - Register account
- `acme.issue` - Get Let's Encrypt cert
- `acme.renew` - Auto-renewal setup

## Common Patterns

### Certificate Generation
```python
# Pattern for creating certificates
@api_method(CertificateCreateArgs, CertificateCreateResult)
async def do_create(self, data):
    # Validate cert type and parameters
    # Generate key pair if needed
    # Create certificate based on type
    # Store in database
    # Return certificate entry
```

### Validation Pattern
- Check key/cert matching
- Verify certificate chain
- Validate expiration dates
- Ensure required fields

### Usage Tracking
Services register certificate usage:
- Web UI (nginx)
- API (middleware)
- FTP service
- Mail service
- Custom applications

## Integration Points

### System Services
- **Web UI**: Uses system certificate
- **API**: TLS configuration
- **FTP**: Explicit/Implicit TLS
- **Mail**: SMTP TLS

### Storage Services
- **S3**: Object storage certificates
- **WebDAV**: HTTPS certificates
- **iSCSI**: CHAP authentication

### Directory Services
- **LDAP**: TLS certificates
- **Active Directory**: Machine certificates

## API Patterns

### Certificate Creation
- Support multiple key types (RSA, EC)
- Configurable key sizes
- Subject alternative names
- Extended key usage

### Import Validation
- Parse certificate format
- Extract metadata
- Verify private key
- Check certificate chain

## Security Considerations

### Private Key Protection
- Encrypted storage
- Restricted permissions
- No key in API responses
- Secure export options

### Certificate Validation
- Chain verification
- Revocation checking
- Expiration monitoring
- Trust store management

## Testing Approach

### Unit Tests
- Certificate generation
- Format parsing
- Chain validation
- Key matching

### Integration Tests
- Service certificate updates
- ACME workflow
- CA operations
- Import/export cycles

## Troubleshooting

### Common Issues

1. **Certificate Mismatch**
   - Verify key matches certificate
   - Check intermediate chain
   - Validate certificate format

2. **ACME Failures**
   - DNS resolution
   - Port 80 accessibility  
   - Account registration

3. **Service Not Using Cert**
   - Check service configuration
   - Restart required services
   - Verify certificate assignment

### Debug Tools
- `certificate.get_service_usages` - Where cert is used
- `certificate.validate` - Check certificate validity
- `certificate.chain_validate` - Verify chain
- `acme.debug` - ACME troubleshooting

## Best Practices

### Certificate Management
1. Use descriptive names
2. Set renewal reminders
3. Keep backups of certificates
4. Monitor expiration dates

### Security
1. Use strong key sizes (2048+ RSA)
2. Prefer EC keys for performance
3. Regularly rotate certificates
4. Limit wildcard usage

### ACME/Let's Encrypt
1. Use DNS validation for wildcards
2. Set up automatic renewal
3. Monitor renewal status
4. Have fallback certificates