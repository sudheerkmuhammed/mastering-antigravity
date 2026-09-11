"""
WhatsApp Cloud API Gateway for Google Antigravity.
Receives inbound Meta webhook events, dispatches them to an Antigravity agent,
and replies directly back to WhatsApp.
"""

import os
import httpx
from fastapi import FastAPI, Request, Query, Response
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

app = FastAPI(title="Antigravity WhatsApp Gateway")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "mock_token")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_ID", "mock_phone_id")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "antigravity_verify_token")


@app.get("/webhook")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge"),
):
    """Meta webhook handshake verification endpoint."""
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(status_code=403, content="Forbidden: Verification Token Mismatch")


@app.post("/webhook")
async def handle_whatsapp_message(request: Request):
    """Handles incoming WhatsApp messages and dispatches to Antigravity."""
    payload = await request.json()

    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "no_messages"}

        user_message = messages[0].get("text", {}).get("body", "")
        sender_phone = messages[0].get("from", "")

        if not user_message or not sender_phone:
            return {"status": "empty_payload"}

        print(f"[*] Inbound WhatsApp message from {sender_phone}: {user_message}")

        # Initialize Antigravity Local Agent
        config = LocalAgentConfig(
            workspace_dir=os.getcwd(),
            system_instructions=(
                "You are an on-call DevOps and Software Engineering assistant "
                "interfaced via WhatsApp. Keep responses clear, concise, and structured."
            ),
            capabilities=CapabilitiesConfig(
                allow_file_modifications=True,
                allow_terminal_execution=True,
                allow_internet_access=True,
            ),
        )

        async with Agent(config) as agent:
            response = await agent.chat(user_message)
            full_response = ""
            async for token in response:
                full_response += token

        # Send response back to WhatsApp
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        body = {
            "messaging_product": "whatsapp",
            "to": sender_phone,
            "type": "text",
            "text": {"body": full_response[:4096]},
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=body, headers=headers)
            print(f"[+] WhatsApp message dispatched. Status code: {res.status_code}")

    except Exception as exc:
        print(f"[-] Error processing WhatsApp webhook: {exc}")

    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
