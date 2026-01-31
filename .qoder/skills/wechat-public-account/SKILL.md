---
name: wechat-public-account
description: 处理微信公众号开发相关任务，包括接入验证、消息处理、菜单管理、用户管理等功能。适用于微信公众号开发者，帮助完成接口对接、消息回复、菜单配置等工作。
---

# 微信公众号开发助手

## 功能概述

此技能帮助开发者处理微信公众号开发中的常见任务，包括：

- 微信公众号服务器接入验证
- 消息接收与回复处理
- 自定义菜单创建与管理
- 用户信息获取与管理
- 素材管理
- 网页授权等高级功能

## 微信公众号服务器接入

### 接入流程

当用户需要配置微信公众号服务器时，按以下步骤操作：

1. 在微信公众平台后台设置服务器地址
2. 验证URL有效性
3. 配置Token、AppID、AppSecret

### 接入验证代码示例

```python
import hashlib
import xml.etree.ElementTree as ET
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/wechat', methods=['GET'])
def verify_server():
    """验证微信服务器"""
    token = 'your_token_here'  # 替换为实际token
    
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')
    
    # 字典序排序后拼接字符串
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    
    # SHA1加密
    hash_obj = hashlib.sha1(tmp_str.encode('utf-8'))
    hash_value = hash_obj.hexdigest()
    
    # 验证签名
    if hash_value == signature:
        return echostr
    else:
        return ''

@app.route('/wechat', methods=['POST'])
def handle_message():
    """处理微信消息"""
    xml_data = request.data
    root = ET.fromstring(xml_data)
    
    msg_type = root.find('MsgType').text
    
    # 根据消息类型进行相应处理
    if msg_type == 'text':
        return handle_text_message(root)
    elif msg_type == 'event':
        return handle_event_message(root)
    else:
        # 其他类型消息默认回复空字符串
        return ''

def handle_text_message(root):
    """处理文本消息"""
    from_user = root.find('FromUserName').text
    to_user = root.find('ToUserName').text
    content = root.find('Content').text
    
    # 构造回复消息XML
    reply_xml = f"""<xml>
    <ToUserName><![CDATA[{from_user}]]></ToUserName>
    <FromUserName><![CDATA[{to_user}]]></FromUserName>
    <CreateTime>{int(time.time())}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[收到您的消息：{content}]]></Content>
    </xml>"""
    
    response = make_response(reply_xml)
    response.content_type = 'application/xml'
    return response

def handle_event_message(root):
    """处理事件消息"""
    event = root.find('Event').text
    from_user = root.find('FromUserName').text
    to_user = root.find('ToUserName').text
    
    if event.lower() == 'subscribe':
        # 关注事件
        content = '欢迎关注我们的公众号！'
    elif event.lower() == 'unsubscribe':
        # 取消关注事件
        content = ''
    else:
        content = '感谢您的互动！'
    
    if content:
        reply_xml = f"""<xml>
        <ToUserName><![CDATA[{from_user}]]></ToUserName>
        <FromUserName><![CDATA[{to_user}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
        </xml>"""
        
        response = make_response(reply_xml)
        response.content_type = 'application/xml'
        return response
    else:
        return ''
```

## 消息处理

### 文本消息处理

当接收到用户发送的文本消息时，可以根据关键词进行智能回复：

- 关键词匹配回复
- 智能客服对话
- 图文消息回复

### 事件消息处理

处理用户的特定行为事件：

- 关注事件 (subscribe)
- 取消关注事件 (unsubscribe)
- 菜单点击事件 (CLICK)
- 扫描带参数二维码事件 (SCAN)

## 自定义菜单管理

### 创建菜单

```python
import requests
import json

def create_menu(access_token, menu_data):
    """
    创建自定义菜单
    :param access_token: 接口调用凭据
    :param menu_data: 菜单数据
    :return: 返回结果
    """
    url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(menu_data, ensure_ascii=False).encode('utf-8'))
    return response.json()

# 示例菜单数据
menu_data = {
    "button": [
        {
            "type": "click",
            "name": "今日歌曲",
            "key": "V1001_TODAY_MUSIC"
        },
        {
            "name": "菜单",
            "sub_button": [
                {
                    "type": "view",
                    "name": "搜索",
                    "url": "http://www.soso.com/"
                },
                {
                    "type": "click",
                    "name": "赞一下我们",
                    "key": "V1001_GOOD"
                }
            ]
        }
    ]
}
```

## 用户管理

### 获取用户列表

```python
def get_user_list(access_token, next_openid=''):
    """
    获取用户列表
    :param access_token: 接口调用凭据
    :param next_openid: 第一个拉取的OPENID
    :return: 用户列表
    """
    url = f"https://api.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&next_openid={next_openid}"
    response = requests.get(url)
    return response.json()
```

## 高级功能

### 网页授权

实现网页授权获取用户基本信息：

1. 引导用户进入授权页面
2. 通过code换取网页授权access_token
3. 拉取用户信息

### 素材管理

- 新增临时素材
- 获取临时素材
- 新增永久素材
- 删除永久素材

## 注意事项

1. Token必须为英文或数字，长度为3-32字符
2. URL必须以http://或https://开头
3. 消息回复必须在5秒内完成
4. 需要正确处理XML格式的消息
5. 注意接口调用频率限制
6. 妥善保管AppSecret，不要泄露