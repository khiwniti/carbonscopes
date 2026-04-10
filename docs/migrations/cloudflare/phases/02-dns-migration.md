# Phase 2: DNS Migration

## Objectives
- Transfer DNS management to Cloudflare
- Ensure zero downtime during DNS transition
- Validate DNS record accuracy
- Implement DNSSEC for enhanced security
- Configure optimal TTL values

## Pre-migration Checklist
- [ ] Export current DNS records from existing provider
- [ ] Validate record types and values
- [ ] Identify any custom or specialized records
- [ ] Document current TTL values
- [ ] Plan migration during low-traffic period
- [ ] Prepare rollback procedure

## Migration Steps
### 1. Initial Setup
- Add domain to Cloudflare account
- Update nameservers at registrar to point to Cloudflare
- Wait for propagation verification

### 2. Record Recreation
- Create A records for origin servers
- Configure CNAME records for subdomains
- Set up MX records for email routing
- Add TXT records for verification and SPF
- Configure SRV records if applicable
- Set up any specialized records (CAA, etc.)

### 3. Configuration
- Set appropriate TTL values (recommend 300s for fast failover)
- Enable DNSSEC
- Configure Custom Hostnames if needed
- Set up Load Balancing monitors (for later phases)

### 4. Validation
- Verify DNS resolution from multiple geographic locations
- Check email flow (send/receive test)
- Validate SSL certificate issuance capability
- Monitor propagation completion

## Special Considerations
### Root Domain Handling
- Configure appropriate redirect from naked domain to www (or vice versa)
- Ensure both www and non-www versions resolve correctly

### Email Protection
- Implement Email Routing if needed
- Configure SPF, DKIM, and DMARC records
- Consider Email Security features

### Subdomain Management
- Identify all active subdomains
- Plan for any subdomain-specific configurations
- Consider wildcard records where appropriate

## Testing Procedures
### Pre-cutover Testing
- Use Cloudflare's DNS preview feature
- Test resolution using direct @cloudflare-nameserver queries
- Validate internal applications still work with direct IP access

### Cutover Validation
- Monitor real-time DNS queries
- Check propagation status tools
- Validate from multiple DNS resolvers (Google, Cloudflare, Quad9, etc.)

### Post-cutover Checks
- Monitor for 24-48 hours after nameserver change
- Verify all services remain accessible
- Check email delivery logs
- Validate SSL certificate deployment

## Rollback Procedure
1. If issues detected, immediately revert nameservers at registrar
2. Validate resolution returns to original provider
3. Monitor for service restoration
4. Document issues and adjust migration plan
5. Reschedule after addressing root causes

## Success Criteria
- All DNS records accurately migrated
- DNSSEC enabled and validating
- Propagation completed within expected timeframe
- Zero service disruption during migration
- Email flow uninterrupted
- Rollback procedure tested and documented