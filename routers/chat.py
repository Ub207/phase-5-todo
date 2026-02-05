# routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import logging
import json
import os

from openai import AsyncOpenAI
from auth_utils import get_current_user, get_db
from models import User, Task
from datetime import datetime

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set, AI chat will not work")
    openai_client = None
else:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    conversation_id: int = None
    tool_calls: List[Dict[str, Any]] = []

# MCP Tool definitions for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new todo task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"}
                },
                "required": ["task_id"]
            }
        }
    }
]

# Conversation history (in-memory)
conversations: Dict[int, List[Dict[str, str]]] = {}

async def execute_tool_call(tool_name: str, arguments: dict, user: User, db: Session) -> dict:
    """Execute tool calls and interact with database"""
    try:
        if tool_name == "add_task":
            # Create new task
            new_task = Task(
                title=arguments.get("title"),
                description=arguments.get("description"),
                user_id=user.id,
                completed=False
            )
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            return {
                "success": True,
                "task": {
                    "id": new_task.id,
                    "title": new_task.title,
                    "description": new_task.description
                }
            }

        elif tool_name == "list_tasks":
            # List tasks
            query = db.query(Task).filter(Task.user_id == user.id)
            status = arguments.get("status", "all")

            if status == "pending":
                query = query.filter(Task.completed == False)
            elif status == "completed":
                query = query.filter(Task.completed == True)

            tasks = query.order_by(Task.created_at.desc()).all()
            return {
                "success": True,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "completed": t.completed,
                        "created_at": t.created_at.isoformat() if t.created_at else None
                    }
                    for t in tasks
                ]
            }

        elif tool_name == "complete_task":
            # Complete task
            task_id = arguments.get("task_id")
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user.id
            ).first()

            if not task:
                return {"success": False, "error": "Task not found"}

            task.completed = True
            task.completed_at = datetime.utcnow()
            db.commit()
            return {"success": True, "task_id": task_id}

        elif tool_name == "delete_task":
            # Delete task
            task_id = arguments.get("task_id")
            task = db.query(Task).filter(
                Task.id == task_id,
                Task.user_id == user.id
            ).first()

            if not task:
                return {"success": False, "error": "Task not found"}

            db.delete(task)
            db.commit()
            return {"success": True, "task_id": task_id}

        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        db.rollback()
        return {"success": False, "error": str(e)}

def parse_simple_command(message: str):
    """Parse simple commands without AI"""
    message = message.lower().strip()

    # Add task
    if message.startswith("add "):
        task_name = message[4:].strip()
        return {"action": "add", "task": task_name}

    # Delete task
    if message.startswith("delete ") or message.startswith("remove "):
        task_name = message.split(" ", 1)[1].strip()
        return {"action": "delete", "task": task_name}

    # Show/list tasks
    if message in ["show list", "list", "show tasks", "my tasks", "show"]:
        return {"action": "list"}

    # Complete task
    if message.startswith("complete ") or message.startswith("done "):
        task_name = message.split(" ", 1)[1].strip()
        return {"action": "complete", "task": task_name}

    return None

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle chat messages with or without AI"""

    user_id = current_user.id
    message = request.message

    # Try simple command parsing first (works without OpenAI)
    parsed = parse_simple_command(message)

    if parsed:
        action = parsed["action"]

        if action == "add":
            # Create task
            new_task = Task(
                title=parsed["task"],
                user_id=user_id,
                completed=False
            )
            db.add(new_task)
            db.commit()
            return ChatResponse(reply=f"✅ Added: {parsed['task']}", tool_calls=[])

        elif action == "delete":
            # Find and delete task
            task = db.query(Task).filter(
                Task.user_id == user_id,
                Task.title.ilike(f"%{parsed['task']}%")
            ).first()

            if task:
                db.delete(task)
                db.commit()
                return ChatResponse(reply=f"🗑️ Deleted: {task.title}", tool_calls=[])
            else:
                return ChatResponse(reply=f"❌ Task not found: {parsed['task']}", tool_calls=[])

        elif action == "complete":
            # Find and complete task
            task = db.query(Task).filter(
                Task.user_id == user_id,
                Task.title.ilike(f"%{parsed['task']}%")
            ).first()

            if task:
                task.completed = True
                task.completed_at = datetime.utcnow()
                db.commit()
                return ChatResponse(reply=f"✅ Completed: {task.title}", tool_calls=[])
            else:
                return ChatResponse(reply=f"❌ Task not found: {parsed['task']}", tool_calls=[])

        elif action == "list":
            # List all tasks
            tasks = db.query(Task).filter(Task.user_id == user_id).all()
            if tasks:
                task_list = "\n".join([f"- {t.title} {'✅' if t.completed else '⏳'}" for t in tasks])
                return ChatResponse(reply=f"📝 Your tasks:\n{task_list}", tool_calls=[])
            else:
                return ChatResponse(reply="📭 Your list is empty!", tool_calls=[])

    # If OpenAI is not available, return helpful message
    if not openai_client:
        return ChatResponse(
            reply="💡 Try: 'add [task]', 'delete [task]', 'complete [task]', or 'show list'",
            tool_calls=[]
        )

    # Try AI mode if OpenAI is available
    # Initialize conversation history for user
    if user_id not in conversations:
        conversations[user_id] = []

    conversations[user_id].append({"role": "user", "content": message})

    try:
        # Call OpenAI with function calling
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful todo list assistant. "
                        "When users ask to add tasks, extract ONLY the item name. "
                        "ALWAYS respond in English. "
                        "Keep responses short and friendly."
                    )
                },
                *conversations[user_id]
            ],
            tools=TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls

        if tool_calls:
            # Store assistant message with tool calls
            conversations[user_id].append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                result = await execute_tool_call(tool_name, tool_args, current_user, db)

                conversations[user_id].append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Get final response from AI
            final_response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Summarize what you did in a friendly way. "
                            "ALWAYS respond in English. "
                            "Keep it brief (1 sentence)."
                        )
                    },
                    *conversations[user_id]
                ]
            )

            final_message = final_response.choices[0].message.content
            conversations[user_id].append({"role": "assistant", "content": final_message})

            return ChatResponse(reply=final_message, tool_calls=[])

        else:
            # No tool calls, just conversation
            conversations[user_id].append({
                "role": "assistant",
                "content": assistant_message.content
            })

            return ChatResponse(reply=assistant_message.content, tool_calls=[])

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return ChatResponse(
            reply="Sorry, I encountered an error. Please try again.",
            tool_calls=[]
        )

@router.get("/chat/history")
async def get_chat_history(current_user: User = Depends(get_current_user)):
    """Get chat history for current user"""
    return {"messages": conversations.get(current_user.id, [])}

@router.delete("/chat/history")
async def clear_chat_history(current_user: User = Depends(get_current_user)):
    """Clear chat history for current user"""
    if current_user.id in conversations:
        conversations[current_user.id] = []
    return {"message": "Chat history cleared"}
