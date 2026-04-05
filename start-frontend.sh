#!/bin/bash

# CarbonScope Frontend Server Manager
# Usage: ./start-frontend.sh [start|stop|restart|status|logs]

LOG_FILE="/tmp/carbonscope-frontend.log"
PROJECT_DIR="/teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init"

case "$1" in
    start)
        echo "🚀 Starting CarbonScope frontend..."
        cd "$PROJECT_DIR"
        
        # Check if already running
        if ps aux | grep "next dev" | grep -v grep > /dev/null; then
            echo "⚠️  Server already running!"
            echo "Run './start-frontend.sh status' to see details"
            exit 1
        fi
        
        # Start in background
        nohup pnpm --filter CarbonScope dev > "$LOG_FILE" 2>&1 &
        
        echo "⏳ Waiting for server to start..."
        sleep 8
        
        if ps aux | grep "next dev" | grep -v grep > /dev/null; then
            echo "✅ Server started successfully!"
            echo "🌐 URL: http://localhost:3000"
            echo "📋 Logs: $LOG_FILE"
        else
            echo "❌ Failed to start server"
            echo "Check logs: cat $LOG_FILE"
            exit 1
        fi
        ;;
        
    stop)
        echo "🛑 Stopping CarbonScope frontend..."
        pkill -9 -f "next dev" 2>/dev/null
        sleep 2
        
        if ! ps aux | grep "next dev" | grep -v grep > /dev/null; then
            echo "✅ Server stopped"
        else
            echo "⚠️  Some processes may still be running"
        fi
        ;;
        
    restart)
        echo "🔄 Restarting CarbonScope frontend..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        echo "📊 CarbonScope Frontend Status"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        if ps aux | grep "next dev" | grep -v grep > /dev/null; then
            echo "Status: 🟢 RUNNING"
            echo ""
            echo "Processes:"
            ps aux | grep "next dev" | grep -v grep | awk '{printf "  PID: %-8s Memory: %.1f MB\n", $2, $6/1024}'
            echo ""
            echo "🌐 URL: http://localhost:3000"
            echo "📋 Logs: tail -f $LOG_FILE"
        else
            echo "Status: 🔴 STOPPED"
            echo ""
            echo "Start with: ./start-frontend.sh start"
        fi
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ;;
        
    logs)
        if [ -f "$LOG_FILE" ]; then
            echo "📋 Tailing logs (Ctrl+C to exit)..."
            tail -f "$LOG_FILE"
        else
            echo "❌ Log file not found: $LOG_FILE"
        fi
        ;;
        
    *)
        echo "CarbonScope Frontend Server Manager"
        echo ""
        echo "Usage: ./start-frontend.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start    - Start the frontend server in background"
        echo "  stop     - Stop the frontend server"
        echo "  restart  - Restart the frontend server"
        echo "  status   - Check server status"
        echo "  logs     - View real-time logs"
        echo ""
        echo "Examples:"
        echo "  ./start-frontend.sh start"
        echo "  ./start-frontend.sh status"
        echo "  tail -f /tmp/carbonscope-frontend.log"
        ;;
esac
