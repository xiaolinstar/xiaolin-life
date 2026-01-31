# 微信公众号菜单管理功能实现指南

## 1. 自定义菜单概述

### 1.1 菜单功能
微信公众号自定义菜单为用户提供便捷的交互入口，支持以下功能：
- 一键触发特定操作
- 跳转到指定网页
- 触发预设关键词回复
- 调用特定功能

### 1.2 菜单限制
- 最多包含3个一级菜单
- 每个一级菜单最多包含5个二级菜单
- 整体菜单不超过80个汉字
- 菜单名称不能为空

## 2. 菜单类型详解

### 2.1 点击推事件（click）
用户点击菜单后，微信服务器会推送事件到开发者服务器。

```json
{
    "type": "click",
    "name": "今日歌曲",
    "key": "V1001_TODAY_MUSIC"
}
```

### 2.2 跳转URL（view）
用户点击菜单后跳转到指定URL页面。

```json
{
    "type": "view",
    "name": "搜索",
    "url": "http://www.soso.com/"
}
```

### 2.3 扫码推事件（scancode_push）
用户点击菜单后弹出扫码框，扫码后返回结果。

```json
{
    "type": "scancode_push",
    "name": "扫码",
    "key": "rselfmenu_0_0"
}
```

### 2.4 扫码推事件且弹出"消息接收中"提示框（scancode_waitmsg）
扫码后返回结果并弹出提示框。

```json
{
    "type": "scancode_waitmsg",
    "name": "扫码带提示",
    "key": "rselfmenu_0_1"
}
```

### 2.5 弹出系统拍照发图（pic_sysphoto）
用户点击菜单后调用系统相机拍照并上传。

```json
{
    "type": "pic_sysphoto",
    "name": "系统拍照",
    "key": "rselfmenu_1_0"
}
```

### 2.6 弹出拍照或者相册发图（pic_photo_or_album）
用户可选择拍照或从相册选择图片上传。

```json
{
    "type": "pic_photo_or_album",
    "name": "拍照或相册",
    "key": "rselfmenu_1_1"
}
```

### 2.7 弹出微信相册发图器（pic_weixin）
直接调用微信相册选择图片上传。

```json
{
    "type": "pic_weixin",
    "name": "微信相册",
    "key": "rselfmenu_1_2"
}
```

### 2.8 弹出地理位置选择器（location_select）
用户可选择地理位置并返回给开发者。

```json
{
    "type": "location_select",
    "name": "选择位置",
    "key": "rselfmenu_2_0"
}
```

## 3. 菜单管理API实现

### 3.1 获取access_token

```python
import requests
import json
import time

def get_access_token(app_id, app_secret):
    """
    获取access_token
    """
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if 'access_token' in result:
            return result['access_token']
        else:
            raise Exception(f"获取access_token失败: {result}")
    except Exception as e:
        raise Exception(f"请求access_token时发生错误: {str(e)}")

# 缓存access_token，避免频繁请求
_access_token_cache = {}
_access_token_expire_time = {}

def get_cached_access_token(app_id, app_secret):
    """
    获取缓存的access_token
    """
    current_time = time.time()
    
    # 检查是否已存在有效的缓存
    cache_key = f"{app_id}_{app_secret}"
    if cache_key in _access_token_expire_time:
        if current_time < _access_token_expire_time[cache_key]:
            return _access_token_cache[cache_key]
    
    # 获取新的access_token
    access_token = get_access_token(app_id, app_secret)
    
    # 缓存access_token，设置过期时间为7200秒（官方默认有效期）
    _access_token_cache[cache_key] = access_token
    _access_token_expire_time[cache_key] = current_time + 7000  # 提前200秒刷新
    
    return access_token
```

### 3.2 创建菜单

```python
def create_menu(access_token, menu_data):
    """
    创建自定义菜单
    :param access_token: 接口调用凭据
    :param menu_data: 菜单数据
    :return: API返回结果
    """
    url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={access_token}"
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    try:
        # 将数据转换为JSON并编码为UTF-8
        json_data = json.dumps(menu_data, ensure_ascii=False).encode('utf-8')
        
        response = requests.post(url, headers=headers, data=json_data)
        result = response.json()
        
        if result.get('errcode') == 0:
            print("菜单创建成功")
            return {"success": True, "message": "菜单创建成功"}
        else:
            error_msg = f"菜单创建失败: 错误码 {result.get('errcode')}, 错误信息: {result.get('errmsg')}"
            print(error_msg)
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"创建菜单时发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}

def create_default_menu(access_token):
    """
    创建默认菜单示例
    """
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
    
    return create_menu(access_token, menu_data)
```

