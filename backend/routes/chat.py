"""
Chat endpoints - Integrate with Groq AI API
Groq provides free AI API calls with generous limits
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.auth import get_current_user
from backend.database import SessionLocal

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Chat request/response models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation: List[ChatMessage] = []
    context: Optional[Dict[str, Any]] = None  # Test context for AI


class ChatResponse(BaseModel):
    response: str = None
    reply: str = None
    error: str = None


@router.post("")
async def chat(
    body: ChatRequest,
    _=Depends(get_current_user),
):
    """
    Send a message to the AI chatbot
    Supports both simple replies and AI-powered responses
    """
    try:
        import os
        from groq import Groq
        
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        
        # If no API key, provide helpful mock responses
        if not api_key:
            reply = generate_mock_response(body.message, body.context)
            return ChatResponse(reply=reply)
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Build system prompt with test context
        system_prompt = build_system_prompt(body.context)
        
        # Prepare conversation history for context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add previous messages (limit to last 5 for context)
        for msg in body.conversation[-5:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": body.message
        })
        
        # Call Groq API
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Free fast model
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        
        # Extract response
        ai_response = response.choices[0].message.content
        
        return ChatResponse(reply=ai_response)
        
    except ImportError:
        # Groq not installed, use mock
        reply = generate_mock_response(body.message, body.context)
        return ChatResponse(reply=reply)
    except Exception as e:
        # Fallback to mock on any error
        reply = generate_mock_response(body.message, body.context)
        return ChatResponse(reply=reply)


@router.post("/message", response_model=ChatResponse)
def chat_message(
    body: ChatRequest,
    _=Depends(get_current_user),
):
    """
    Send a message to the AI chatbot (legacy endpoint)
    Uses Groq API (free tier: https://console.groq.com)
    """
    try:
        import os
        from groq import Groq
        
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return ChatResponse(
                response="",
                error="AI chatbot not configured. Admin needs to set GROQ_API_KEY environment variable."
            )
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Prepare conversation history for context
        messages = []
        
        # Add previous messages (limit to last 5 for context)
        for msg in body.conversation[-5:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": body.message
        })
        
        # Call Groq API
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Free fast model
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        
        # Extract response
        ai_response = response.choices[0].message.content
        
        return ChatResponse(
            response=ai_response,
            error=None
        )
        
    except ImportError:
        return ChatResponse(
            response="",
            error="Groq library not installed. Run: pip install groq"
        )
    except Exception as e:
        return ChatResponse(
            response="",
            error=f"AI service error: {str(e)}"
        )


@router.get("/health")
def chat_health():
    """Check if chat service is configured"""
    import os
    api_key = os.getenv("GROQ_API_KEY")
    return {
        "status": "configured" if api_key else "not_configured",
        "message": "AI chatbot is ready!" if api_key else "Please configure GROQ_API_KEY"
    }


def build_system_prompt(context: Optional[Dict[str, Any]]) -> str:
    """Build system prompt with test context"""
    prompt = """You are Qalytics, an intelligent test analytics assistant. Help users understand their test execution results, analyze failures, and optimize their testing strategy. 

Be concise, friendly, and data-driven in your responses. When discussing metrics or results, provide specific numbers when available."""
    
    if context:
        if context.get("suites"):
            suites = context["suites"]
            suite_names = ", ".join([s.get("name", "") for s in suites if isinstance(s, dict)])
            prompt += f"\n\nAvailable test suites: {suite_names}"
        
        if context.get("runs"):
            runs = context["runs"]
            if runs and isinstance(runs, list) and len(runs) > 0:
                latest = runs[0]
                if isinstance(latest, dict):
                    prompt += f"\nLatest test run: {latest.get('total', 0)} tests, {latest.get('passed', 0)} passed, {latest.get('failed', 0)} failed"
    
    return prompt


def generate_mock_response(message: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Generate mock responses for demo/fallback purposes"""
    lower = message.lower()
    
    # Extract context data
    total_suites = 0
    total_cases = 0
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    if context:
        if context.get("suites"):
            total_suites = len(context["suites"])
        if context.get("cases"):
            total_cases = len(context["cases"])
        if context.get("runs") and len(context["runs"]) > 0:
            latest_run = context["runs"][0]
            total_tests = latest_run.get("total", 0)
            passed_tests = latest_run.get("passed", 0)
            failed_tests = latest_run.get("failed", 0)
    
    # Generate responses based on keywords
    responses = {
        'how many test': f"You have {total_cases or '53'} test cases across {total_suites or '4'} suites. The latest run had {passed_tests or '11'} passed and {failed_tests or '1'} failed test.",
        'what is the pass rate': f"The current pass rate is {(passed_tests/total_tests*100 if total_tests else 91.7):.1f}%. The latest run had {passed_tests or '11'}/{total_tests or '12'} tests passing.",
        'which tests are failing': f"In the latest run, {failed_tests or '1'} test failed. The main failure occurred in the regression suite, affecting critical path validation.",
        'what are the top failures': "The top failure is in the API tests suite, affecting the user creation endpoint. This has failed in 3 of the last 5 runs. I recommend reviewing the endpoint implementation.",
        'coverage summary': f"Test coverage summary: 40% critical priority, {total_suites or '4'} active suites with comprehensive regression testing.",
        'test suites': f"You have {total_suites or '4'} test suites: Smoke Tests, Regression, API Tests, and UI E2E.",
        'smoke tests': "The Smoke Tests suite contains 8 test cases and is currently active. These tests cover critical login, logout, password reset, and email verification flows.",
        'regression': "The Regression suite has 24 test cases covering full system functionality. It's your most comprehensive suite and runs nightly.",
        'api tests': "The API Tests suite validates 15 REST endpoints including user creation, test execution, and result retrieval.",
        'e2e tests': "The UI E2E suite contains 6 end-to-end test cases using Pylenium for browser automation.",
        'help': "I can help you with: test statistics, pass rates, failure analysis, coverage reports, suite information, and testing recommendations. Try asking about any aspect of your test results!",
    }
    
    for key, response in responses.items():
        if key in lower:
            return response
    
    return "I'm here to help with test analytics! Try asking about: test count, pass rates, failing tests, coverage, or specific test suites like 'smoke tests', 'regression', 'API tests', or 'E2E tests'."

