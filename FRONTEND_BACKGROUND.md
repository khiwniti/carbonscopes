# 🚀 Running CarbonScope Frontend in Background

**Server:** Next.js 15.5.9 with Turbopack  
**Status:** ✅ Currently running on http://localhost:3000  
**Log File:** `/tmp/carbonscope-frontend.log`

---

## ⚡ Quick Start

### Using the Helper Script (Recommended)

```bash
cd /teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init

# Start server
./start-frontend.sh start

# Check status
./start-frontend.sh status

# Stop server
./start-frontend.sh stop

# Restart server
./start-frontend.sh restart

# View logs (real-time)
./start-frontend.sh logs
```

---

## 📋 Manual Commands

### Start in Background

```bash
cd /teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init
nohup pnpm --filter CarbonScope dev > /tmp/carbonscope-frontend.log 2>&1 &
```

### Check Status

```bash
# See running processes
ps aux | grep "next dev" | grep -v grep

# Check if port 3000 is in use
lsof -i :3000

# Quick test
curl -s http://localhost:3000 > /dev/null && echo "✅ Server responding" || echo "❌ Server not responding"
```

### View Logs

```bash
# Real-time logs (Ctrl+C to exit)
tail -f /tmp/carbonscope-frontend.log

# Last 50 lines
tail -50 /tmp/carbonscope-frontend.log

# Search logs for errors
grep -i "error" /tmp/carbonscope-frontend.log
```

### Stop Server

```bash
# Kill all Next.js dev servers
pkill -9 -f "next dev"

# Kill by port
lsof -ti:3000 | xargs kill -9
```

---

## 🔧 Management Script Reference

### `./start-frontend.sh` Commands

| Command | Description |
|---------|-------------|
| `start` | Start server in background |
| `stop` | Stop all running instances |
| `restart` | Stop and start server |
| `status` | Show server status & PID |
| `logs` | Tail logs in real-time |

### Status Output Example

```bash
$ ./start-frontend.sh status

📊 CarbonScope Frontend Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: 🟢 RUNNING

Processes:
  PID: 627789   Memory: 0.1 MB
  PID: 627790   Memory: 80.5 MB

🌐 URL: http://localhost:3000
📋 Logs: tail -f /tmp/carbonscope-frontend.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🌐 Access URLs

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Local access |
| http://10.128.0.63:3000 | Network access (if needed) |

---

## 📊 Monitoring

### Watch Logs Live

```bash
# Auto-scroll logs
tail -f /tmp/carbonscope-frontend.log

# Filter specific events
tail -f /tmp/carbonscope-frontend.log | grep -E "Compiled|Ready|Error"
```

### Resource Usage

```bash
# Memory usage
ps aux | grep "next dev" | grep -v grep | awk '{sum+=$6} END {print "Total Memory: " sum/1024 " MB"}'

# CPU usage
top -p $(pgrep -f "next dev" | tr '\n' ',')
```

---

## 🐛 Troubleshooting

### Server Won't Start

**Issue:** Port 3000 already in use

```bash
# Find what's using port 3000
lsof -i :3000

# Kill the process
kill -9 $(lsof -ti:3000)

# Then restart
./start-frontend.sh start
```

### Server Crashes

```bash
# Check logs for errors
cat /tmp/carbonscope-frontend.log | grep -i "error"

# Clear cache and restart
cd /teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init/apps/frontend
rm -rf .next .turbopack
cd ../..
./start-frontend.sh restart
```

### Can't Access Server

```bash
# Verify it's running
./start-frontend.sh status

# Test connection
curl -I http://localhost:3000

# Check firewall (if remote)
sudo ufw status
```

---

## 🔄 Automatic Restart on Crash

### Using `systemd` (Production)

Create `/etc/systemd/system/carbonscope.service`:

```ini
[Unit]
Description=CarbonScope Frontend
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init
ExecStart=/usr/bin/pnpm --filter CarbonScope dev
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable carbonscope
sudo systemctl start carbonscope
```

### Using `pm2` (Alternative)

```bash
# Install pm2
npm install -g pm2

# Start with pm2
cd /teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init
pm2 start "pnpm --filter CarbonScope dev" --name carbonscope

# Save pm2 config
pm2 save

# Auto-start on boot
pm2 startup
```

---

## 📁 Log File Locations

| File | Path | Purpose |
|------|------|---------|
| Main log | `/tmp/carbonscope-frontend.log` | All server output |
| Next.js cache | `apps/frontend/.next/` | Build cache |
| Turbopack cache | `apps/frontend/.turbopack/` | Dev server cache |

---

## 🎯 Best Practices

### Development

✅ **DO:**
- Use `./start-frontend.sh` for convenience
- Check status before starting: `./start-frontend.sh status`
- Monitor logs when testing: `tail -f /tmp/carbonscope-frontend.log`
- Clear cache if weird errors: `rm -rf apps/frontend/.next`

❌ **DON'T:**
- Run multiple instances (check with `ps aux | grep "next dev"`)
- Forget to stop server when done (uses memory)
- Ignore errors in logs

### Production

✅ **DO:**
- Use process manager (pm2, systemd)
- Set up log rotation
- Monitor resource usage
- Use reverse proxy (nginx)

---

## 🚀 Performance Tips

### Faster Builds

```bash
# Use SWC minifier (already configured)
# Clear cache if slow
cd apps/frontend
rm -rf .next .turbopack node_modules/.cache

# Reinstall if needed
pnpm install
```

### Memory Optimization

If server uses too much memory:

```bash
# Set Node.js memory limit
NODE_OPTIONS="--max-old-space-size=2048" pnpm --filter CarbonScope dev
```

---

## ✅ Current Status Summary

```
Status:     🟢 RUNNING
URL:        http://localhost:3000
PID:        627789, 627790
Memory:     ~80 MB
Log:        /tmp/carbonscope-frontend.log
Script:     ./start-frontend.sh
```

---

## 📞 Quick Commands Cheat Sheet

```bash
# Start
./start-frontend.sh start

# Status
./start-frontend.sh status

# Logs
tail -f /tmp/carbonscope-frontend.log

# Stop
pkill -9 -f "next dev"

# Restart
./start-frontend.sh restart

# Check port
lsof -i :3000

# Test server
curl http://localhost:3000
```

---

**Last Updated:** March 28, 2026  
**Server Version:** Next.js 15.5.9 (Turbopack)  
**Status:** ✅ Running in background
