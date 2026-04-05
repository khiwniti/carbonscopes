# Redis Connectivity Fix Plan

## Goal
Fix Redis connectivity to restore agent system functionality from degraded to healthy status.

## Context
- Redis container is running but not accessible from external environment
- Backend shows `Redis ping timed out after 5 seconds`
- Agent system reports `"initialized": false, "checkpointer_connected": false`
- System functional for basic API operations (non-blocking issue)

## Tasks

### Task 1: Diagnose Redis Network Configuration
**Objective**: Identify why Redis container is running but unreachable

**Acceptance Criteria**:
- Redis container network mode identified
- Container port mappings verified
- Network connectivity from backend to Redis confirmed
- Root cause of timeout documented

**Technical Details**:
- Check Docker network configuration for Redis container
- Verify Redis is listening on correct interface (0.0.0.0 vs 127.0.0.1)
- Test connectivity from backend container to Redis container
- Check Azure Container Apps networking (if applicable)

### Task 2: Fix Redis Connection Configuration
**Objective**: Update Redis connection settings to establish connectivity

**Acceptance Criteria**:
- Redis connection string updated with correct host/port
- Connection test succeeds with <1s latency
- Backend logs show successful Redis ping
- No timeout errors in logs

**Technical Details**:
- Update Redis connection URL in backend environment variables
- Ensure Redis password matches (if configured)
- Verify Redis protocol version compatibility
- Test connection before restart

### Task 3: Initialize Agent System Checkpointer
**Objective**: Enable agent system checkpointer once Redis is connected

**Acceptance Criteria**:
- Agent system initializes successfully on backend startup
- Checkpointer connects to Redis
- Health endpoint shows `"initialized": true, "checkpointer_connected": true`
- Agent system status changes from "degraded" to "healthy"

**Technical Details**:
- Verify agent system configuration points to correct Redis instance
- Check checkpointer initialization code for errors
- Validate checkpoint data structure in Redis
- Test agent checkpoint save/restore operations

### Task 4: Verify End-to-End Agent Functionality
**Objective**: Confirm agent system fully operational

**Acceptance Criteria**:
- Create test agent run successfully
- Agent state persists to Redis
- Agent can resume from checkpoint
- No degraded status in health endpoint
- Backend logs clean (no Redis errors)

**Technical Details**:
- Create simple test agent via API
- Trigger checkpoint save
- Simulate restart and verify resume
- Monitor Redis keys for agent state
- Verify cleanup of orphaned agent runs

## Success Criteria
- Health endpoint returns `"status": "healthy"`
- Agent system fully initialized
- Checkpointer connected and functional
- No Redis timeout errors in logs
- Agent runs can be created, checkpointed, and resumed

## Rollback Plan
If Redis fix causes issues:
1. Revert environment variable changes
2. Restart backend to previous revision
3. System remains in current "degraded but functional" state
