from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, ImageMessage, TextSendMessage,
                            TextMessage, MessageAction, FlexSendMessage,
                            QuickReplyButton, QuickReply, CameraAction,
                            CameraRollAction
)
from io import BytesIO
from PIL import Image
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import re, json, configparser, requests, cv2, os
from select_tool_v3 import select_1, select_2, load_js1, load_js2, push_db, get_info_dict


app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

info_dict = get_info_dict()


@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=(TextMessage, ImageMessage))
def handle_message(event):
    global product_data, skin_os, age_os
    
    if isinstance(event.message, ImageMessage):
        # 讀取圖片内容
        message_content = line_bot_api.get_message_content(event.message.id)
        image_bytes = BytesIO(message_content.content)
        
         # 使用 PIL.Image 打開圖片
        img = Image.open(image_bytes)
        width, height = img.size

        # 轉換為numpy後處理
        img_np = np.array(img)

        # 檢查高度和寬度，進行填充
        if height > width:
            diff = height - width
            left = diff // 2
            right = diff - left
            padding = ((0, 0), (left, right), (0, 0))
        elif width > height:
            diff = width - height
            top = diff // 2
            bottom = diff - top
            padding = ((top, bottom), (0, 0), (0, 0))
        else:
            padding = ((0, 0), (0, 0), (0, 0))

        padded_image = np.pad(img_np, padding, mode="constant", constant_values=0)

        # 調整大小
        resized_image = cv2.resize(padded_image, (224, 224))

        img_array = np.expand_dims(resized_image, axis=0)  # 創建一個 batch
        img_array = preprocess_input(img_array)  # 應用預處理

        # 預測
        img_array = img_array.astype(np.float32)

        r = requests.post(
            "https://washmodel-p6kjjp4naq-uc.a.run.app:443/v1/models/mobile:predict",
            json={"instances": img_array.tolist()},
        )

        predicted_class = np.argmax(r.json()["predictions"][0])

        # 使用預測结果生成回覆消息
        product_id = predicted_class  # 商品編號
        product_data = select_1(product_id)  # 回傳 ID, 簡稱, 平均分數, 效果, 優點, 缺點, 推薦1, 推薦2, 推薦3
        flex_msg = FlexSendMessage(
            alt_text = 'flex_msg',
            contents = load_js1(product_data)
        )

        line_bot_api.reply_message(event.reply_token, flex_msg)

    elif isinstance(event.message, TextMessage):
        if '推薦:' in event.message.text:
            push_id = info_dict[event.message.text[3:]]
            push_info = select_1(push_id)
            id_tp = (info_dict[push_info[6]], info_dict[push_info[7]], info_dict[push_info[8]])
            push_data = push_db(id_tp)
            
            flex_msg2 = FlexSendMessage(
                alt_text = 'flex_msg',
                contents = load_js2(push_data)
            )

            line_bot_api.reply_message(event.reply_token, flex_msg2)

        elif event.message.text == '選擇膚質':
            try: 
                i = product_data
                skin = TextSendMessage(text='請選擇膚質!',
                                    quick_reply=QuickReply(items=[
                                        QuickReplyButton(action=MessageAction(label='乾性肌膚', text='1: 乾性肌膚')),
                                        QuickReplyButton(action=MessageAction(label='油性肌膚', text='2: 油性肌膚')),
                                        QuickReplyButton(action=MessageAction(label='敏感性肌膚', text='3: 敏感性肌膚')),
                                        QuickReplyButton(action=MessageAction(label='混合性肌膚', text='4: 混合性肌膚'))
                                    ]))
                line_bot_api.reply_message(event.reply_token, skin)
            except NameError:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請上傳照片!!!"))

        elif re.match('[1-4]', event.message.text[:1]):
            skin_os = event.message.text[:1]
            age = TextSendMessage(text='請選擇年紀範圍!',
                                quick_reply=QuickReply(items=[
                                    QuickReplyButton(action=MessageAction(label='20歲以下', text='A: 20歲以下')),
                                    QuickReplyButton(action=MessageAction(label='21-30歲', text='B: 21-30歲')),
                                    QuickReplyButton(action=MessageAction(label='31-45歲', text='C: 31-45歲')),
                                    QuickReplyButton(action=MessageAction(label='46歲以上', text='D: 46歲以上'))
                                ]))
            line_bot_api.reply_message(event.reply_token, age)

        elif re.match('[ABCD]', event.message.text[:1]):
            age_os = event.message.text[:1]
            age_type = f'{age_os}{skin_os}'
            result = select_2(product_data[0], age_type)
            skin_dict = {"1": "乾性肌膚", "2": "油性肌膚", "3": "敏感性肌膚", "4": "混合性肌膚"}
            age_dict = {"A": "20歲以下", "B": "21-30歲", "C": "31-45歲", "D": "46歲以上"}
            
            with open('v3.json', mode='r', encoding='utf-8') as fi:
                js = json.load(fi)

            js['body']['contents'][1]['text'] = product_data[1]  #商品名稱
            js['body']['contents'][3]['contents'][0]['contents'][1]['text'] = skin_dict[skin_os]  #皮膚屬性
            js['body']['contents'][3]['contents'][1]['contents'][1]['text'] = age_dict[age_os]  #年紀範圍
            js['body']['contents'][3]['contents'][3]['contents'][1]['text'] = str(result[0]) if result[0] != None else "無使用者分享"  #分數
            js['body']['contents'][3]['contents'][4]['contents'][1]['text'] = result[1] if result[1] != None else "無使用者分享" #效果

            flex_msg3 = FlexSendMessage(
                alt_text = 'flex_msg',
                contents = js
            )        

            line_bot_api.reply_message(event.reply_token, flex_msg3)

            skin_os = ""
            age_os = ""

        elif event.message.text == "拍照":
            camera_button = QuickReplyButton(action=CameraAction(label="拍照"))
            camera_roll = QuickReplyButton(action=CameraRollAction(label="上傳照片"))
            quick_reply = QuickReply(items=[camera_button, camera_roll])
            message = TextSendMessage(
                text="請拍照或上傳照片", quick_reply=quick_reply
            )
            line_bot_api.reply_message(event.reply_token, message)





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)