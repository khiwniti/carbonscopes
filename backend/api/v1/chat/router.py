"""Chat API endpoints - natural language prompts that trigger agent/computer-use flows."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from core.utils.auth_utils import verify_and_get_user_id_from_jwt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    prompt: str
    thread_id: Optional[str] = None
    agent_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    status: str
    thread_id: Optional[str] = None
    agent_run_id: Optional[str] = None


@router.post("", response_model=ChatResponse, summary="Chat Prompt", operation_id="chat_prompt")
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(verify_and_get_user_id_from_jwt),
):
    """
    Accept a natural language prompt and start an agent run.

    This is the primary entry point for computer-use interactions.
    It creates a thread (or reuses an existing one) and kicks off
    an agent run that can execute computer-use tasks.
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        from core.services.supabase import DBConnection
        from core.agents import repo as agents_repo
        from core.threads import repo as threads_repo
        from core.agents.runner import execute_agent_run
        from core.ai_models import model_manager
        import uuid

        db = DBConnection()
        client = await db.client

        # 1. Resolve or create thread
        thread_id = request.thread_id
        if not thread_id:
            result = await threads_repo.create_new_thread_with_project(
                user_id, "Chat Session"
            )
            thread_id = result["thread_id"]
            project_id = result["project_id"]
        else:
            thread_data = await threads_repo.get_thread_with_project(thread_id)
            if not thread_data:
                raise HTTPException(status_code=404, detail="Thread not found")
            project_id = thread_data["project_id"]

        # 2. Resolve model
        model_name = await model_manager.get_default_model_for_user(client, user_id)

        # 3. Create and start agent run
        agent_run_id = str(uuid.uuid4())
        await execute_agent_run(
            agent_run_id=agent_run_id,
            thread_id=thread_id,
            account_id=user_id,
            prompt=request.prompt.strip(),
            model_name=model_name,
        )

        return ChatResponse(
            response="Agent run started successfully.",
            status="started",
            thread_id=thread_id,
            agent_run_id=agent_run_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"chat_endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
