# 微信公众号开发示例

## 基础接入示例

### Node.js Express 实现

```javascript
const express = require('express');
const crypto = require('crypto');
const xml2js = require('xml2js');

const app = express();

// 验证微信服务器
app.get('/wechat', (req, res) => {
  const { signature, timestamp, nonce, echostr } = req.query;
  const token = 'your_token_here';

  // 字典序排序
  const arr = [token, timestamp, nonce].sort();
  const str = arr.join('');

  // SHA1加密
  const hashCode = crypto.createHash('sha1');
  const resultCode = hashCode.update(str, 'utf8').digest('hex');

  if (resultCode === signature) {
    res.send(echostr);
  } else {
    res.send('');
  }
});

// 处理微信消息
app.post('/wechat', (req, res) => {
  let buffer = [];
  req.on('data', (data) => {
    buffer.push(data);
  });

  req.on('end', () => {
    const msgXml = Buffer.concat(buffer).toString('utf8');
    
    xml2js.parseString(msgXml, { trim: true }, (err, result) => {
      if (err) {
        console.error('解析XML失败:', err);
        res.send('');
        return;
      }

      const msgType = result.xml.MsgType[0];
      
      if (msgType === 'text') {
        handleTextMessage(result.xml, res);
      } else if (msgType === 'event') {
        handleEventMessage(result.xml, res);
      } else {
        res.send('');
      }
    });
  });
});

function handleTextMessage(msgData, res) {
  const fromUser = msgData.FromUserName[0];
  const toUser = msgData.ToUserName[0];
  const content = msgData.Content[0];

  const replyMsg = `收到您的消息：${content}`;
  
  const replyXml = `
    <xml>
      <ToUserName><![CDATA[${fromUser}]]></ToUserName>
      <FromUserName><![CDATA[${toUser}]]></FromUserName>
      <CreateTime>${Math.floor(Date.now()/1000)}</CreateTime>
      <MsgType><![CDATA[text]]></MsgType>
      <Content><![CDATA[${replyMsg}]]></Content>
    </xml>
  `;
  
  res.set('Content-Type', 'application/xml');
  res.send(replyXml);
}

function handleEventMessage(msgData, res) {
  const event = msgData.Event[0];
  const fromUser = msgData.FromUserName[0];
  const toUser = msgData.ToUserName[0];

  let replyContent = '';
  
  if (event.toLowerCase() === 'subscribe') {
    replyContent = '欢迎关注我们的公众号！';
  } else if (event.toLowerCase() === 'unsubscribe') {
    // 取消关注事件一般不回复
    res.send('');
    return;
  } else if (event.toLowerCase() === 'click') {
    const eventKey = msgData.EventKey[0];
    if (eventKey === 'V1001_TODAY_MUSIC') {
      replyContent = '为您推荐今日音乐！';
    } else {
      replyContent = '感谢您的点击！';
    }
  }

  if (replyContent) {
    const replyXml = `
      <xml>
        <ToUserName><![CDATA[${fromUser}]]></ToUserName>
        <FromUserName><![CDATA[${toUser}]]></FromUserName>
        <CreateTime>${Math.floor(Date.now()/1000)}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[${replyContent}]]></Content>
      </xml>
    `;
    
    res.set('Content-Type', 'application/xml');
    res.send(replyXml);
  } else {
    res.send('');
  }
});

app.listen(3000, () => {
  console.log('服务器运行在端口3000');
});
```

## 菜单管理示例

### 创建个性化菜单

```javascript
const axios = require('axios');

async function createConditionalMenu() {
  const accessToken = await getAccessToken(); // 获取access_token的函数
  
  const menuData = {
    button: [
      {
        type: "click",
        name: "今日歌曲",
        key: "V1001_TODAY_MUSIC"
      },
      {
        name: "菜单",
        sub_button: [
          {
            type: "view",
            name: "搜索",
            url: "http://www.soso.com/"
          },
          {
            type: "click",
            name: "赞一下我们",
            key: "V1001_GOOD"
          }
        ]
      }
    ],
    matchrule: {
      "sex": "1",
      "country": "中国"
    }
  };

  try {
    const response = await axios.post(
      `https://api.weixin.qq.com/cgi-bin/menu/addconditional?access_token=${accessToken}`,
      menuData,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('创建个性化菜单结果:', response.data);
  } catch (error) {
    console.error('创建菜单失败:', error.response.data);
  }
}
```

## 消息推送示例

### 客服消息推送

```javascript
async function sendCustomMessage(openId, message) {
  const accessToken = await getAccessToken();
  
  const data = {
    touser: openId,
    msgtype: "text",
    text: {
      content: message
    }
  };
  
  try {
    const response = await axios.post(
      `https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=${accessToken}`,
      data,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('发送客服消息结果:', response.data);
  } catch (error) {
    console.error('发送消息失败:', error.response.data);
  }
}
```

## 网页授权示例

### 获取用户授权

```javascript
// 构造授权链接
function buildAuthUrl(redirectUri, scope = 'snsapi_userinfo') {
  const appId = 'your_app_id';
  const encodedRedirectUri = encodeURIComponent(redirectUri);
  const state = Math.random().toString(36).substr(2, 10); // 随机state值
  
  return `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${encodedRedirectUri}&response_type=code&scope=${scope}&state=${state}#wechat_redirect`;
}

// 通过code获取access_token和openid
async function getOAuthToken(code) {
  const appId = 'your_app_id';
  const secret = 'your_app_secret';
  
  const url = `https://api.weixin.qq.com/sns/oauth2/access_token?appid=${appId}&secret=${secret}&code=${code}&grant_type=authorization_code`;
  
  try {
    const response = await axios.get(url);
    return response.data; // 包含access_token, openid等信息
  } catch (error) {
    console.error('获取OAuth token失败:', error.response.data);
    throw error;
  }
}

// 获取用户详细信息
async function getUserInfo(oauthAccessToken, openId) {
  const url = `https://api.weixin.qq.com/sns/userinfo?access_token=${oauthAccessToken}&openid=${openId}&lang=zh_CN`;
  
  try {
    const response = await axios.get(url);
    return response.data; // 用户详细信息
  } catch (error) {
    console.error('获取用户信息失败:', error.response.data);
    throw error;
  }
}
```