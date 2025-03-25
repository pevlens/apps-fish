import logging
from fastapi import FastAPI, Request, HTTPException
from telegram import Bot
from telegram.error import BadRequest
import json
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(os.getenv('VAULT_SECRETS_FILE', '.env'))
API_PORT = int(os.getenv("API_PORT", 5000))
API_KEY = os.getenv("X-API-KEY", "xuixuixuixui")
TOKEN_TG_BOT = os.getenv("TOKEN_TG_BOT", "xuixuwdvxui")
CHANNELID = os.getenv("CHANNEL_ID", "xuixuixuixui")



app = FastAPI()
bot = Bot(token=TOKEN_TG_BOT)

class MessageRequest(BaseModel):
    user_id: int
    message: str

async def validate_api_key(headers):
    """Проверка API ключа"""
    return headers.get("X-API-Key") == API_KEY

@app.post("/send_message")
async def send_message(request: Request):
    """Эндпоинт для отправки сообщений и удаления из канала"""
    if not await validate_api_key(request.headers):
        raise HTTPException(status_code=401, detail="Unauthorized")

    
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    if "user_id" not in data or "message" not in data:
        raise HTTPException(status_code=400, detail="Missing required fields: 'user_id' and 'message'")



    try:
        sent_message = await bot.send_message(
            chat_id=data["user_id"],
            text=data["message"],
            parse_mode="HTML" if data.get("html", False) else None
        )

        if "channel_message_id" in data:
            lst_messages = [ str(x) for x in data["channel_message_id"].split(",")] if data["channel_message_id"] else []
            for del_msg in lst_messages:
                try:
                    await bot.delete_message(
                        chat_id=CHANNELID,
                        message_id= del_msg
                    )
                except BadRequest as e:
                    if "Message can't be deleted" in str(e):
                        print(f"Сообщение {del_msg} уже удалено или недоступно!") 

        return {"status": "success", "sent_message_id": sent_message.message_id}

    except Exception as e:
        logging.exception("API Error")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def check_status(request: Request):
    """Проверка статуса API"""
    if not await validate_api_key(request.headers):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "online", "users_online": "N/A"}

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=int(API_PORT))