### 3.3 查询菜单

```python
def get_current_menu(access_token):
    """
    查询当前菜单配置
    :param access_token: 接口调用凭据
    :return: 菜单配置信息
    """
    url = f"https://api.weixin.qq.com/cgi-bin/menu/get?access_token={access_token}"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if 'menu' in result:
            return {
                "success": True,
                "menu": result['menu']
            }
        else:
            return {
                "success": False,
                "error": f"查询菜单失败: {result.get('errmsg', '未知错误')}",
                "error_code": result.get('errcode')
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"查询菜单时发生错误: {str(e)}"
        }

def get_menu_config(access_token):
    """
    获取菜单配置的简化方法
    """
    result = get_current_menu(access_token)
    if result['success']:
        return result['menu']
    else:
        print(result['error'])
        return None
```

### 3.4 删除菜单

```python
def delete_menu(access_token):
    """
    删除自定义菜单
    :param access_token: 接口调用凭据
    :return: 删除结果
    """
    url = f"https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={access_token}"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get('errcode') == 0:
            print("菜单删除成功")
            return {"success": True, "message": "菜单删除成功"}
        else:
            error_msg = f"菜单删除失败: 错误码 {result.get('errcode')}, 错误信息: {result.get('errmsg')}"
            print(error_msg)
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"删除菜单时发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
```

## 4. 个性化菜单管理

### 4.1 创建个性化菜单

```python
def create_conditional_menu(access_token, menu_data):
    """
    创建个性化菜单
    :param access_token: 接口调用凭据
    :param menu_data: 包含matchrule的菜单数据
    :return: API返回结果
    """
    url = f"https://api.weixin.qq.com/cgi-bin/menu/addconditional?access_token={access_token}"
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    try:
        json_data = json.dumps(menu_data, ensure_ascii=False).encode('utf-8')
        
        response = requests.post(url, headers=headers, data=json_data)
        result = response.json()
        
        if result.get('errcode') == 0:
            menu_id = result.get('menuid')
            print(f"个性化菜单创建成功，菜单ID: {menu_id}")
            return {"success": True, "menu_id": menu_id, "message": "个性化菜单创建成功"}
        else:
            error_msg = f"个性化菜单创建失败: 错误码 {result.get('errcode')}, 错误信息: {result.get('errmsg')}"
            print(error_msg)
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"创建个性化菜单时发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}

def create_gender_based_menu(access_token):
    """
    创建基于性别的个性化菜单示例
    """
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
        ],
        "matchrule": {
            "sex": "1",  # 男
            "country": "中国",
            "province": "广东",
            "city": "广州"
        }
    }
    
    return create_conditional_menu(access_token, menu_data)
```

### 4.2 测试个性化菜单

```python
def test_conditional_menu(access_token, menu_id):
    """
    测试个性化菜单
    :param access_token: 接口调用凭据
    :param menu_id: 菜单ID
    :return: 测试结果
    """
    url = f"https://api.weixin.qq.com/cgi-bin/menu/trymatch?access_token={access_token}"
    
    data = {
        "user_id": "test_openid"  # 实际使用时替换为真实的openid
    }
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    try:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        response = requests.post(url, headers=headers, data=json_data)
        result = response.json()
        
        if result.get('errcode') == 0:
            print("个性化菜单测试成功")
            return {"success": True, "menu": result.get('menu')}
        else:
            error_msg = f"个性化菜单测试失败: 错误码 {result.get('errcode')}, 错误信息: {result.get('errmsg')}"
            print(error_msg)
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"测试个性化菜单时发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
```

### 4.3 删除个性化菜单

