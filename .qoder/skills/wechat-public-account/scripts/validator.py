#!/usr/bin/env python3
"""
微信公众号配置验证工具
用于验证微信公众号的基本配置是否正确
"""

import hashlib
import sys
import os
import json
from urllib.parse import urlparse

def verify_signature(token, timestamp, nonce, signature):
    """
    验证微信服务器签名
    """
    # 字典序排序后拼接字符串
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    
    # SHA1加密
    hash_obj = hashlib.sha1(tmp_str.encode('utf-8'))
    hash_value = hash_obj.hexdigest()
    
    return hash_value == signature

def validate_url_format(url):
    """
    验证URL格式是否正确
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_token(token):
    """
    验证Token格式
    """
    if len(token) < 3 or len(token) > 32:
        return False
    # Token只能包含字母、数字、下划线
    import re
    return bool(re.match(r'^[a-zA-Z0-9_]+$', token))

def check_config_file(config_path):
    """
    检查配置文件是否存在及格式是否正确
    """
    if not os.path.exists(config_path):
        return False, f"配置文件不存在: {config_path}"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = ['app_id', 'app_secret', 'token']
        for field in required_fields:
            if field not in config:
                return False, f"配置文件缺少必要字段: {field}"
        
        return True, config
    except json.JSONDecodeError:
        return False, "配置文件JSON格式错误"
    except Exception as e:
        return False, f"读取配置文件出错: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python wechat_validator.py validate_config <config_path>     # 验证配置文件")
        print("  python wechat_validator.py verify_signature <token> <timestamp> <nonce> <signature>  # 验证签名")
        print("  python wechat_validator.py validate_token <token>           # 验证token格式")
        print("  python wechat_validator.py validate_url <url>               # 验证URL格式")
        return

    command = sys.argv[1]
    
    if command == "validate_config":
        if len(sys.argv) != 3:
            print("请提供配置文件路径")
            return
        
        config_path = sys.argv[2]
        is_valid, result = check_config_file(config_path)
        
        if is_valid:
            print("✓ 配置文件验证通过")
            print(f"AppID: {result.get('app_id', 'N/A')}")
            print(f"Token: {result.get('token', 'N/A')}")
        else:
            print(f"✗ {result}")
    
    elif command == "verify_signature":
        if len(sys.argv) != 6:
            print("请提供token, timestamp, nonce, signature参数")
            return
        
        token, timestamp, nonce, sig = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
        is_valid = verify_signature(token, timestamp, nonce, sig)
        
        if is_valid:
            print("✓ 签名验证通过")
        else:
            print("✗ 签名验证失败")
    
    elif command == "validate_token":
        if len(sys.argv) != 3:
            print("请提供token参数")
            return
        
        token = sys.argv[2]
        is_valid = validate_token(token)
        
        if is_valid:
            print("✓ Token格式正确")
        else:
            print("✗ Token格式错误，长度应为3-32位，只允许字母、数字、下划线")
    
    elif command == "validate_url":
        if len(sys.argv) != 3:
            print("请提供URL参数")
            return
        
        url = sys.argv[2]
        is_valid = validate_url_format(url)
        
        if is_valid:
            print("✓ URL格式正确")
        else:
            print("✗ URL格式错误")

if __name__ == "__main__":
    main()