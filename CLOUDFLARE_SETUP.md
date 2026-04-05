# Cloudflare DNS Setup for carbonscope.ensimu.space

**Date:** March 28, 2026  
**Domain:** carbonscope.ensimu.space  

---

## 🎯 Quick Setup (5 Minutes)

### Step 1: Login to Cloudflare

1. Visit: https://dash.cloudflare.com
2. Login with your credentials
3. Select domain: **ensimu.space**

### Step 2: Add DNS Record

Navigate to: **DNS** → **Records**

Click **Add record** and enter:

| Field | Value |
|-------|-------|
| **Type** | A |
| **Name** | carbonscope |
| **IPv4 address** | `YOUR_VM_IP` |
| **Proxy status** | ☁️ Proxied (orange cloud ON) |
| **TTL** | Auto |

Click **Save**

### Step 3: SSL/TLS Configuration

Navigate to: **SSL/TLS** → **Overview**

Set encryption mode:
- ✅ **Full** (or Full (strict) if you have origin certificate)

### Step 4: Enable Security Features

Navigate to: **SSL/TLS** → **Edge Certificates**

Enable these settings:
- ✅ **Always Use HTTPS** - Force HTTPS
- ✅ **Automatic HTTPS Rewrites** - Fix mixed content
- ✅ **Minimum TLS Version** - 1.2 or higher
- ✅ **Opportunistic Encryption** - Enable
- ✅ **TLS 1.3** - Enable

### Step 5: Performance Optimization

Navigate to: **Speed** → **Optimization**

Enable:
- ✅ **Auto Minify** - JavaScript, CSS, HTML
- ✅ **Brotli** - Compression
- ✅ **Early Hints** - Faster page loads

Navigate to: **Caching** → **Configuration**

- **Browser Cache TTL:** 4 hours
- **Caching Level:** Standard

---

## 🔐 Optional: Origin Certificate (Recommended)

For end-to-end encryption between Cloudflare and your VM:

### Step 1: Create Origin Certificate

1. Navigate to: **SSL/TLS** → **Origin Server**
2. Click **Create Certificate**
3. Leave default settings:
   - Private key type: RSA (2048)
   - Hostnames: `*.ensimu.space, ensimu.space`
   - Certificate Validity: 15 years
4. Click **Create**

### Step 2: Save Certificates

Copy both:
- **Origin Certificate** (long text block)
- **Private Key** (long text block)

### Step 3: Install on VM

SSH into your VM:

```bash
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP

# Create SSL directory
mkdir -p ~/carbonscope/nginx/ssl

# Create certificate file
cat > ~/carbonscope/nginx/ssl/cert.pem << 'EOF'
[Paste Origin Certificate here]
EOF

# Create private key file
cat > ~/carbonscope/nginx/ssl/key.pem << 'EOF'
[Paste Private Key here]
EOF

# Set permissions
chmod 600 ~/carbonscope/nginx/ssl/key.pem
chmod 644 ~/carbonscope/nginx/ssl/cert.pem
```

### Step 4: Update Nginx Config

Edit nginx configuration:

```bash
nano ~/carbonscope/nginx/nginx.conf
```

Add SSL configuration to the server block:

```nginx
server {
    listen 443 ssl http2;
    server_name carbonscope.ensimu.space;

    # Cloudflare Origin Certificate
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

    # Rest of your config...
}
```

Update docker-compose.yml to mount SSL:

```yaml
nginx:
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/ssl:/etc/nginx/ssl:ro  # Add this line
```

Restart:

```bash
docker-compose restart nginx
```

### Step 5: Update SSL Mode

Back in Cloudflare:
- Navigate to: **SSL/TLS** → **Overview**
- Change encryption mode to: **Full (strict)**

---

## 🛡️ Security Rules

### Firewall Rules (Optional)

Navigate to: **Security** → **WAF**

Add rules to:
- Block traffic from certain countries
- Rate limit requests
- Challenge suspicious traffic

Example rule:
- **If:** Request rate > 100 req/min from same IP
- **Then:** Challenge

### Page Rules (Optional)

Navigate to: **Rules** → **Page Rules**

Example:
- **URL:** `carbonscope.ensimu.space/*`
- **Settings:**
  - Cache Level: Standard
  - Browser Cache TTL: 4 hours
  - Always Online: On

---

## 🚀 Performance Tuning

### Enable Argo Smart Routing (Paid)

Speeds up dynamic content by 30%
- Navigate to: **Speed** → **Optimization**
- Enable **Argo Smart Routing** ($5/month base + $0.10/GB)

### Enable Image Optimization

- Navigate to: **Speed** → **Optimization**
- Enable **Polish** - Optimize images
- Enable **Mirage** - Lazy load images

---

## ✅ Verification

### DNS Propagation Check

```bash
# Check DNS resolution
dig carbonscope.ensimu.space

# Check if Cloudflare is active (should show Cloudflare IPs)
dig carbonscope.ensimu.space +short
```

### SSL Check

```bash
# Test HTTPS
curl -I https://carbonscope.ensimu.space

# Check SSL certificate
openssl s_client -connect carbonscope.ensimu.space:443 -servername carbonscope.ensimu.space
```

### Website Test

Visit these tools:
- **SSL Test:** https://www.ssllabs.com/ssltest/analyze.html?d=carbonscope.ensimu.space
- **DNS Check:** https://dnschecker.org/#A/carbonscope.ensimu.space
- **Speed Test:** https://www.webpagetest.org

---

## 🐛 Troubleshooting

### Issue: DNS not resolving

**Solution:**
- Wait 5-10 minutes for DNS propagation
- Check Cloudflare DNS records are correct
- Verify proxy status is enabled (orange cloud)

### Issue: SSL certificate errors

**Solution:**
- Ensure SSL mode is set to "Full" or "Full (strict)"
- If using origin certificate, verify it's installed correctly
- Check certificate hasn't expired

### Issue: Too many redirects

**Solution:**
- In Cloudflare: SSL/TLS → Overview → Set to "Full"
- In Nginx: Ensure you're not redirecting HTTPS to HTTPS

### Issue: Mixed content warnings

**Solution:**
- Enable "Automatic HTTPS Rewrites" in Cloudflare
- Update all resource URLs to use HTTPS

---

## 📊 Monitoring

### Analytics

Navigate to: **Analytics & Logs**

View:
- Traffic patterns
- Bandwidth usage
- Requests blocked
- Cache performance

### Email Alerts

Navigate to: **Notifications**

Set up alerts for:
- SSL certificate expiration
- High traffic
- Security events

---

## 🎯 Summary Checklist

Before going live:

- [ ] DNS A record added (carbonscope → VM IP)
- [ ] Proxy enabled (orange cloud)
- [ ] SSL/TLS set to "Full"
- [ ] Always Use HTTPS enabled
- [ ] TLS 1.2+ minimum version
- [ ] Auto Minify enabled
- [ ] DNS propagation complete (10-15 min)
- [ ] HTTPS working: https://carbonscope.ensimu.space
- [ ] HTTP redirects to HTTPS
- [ ] No SSL errors

Optional enhancements:

- [ ] Origin certificate installed
- [ ] Firewall rules configured
- [ ] Page rules set up
- [ ] Analytics reviewed
- [ ] Email alerts configured

---

## 📖 Cloudflare Resources

- **Dashboard:** https://dash.cloudflare.com
- **Documentation:** https://developers.cloudflare.com
- **Community:** https://community.cloudflare.com
- **Status:** https://www.cloudflarestatus.com

---

**Ready?** After completing this setup, your site will be accessible at:
**https://carbonscope.ensimu.space** 🚀
