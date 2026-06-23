---
title: "Firebase: 阅读量 & 点赞量"
weight: 15
draft: false
description: "了解 Blowfish 如何集成 Firebase，并动态显示阅读量和点赞量。"
slug: "firebase-views"
tags: ["firebase", "阅读量", "点赞量"]
series: ["部署教程"]
series_order: 15
---

为了能够在网站中获取动态数据，我们支持了对 Firebase 的集成。这将允许你在列表和文章中使用阅读量功能。

1. 访问 <a target="_blank" href="https://firebase.com">Firebase</a> 并创建一个账户
2. 创建一个新项目
3. 选择分析位置 
4. Blowfish 是通过 `params.toml` 配置文件中的 firebase 相关参数，来和 firebase 集成的，更多的细节内容可以参考  <a target="_blank" href="{{< ref "configuration/#theme-parameters" >}}">这个页面</a>。在 Firebase 控制台创建 Web 应用后，将 `FirebaseConfig` 对象中的参数填入 `params.toml`，**不要**把真实凭据提交到公开仓库。示例结构如下：

```js
// 从你需要的 SDK 中导入所需的函数
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

// 你 Web 应用的 Firebase 配置（请替换为自己的项目值）
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID"
};

// 初始化 Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
```

对应 `params.toml` 配置示例：

```toml
[firebase]
  apiKey = "YOUR_API_KEY"
  authDomain = "YOUR_PROJECT_ID.firebaseapp.com"
  projectId = "YOUR_PROJECT_ID"
  storageBucket = "YOUR_PROJECT_ID.appspot.com"
  messagingSenderId = "YOUR_MESSAGING_SENDER_ID"
  appId = "YOUR_APP_ID"
  measurementId = "YOUR_MEASUREMENT_ID"
```

5. 设置 Firestore - 选择 Build 并打开 Firestore. 创建一个数据库，并在生产环境中启动。选择服务器位置然后等待其部署完成。启动之后你需要配置规则。只需要复制并粘贴下面的内容，然后点击发布即可。这些规则确保阅读量只能增加1，点赞量只能增加或减少1（且不会低于0）。
```txt
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Views - read anyone, only increment by 1
    match /views/{document} {
      allow read: if request.auth != null;
      allow create: if request.auth != null
                    && request.resource.data.keys().hasOnly(['views'])
                    && request.resource.data.views == 1;
      allow update: if request.auth != null
                    && request.resource.data.diff(resource.data).affectedKeys().hasOnly(['views'])
                    && request.resource.data.views == resource.data.views + 1;
    }

    // Likes - read anyone, only +1 or -1
    match /likes/{document} {
      allow read: if request.auth != null;
      allow create: if request.auth != null
                    && request.resource.data.keys().hasOnly(['likes'])
                    && request.resource.data.likes == 1;
      allow update: if request.auth != null
                    && request.resource.data.diff(resource.data).affectedKeys().hasOnly(['likes'])
                    && (request.resource.data.likes == resource.data.likes + 1
                        || request.resource.data.likes == resource.data.likes - 1)
                    && request.resource.data.likes >= 0;
    }

    // Deny everything else
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```
6. 开启匿名授权 - 选择 Build 并打开 Authentication。选择开始，点击 Anonymous 并开启，保存。
7. 享受 - 现在可以激活 Blowfish 中文章阅读量和点赞量的功能。
