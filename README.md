# paddlenlp-wechaty

本例子展示一个基于 PaddleNLP + Wechaty 的微信闲聊机器人。通过Wechaty获取微信接收的消息，然后使用PaddleNLP的`plato-mini`模型根据对话的上下文生成新的对话文本，最终以微信消息的形式发送，实现闲聊的交互，可发语音、可发文字聊天，发一张图片，机器人会把图片转换成星际争霸风格的图片。

## 风险提示

本项目采用的api为第三方——Wechaty提供，**非微信官方api**，用户需承担来自微信方的使用风险。  
在运行项目的过程中，建议尽量选用**新注册的小号**进行测试，不要用自己的常用微信号。

## Wechaty

关于Wechaty和python-wechaty，请查阅以下官方repo：
- [Wechaty](https://github.com/Wechaty/wechaty)
- [python-wechaty](https://github.com/wechaty/python-wechaty)
- [python-wechaty-getting-started](https://github.com/wechaty/python-wechaty-getting-started/blob/master/README.md)


## 环境准备

- 系统环境：Windows10
-  python3.7+
- 安装必要的包，在requirements.txt
    pip install -r requirements.txt
  

## 安装和使用
1. Set token for your bot

    在当前系统的环境变量中，配置以下与`WECHATY_PUPPET`相关的两个变量。
    关于其作用详情和TOKEN的获取方式，请查看[Wechaty Puppet Services](https://wechaty.js.org/docs/puppet-services/)。
   

2. 部署服务器
   
   首先去阿里云申请服务器部署申请好的token，参照链接[部署](https://aistudio.baidu.com/aistudio/projectdetail/1836012)

3. 申请百度语音api接口.参照链接[百度api](https://blog.csdn.net/qq_15821487/article/details/119206606)


4. Run the bot

   ```shell
   python main_chat_bot.py
   ```
   运行后，可以通过微信移动端扫码登陆，登陆成功后则可正常使用。

## 运行效果

在`main_chat_bot.py`中，通过以下几行代码即可实例化一个`plato-mini`的模型

```python
# Initialize a PaddleHub plato-mini model
from interaction_chat import PlatoNlp
model = PlatoNlp(max_turn=10)  # Dialogue round configuration # 对话轮次配置

```

`on_message`方法是接收到消息时的回调函数，可以通过自定义的条件(譬如消息类型、消息来源、消息文字是否包含关键字、是否群聊消息等等)来判断是否回复信息，消息的更多属性和条件可以参考[Class Message](https://github.com/Wechaty/wechaty#3-class-message)。  

本示例中的`on_message`方法的代码如下，脚本中回复的条件是：
1. 消息类型是文字


```python
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
```

脚本成功运行后，所登陆的账号即可作为一个Chatbot，