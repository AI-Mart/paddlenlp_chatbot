# -*- coding: utf-8 -*-
"""
@Author  :Mart
@Time    :2021/7/8 21:25
@version :Python3.7.4
@Software:pycharm2020.3.2
"""
import time
import os
import asyncio
from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
)
from wechaty_puppet import MessageType
from interaction_chat import PlatoNlp

hello_dict = {'7:30': '上午好', '12:00': '中午好', '18:00': '晚上好'}

os.environ['WECHATY_PUPPET'] = "wechaty-puppet-service"
os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = "puppet_padlocal_xxx"

model = PlatoNlp(max_turn=10)  # Dialogue round configuration


async def on_message(msg: Message):
    """
    Message Handler for the Bot
    """
    time_now = time.strftime('%H:%M')
    if time_now in hello_dict and msg.room().payload.topic == '可爱的一家人':
        await msg.say(hello_dict[time_now])
    if not msg.is_self() and isinstance(msg.text(), str) and len(msg.text()) > 0 and \
            msg._payload.type == MessageType.MESSAGE_TYPE_TEXT:
        if '@' in msg.text():
            if '@哚哚棒' in msg.text():
                bot_response = model.predict(data=msg.text().replace('@哚哚棒', ''))
                await msg.say(bot_response)
        else:
            bot_response = model.predict(data=msg.text())
            await msg.say(bot_response)


async def on_scan(
        qrcode: str,
        status: ScanStatus,
        _data,
):
    """
    Scan Handler for the Bot
    """
    print('Status: ' + str(status))
    print('View QR Code Online: https://wechaty.js.org/qrcode/' + qrcode)


async def on_login(user: Contact):
    """
    Login Handler for the Bot
    """
    print(user)
    # TODO: To be written


async def main():
    """
    Async Main Entry
    """
    #
    # Make sure we have set WECHATY_PUPPET_SERVICE_TOKEN in the environment variables.
    #
    if 'WECHATY_PUPPET_SERVICE_TOKEN' not in os.environ:
        print('''
            Error: WECHATY_PUPPET_SERVICE_TOKEN is not found in the environment variables
            You need a TOKEN to run the Python Wechaty. Please goto our README for details
            https://github.com/wechaty/python-wechaty-getting-started/#wechaty_puppet_service_token
        ''')

    bot = Wechaty()

    bot.on('scan', on_scan)
    bot.on('login', on_login)
    bot.on('message', on_message)

    await bot.start()


asyncio.run(main())