```python
def delete_conditional_menu(access_token, menu_id):
    """
    删除个性化菜单
    :param access_token: 接口调用凭据
    :param menu_id: 菜单ID
    :return: 删除结果
    """
    url = f"https://api.weixin.qq.com/cgi-bin/menu/delconditional?access_token={access_token}"
    
    data = {
        "menuid": menu_id
    }
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    try:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        response = requests.post(url, headers=headers, data=json_data)
        result = response.json()
        
        if result.get('errcode') == 0:
            print(f"个性化菜单(菜单ID: {menu_id})删除成功")
            return {"success": True, "message": f"个性化菜单(菜单ID: {menu_id})删除成功"}
        else:
            error_msg = f"个性化菜单删除失败: 错误码 {result.get('errcode')}, 错误信息: {result.get('errmsg')}"
            print(error_msg)
            return {"success": False, "error": error_msg}
            
    except Exception as e:
        error_msg = f"删除个性化菜单时发生错误: {str(e)}"
        print(error_msg)
        return {"success": False, "error": error_msg}
```

## 5. 菜单配置管理类

```python
class WeChatMenuManager:
    """
    微信菜单管理类
    """
    
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
    
    def get_access_token(self):
        """
        获取access_token
        """
        return get_cached_access_token(self.app_id, self.app_secret)
    
    def create_menu(self, menu_data):
        """
        创建菜单
        """
        access_token = self.get_access_token()
        return create_menu(access_token, menu_data)
    
    def get_menu(self):
        """
        获取当前菜单
        """
        access_token = self.get_access_token()
        return get_current_menu(access_token)
    
    def delete_menu(self):
        """
        删除菜单
        """
        access_token = self.get_access_token()
        return delete_menu(access_token)
    
    def create_conditional_menu(self, menu_data):
        """
        创建个性化菜单
        """
        access_token = self.get_access_token()
        return create_conditional_menu(access_token, menu_data)
    
    def delete_conditional_menu(self, menu_id):
        """
        删除个性化菜单
        """
        access_token = self.get_access_token()
        return delete_conditional_menu(access_token, menu_id)
    
    def test_conditional_menu(self, menu_id):
        """
        测试个性化菜单
        """
        access_token = self.get_access_token()
        return test_conditional_menu(access_token, menu_id)

# 菜单配置模板
MENU_TEMPLATES = {
    "basic_service": {
        "button": [
            {
                "name": "服务",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "在线客服",
                        "key": "SERVICE_ONLINE_CHAT"
                    },
                    {
                        "type": "click",
                        "name": "预约服务",
                        "key": "SERVICE_BOOKING"
                    },
                    {
                        "type": "click",
                        "name": "常见问题",
                        "key": "SERVICE_FAQ"
                    }
                ]
            },
            {
                "name": "资讯",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "最新动态",
                        "key": "INFO_NEWS"
                    },
                    {
                        "type": "click",
                        "name": "产品介绍",
                        "key": "INFO_PRODUCTS"
                    },
                    {
                        "type": "view",
                        "name": "官方网站",
                        "url": "https://example.com"
                    }
                ]
            },
            {
                "name": "我的",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "个人中心",
                        "key": "MY_CENTER"
                    },
                    {
                        "type": "click",
                        "name": "联系我们",
                        "key": "MY_CONTACT"
                    },
                    {
                        "type": "click",
                        "name": "意见反馈",
                        "key": "MY_FEEDBACK"
                    }
                ]
            }
        ]
    },
    "ecommerce": {
        "button": [
            {
                "name": "商品",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "热销商品",
                        "key": "PRODUCT_HOT"
                    },
                    {
                        "type": "click",
                        "name": "新品推荐",
                        "key": "PRODUCT_NEW"
                    },
                    {
                        "type": "click",
                        "name": "商品分类",
                        "key": "PRODUCT_CATEGORY"
                    }
                ]
            },
            {
                "name": "购物",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "购物车",
                        "url": "https://example.com/cart"
                    },
                    {
                        "type": "view",
                        "name": "我的订单",
                        "url": "https://example.com/orders"
                    },
                    {
                        "type": "click",
                        "name": "优惠活动",
                        "key": "SHOP_PROMOTION"
                    }
                ]
            },
            {
                "name": "服务",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "物流查询",
                        "key": "SERVICE_LOGISTICS"
                    },
                    {
                        "type": "click",
                        "name": "售后服务",
                        "key": "SERVICE_AFTER_SALES"
                    },
                    {
                        "type": "click",
                        "name": "客服中心",
                        "key": "SERVICE_SUPPORT"
                    }
                ]
            }
        ]
    }
}

def load_menu_from_file(file_path):
    """
    从文件加载菜单配置
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            menu_data = json.load(f)
        return menu_data
    except FileNotFoundError:
        print(f"菜单配置文件不存在: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"菜单配置文件格式错误: {file_path}")
        return None
    except Exception as e:
        print(f"加载菜单配置文件时发生错误: {str(e)}")
        return None

def save_menu_to_file(menu_data, file_path):
    """
    保存菜单配置到文件
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(menu_data, f, ensure_ascii=False, indent=2)
        print(f"菜单配置已保存到: {file_path}")
    except Exception as e:
        print(f"保存菜单配置文件时发生错误: {str(e)}")
```

