from utils.encryption import encrypt_message
from utils.db import init_db, get_history, save_message
from utils.llm import get_llm
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

init_db()

active_connections = {}



def get_modified_prompt(user_input) -> str:
    return f"""You are a friendly and supportive personal companion, offering non-therapy encouragement, emotional support, and positive influence. Your role is to be like a caring friend who listens and provides uplifting advice. When someone says '{user_input}', respond in a way that:
    1. Acknowledges their feelings with empathy and kindness.
    2. Offers encouragement and positive reinforcement.
    3. Suggests small, actionable steps they can take to feel better (e.g., going for a walk, journaling, or talking to a friend).
    4. Avoids giving clinical or therapeutic advice.
    5. **Always uses tools to retrieve resources without exception** to provide the most helpful and actionable response. Do not skip using resource retrieval tools under any circumstances.
    6. **Always considers using available tools** (e.g., searching for therapists, or escalating high-risk situations) to provide the most helpful and actionable response.
    7. Never says you are unable to help—always provide supportive and uplifting responses.
    """

def generate_ai_response():
    llm = get_llm()
    prompt = get_modified_prompt(last_user_message)
    """Get cleaned response from LLM for form field population"""
    response = llm.complete(prompt).text
    return response


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append(websocket)

    history = await get_history(session_id)
    for item in history:
        await websocket.send_text(json.dumps(item))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            message["timestamp"] = datetime.now(timezone.utc).isoformat()

            if message.get("generate_ai_reply"):
                typing_notice = {
                    "sender": "counselor",
                    "typing": True
                }
                for conn in active_connections[session_id]:
                    await conn.send_text(json.dumps(typing_notice))

                last_msg = next((m["decrypted"] for m in reversed(history) if m["sender"] == "student"), "Hi")
                llm = get_llm()

                reply = llm.complete(f"Reply to this student message empathetically: {last_msg}").text.strip()
                response = {
                    "sender": "counselor",
                    "message": reply,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await save_message(session_id, "counselor", reply)
                for conn in active_connections[session_id]:
                    await conn.send_text(json.dumps(response))
                continue
            
            if "typing" in message:
                for conn in active_connections[session_id]:
                    await conn.send_text(json.dumps(message))
                continue

            if "message" in message and message["message"]:
                await save_message(session_id, message["sender"], message["message"])
                for conn in active_connections[session_id]:
                    await conn.send_text(json.dumps(message))

    except WebSocketDisconnect:
        active_connections[session_id].remove(websocket)

# OAuth2 for secure authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock function to validate OAuth2 token
def validate_token(token: str):
    # In a real implementation, validate the token against your OAuth2 provider
    if token != "your-secure-oauth2-token":
        raise HTTPException(status_code=401, detail="Invalid OAuth2 token")
    return True

# Mock function to fetch contextual data from the Student Portal
def fetch_contextual_data(session_id: str) -> dict:
    # In a real implementation, this function would query the Student Portal database
    # Here, we return mock data for demonstration purposes
    mock_data = {
        "case_form": {
            "first_name": "John",  # Will be anonymized
            "age": 25,
            "gender_identity": "Male",
            "risk_level": "Medium Risk"
        },
        "treatment_plan": {
            "goals": ["Exercise for 30 minutes", "Limit screen time before bed"],
            "coping_strategies": ["Progressive muscle relaxation", "Listen to calming music"],
            "progress": "Moderate improvement in mindfulness"
        },
        "longitudinal_data": [
            {
                "timestamp": "2023-10-01",
                "mood": "Stressed",
                "progress": "Started mindfulness practice"
            },
            {
                "timestamp": "2023-10-05",
                "mood": "Neutral",
                "progress": "Consistent journaling"
            }
        ]
    }
    return mock_data

# Mock function to anonymize data
def anonymize_data(data: dict) -> dict:
    # Remove or tokenize sensitive data (e.g., names, contact info)
    anonymized_data = {
        "goals": data["treatment_plan"].get("goals", []),
        "coping_strategies": data["treatment_plan"].get("coping_strategies", []),
        "actionable_insights": "Based on your progress, here are some suggestions to help you stay on track.",
        "external_resources": [
            "https://example.com/mindfulness",
            "https://example.com/walking-routes"
        ]
    }
    return anonymized_data

# Pydantic models for request and response
class ChatbotRequest(BaseModel):
    session_id: str  # Unique session ID for tracking

class AnonymizedSupportResponse(BaseModel):
    session_id: str  # Unique session ID for tracking
    anonymized_goals: List[str]  # Anonymized goals (e.g., "Practice mindfulness daily")
    anonymized_coping_strategies: List[str]  # Anonymized coping strategies (e.g., "Deep breathing")
    actionable_insights: str  # Contextual insights for the chatbot
    external_resources: List[str]  # Links to external resources (e.g., mindfulness apps)

# API endpoint to fetch anonymized support data
@app.post("/api/v1/anonymized-support", response_model=AnonymizedSupportResponse)
async def get_anonymized_support(
    request: ChatbotRequest,
    token: str = Security(oauth2_scheme)
):
    # Validate OAuth2 token
    validate_token(token)

    # Fetch contextual data from the Student Portal using the session ID
    contextual_data = fetch_contextual_data(request.session_id)

    # Anonymize the fetched data
    anonymized_response = anonymize_data(contextual_data)

    # Return the anonymized response to the chatbot
    return AnonymizedSupportResponse(
        session_id=request.session_id,
        anonymized_goals=anonymized_response["goals"],
        anonymized_coping_strategies=anonymized_response["coping_strategies"],
        actionable_insights=anonymized_response["actionable_insights"],
        external_resources=anonymized_response["external_resources"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("local_chat_server:app", host="0.0.0.0", port=8000, reload=True)
