# Production-ready Dockerfile using pre-built Next.js standalone output
FROM node:20-alpine AS runner

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy pre-built standalone output (paths from project root context)
COPY --chown=nextjs:nodejs carbonscope-init/apps/frontend/.next/standalone /app
COPY --chown=nextjs:nodejs carbonscope-init/apps/frontend/.next/static /app/carbonscope-init/apps/frontend/.next/static
COPY --chown=nextjs:nodejs carbonscope-init/apps/frontend/public /app/carbonscope-init/apps/frontend/public

# Set working directory to where server.js is located (monorepo structure)
WORKDIR /app/carbonscope-init/apps/frontend

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "server.js"]