## 6. 菜单管理命令行工具

```python
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='微信公众号菜单管理工具')
    parser.add_argument('--app-id', required=True, help='微信公众号AppID')
    parser.add_argument('--app-secret', required=True, help='微信公众号AppSecret')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建菜单命令
    create_parser = subparsers.add_parser('create', help='创建菜单')
    create_parser.add_argument('--menu-file', required=True, help='菜单配置文件路径')
    
    # 查询菜单命令
    get_parser = subparsers.add_parser('get', help='查询当前菜单')
    
    # 删除菜单命令
    delete_parser = subparsers.add_parser('delete', help='删除菜单')
    
    # 创建个性化菜单命令
    create_cond_parser = subparsers.add_parser('create-cond', help='创建个性化菜单')
    create_cond_parser.add_argument('--menu-file', required=True, help='菜单配置文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建菜单管理器
    menu_manager = WeChatMenuManager(args.app_id, args.app_secret)
    
    if args.command == 'create':
        menu_data = load_menu_from_file(args.menu_file)
        if menu_data:
            result = menu_manager.create_menu(menu_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("无法加载菜单配置文件")
    
    elif args.command == 'get':
        result = menu_manager.get_menu()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == 'delete':
        result = menu_manager.delete_menu()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == 'create-cond':
        menu_data = load_menu_from_file(args.menu_file)
        if menu_data:
            result = menu_manager.create_conditional_menu(menu_data)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("无法加载菜单配置文件")

if __name__ == '__main__':
    main()
```

## 7. 菜单管理最佳实践

### 7.1 菜单设计原则

1. **简洁明了**：菜单层级不宜过深，建议不超过两级
2. **功能明确**：菜单名称应清晰表达功能意图
3. **常用优先**：将最常用的功能放在显眼位置
4. **定期更新**：根据用户使用习惯调整菜单结构

### 7.2 错误处理

```python
def safe_create_menu(access_token, menu_data, max_retries=3):
    """
    安全创建菜单，带重试机制
    """
    for attempt in range(max_retries):
        try:
            result = create_menu(access_token, menu_data)
            if result['success']:
                return result
            else:
                print(f"第{attempt + 1}次尝试失败: {result['error']}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # 等待1秒后重试
        except Exception as e:
            print(f"第{attempt + 1}次尝试异常: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    return {"success": False, "error": f"经过{max_retries}次尝试仍失败"}

def validate_menu_structure(menu_data):
    """
    验证菜单结构是否符合微信规范
    """
    errors = []
    
    if 'button' not in menu_data:
        errors.append("菜单数据缺少'button'字段")
        return False, errors
    
    buttons = menu_data['button']
    
    if len(buttons) > 3:
        errors.append("一级菜单不能超过3个")
    
    for i, button in enumerate(buttons):
        if 'name' not in button:
            errors.append(f"第{i+1}个菜单缺少'name'字段")
            continue
        
        name = button['name']
        if len(name.encode('utf-8')) > 16:  # 微信限制16字节
            errors.append(f"菜单'{name}'名称过长")
        
        # 检查是否有子菜单
        if 'sub_button' in button:
            sub_buttons = button['sub_button']
            if len(sub_buttons) > 5:
                errors.append(f"菜单'{name}'的子菜单不能超过5个")
            
            for j, sub_button in enumerate(sub_buttons):
                if 'name' not in sub_button:
                    errors.append(f"第{i+1}个菜单的第{j+1}个子菜单缺少'name'字段")
                    continue
                
                sub_name = sub_button['name']
                if len(sub_name.encode('utf-8')) > 16:
                    errors.append(f"子菜单'{sub_name}'名称过长")
    
    return len(errors) == 0, errors
```

通过以上完整的菜单管理实现，你可以方便地创建、更新、删除微信公众号的自定义菜单，并支持个性化菜单功能。