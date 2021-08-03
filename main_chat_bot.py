# -*- coding: utf-8 -*-
"""
@Author  :Mart
@Time    :2021/7/8 21:25
@version :Python3.7.4
@Software:pycharm2020.3.2
"""
import re
import cv2
import asyncio
import ffmpeg
import os
import paddlehub as hub
from wechaty import (
    Contact,
    FileBox,
    Message,
    Wechaty,
    ScanStatus,
)
from wechaty_puppet import MessageType
from interaction_chat import PlatoNlp
from aip import AipSpeech

APP_ID = '24619173'
API_KEY = 'iHG3dPeSKbfqlTnCtZfXX'  # 填写自己申请的
SECRET_KEY = '4xOR67deEcxkEfUVU8wp8sLz1XX'  # 填写自己申请的
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

os.environ['WECHATY_PUPPET'] = "wechaty-puppet-service"
os.environ['WECHATY_PUPPET_SERVICE_TOKEN'] = "puppet_padlocal_XX"  # 填写自己申请的

mp3_path = 'audio/receive.mp3'
wav_path = 'audio/receive.wav'
wav_path_res = 'audio/response.wav'

img_in_path = 'image/receive.jpg'
img_out_path = 'image/response.jpg'
img_style_path = 'image/image_style.jpg'

model = PlatoNlp(max_turn=5)  # Dialogue round configuration

model_cv = hub.Module(name="stylepro_artistic")  # 定义model


def img_transform(img_path):
    """
    img_path: 图片的路径
    img_name: 图片的文件名
    """
    # 模型预测
    result = model_cv.style_transfer(
                                    images=[{
                                        'content': cv2.imread(img_path),
                                        'styles': [cv2.imread(img_style_path)]
                                    }],
                                    visualization=True,
                                    output_dir='image')

    # 返回新图片的路径
    return result[0]['save_path']


def aip_asr(file_path):
    """
    pass
    """
    with open(file_path, 'rb') as fp:
        text_result = client.asr(fp.read(), 'wav', 16000, {'dev_pid': 1537})
    return text_result['result'][0]


def aip_synthesis(text, out_path):
    """
    pass
    """
    result = client.synthesis(text, 'zh', 1, {'vol': 5})
    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open(out_path, 'wb') as f:
            f.write(result)
    return out_path


def resample_rate(in_path, out_path, new_sample_rate=16000):
    """
    pass
    """
    if os.path.isfile(out_path):
        os.remove(out_path)
    ffmpeg.input(in_path).output(out_path, ar=new_sample_rate).run()
    return out_path


async def on_message(msg: Message):
    """
    Message Handler for the Bot
    """
    if not msg.is_self() and isinstance(msg.text(), str) and len(msg.text()) > 0 and \
            msg._payload.type == MessageType.MESSAGE_TYPE_TEXT:
        text_new = re.sub(r'<.*>', '', msg.text())
        if len(text_new) < 400:
            if '@' in text_new:
                if '@小裕' in text_new:
                    bot_response = model.predict(data=text_new.replace('@小裕', ''))
                    await msg.say(bot_response)
            else:
                bot_response = model.predict(data=text_new)
                await msg.say(bot_response)
        else:
            await msg.say('说的太多了，长话短说啊')
    elif not msg.is_self() and msg._payload.type == MessageType.MESSAGE_TYPE_IMAGE:
        file_box_2 = await msg.to_file_box()  # 将Message转换为FileBox
        await file_box_2.to_file(file_path=img_in_path, overwrite=True)  # 将图片保存为本地文件
        img_new_path = img_transform(img_in_path)  # 调用图片风格转换的函数
        file_box_3 = FileBox.from_file(img_new_path)  # 从新的路径获取图片
        await msg.say(file_box_3)
    elif not msg.is_self() and msg._payload.type == MessageType.MESSAGE_TYPE_AUDIO:
        file_box_audio = await msg.to_file_box()
        await file_box_audio.to_file(file_path=mp3_path, overwrite=True)
        audio_path_new = resample_rate(mp3_path, wav_path, new_sample_rate=16000)  # 转换能识别格式
        text = aip_asr(audio_path_new)  # 语音识别成文字
        bot_response = model.predict(data=text)  # 生产文字回复
        bot_response_path = aip_synthesis(bot_response, wav_path_res)  # 语音生成
        file_box_audio_new = FileBox.from_file(bot_response_path)
        await msg.say(file_box_audio_new)


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


