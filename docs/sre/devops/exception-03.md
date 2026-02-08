# Exception异常架构设计：异常抛出（02）

什么时候抛出异常？什么时候是`if-raise`，什么时候是`try-except-raise`？

在软件开发中，异常不应被视为“失败”，而应视为一种**结构化的契约通信**。有效的异常抛出策略能让代码在崩溃前“优雅地拒绝”，并在发生不可控错误时“清晰地解释”。

## 异常发生的预期管理

异常并非随机产生的。根据**防御性编程**的原则，将异常分为两类预期：

- **可预见的违反约束，LBYL**：客户端输入了非法参数，或业务逻辑不满足前提条件。
- **不可控的环境失败，EAFP**：数据库连接断开、第三方接口超时或系统资源枯竭。

### 询问许可 (LBYL) 与 `if-raise`

该模式遵循“先检查，后执行”的原则，当明确知道哪些条件会导致程序进入非法状态时，应**主动预防**，异常是可预期、可枚举的。

#### 接口层的客户端校验 (`ClientException`)

在接口入口处，即使已经和前端约定了参数，但仍需要做防御，**不信任任何外部输入**。使用 `if-raise` 可以在错误逻辑进入核心业务层之前将其拦截。

```python
def create_user(username, age):
    # LBYL: 主动预防非法输入
    if not username:
        raise ClientException("用户名不能为空", code=400)
    if age < 18:
        raise ClientException("未成年人禁止注册", code=403)
    
    # 执行业务逻辑...
```

#### 防御性业务逻辑 (`BizException`)

在业务深层，当某些业务前提不满足（例如余额不足、库存告急）时，主动抛出业务异常。这比返回 `False` 或 `None` 更具语义化，且能强制调用方处理。

```python
def withdraw_money(account_id, amount):
    account = db.get_account(account_id)
    # 防御性编程：如果不满足业务前提，主动拒绝
    if account.balance < amount:
        raise BizException("账户余额不足")
    
    account.balance -= amount
    account.save()
```

### 异常转换与 `try-except-raise`

当调用底层库、数据库或第三方 API 时，无法预测所有失败场景。此时需要捕获底层异常，并将其**包装（Wrap）**为面向用户的抽象异常。特别需要注意的是，在进行异常转换时需保留原始堆栈信息（异常链），便于进行异常诊断，不能直接丢弃。

#### 异常转换策略 (`ServerException`)

直接将 `OperationalError` 或 `ConnectionError` 抛给上一层是非常危险且不友好的，需通过 `try-except-raise` 进行异常转换（翻译）。此外，除了已知的可能会发生的异常，可使用父类`Exception`进行兜底，对所有其他不可预期的异常进行转换。

```python
def get_user_profile(user_id):
    try:
        return remote_api.fetch_user(user_id)
    except RemoteTimeoutError as e:
        # 将底层超时转换为可理解的服务端异常
        # 使用 'from e' 保留原始堆栈信息（异常链）
        raise ServerException("用户服务暂时不可用，请稍后再试") from e
    except Exception as e:
        # 兜底捕获，防止信息泄露
        logger.error(f"Unknown error: {e}")
        raise ServerException("内部系统错误") from e
```

### 铁律：严禁静默失败

无论选择哪种方式，**严禁使用空的 `except: pass`**。 静默失败（Silent Failure）是调试的噩梦。如果异常被捕获，它必须被：

- **处理**（如重试、回滚、记录日志）
- **转换**（重新抛出更高级别的异常）

```python
# 静默失败
def save_order(order):
    try:
        db.insert(order)
    except Exception:
        # 错误在这里消失了！
        # 既没有日志，也没有通知调用方，更没有回滚
        pass 
        # print("数据库异常") # 简单在中断打印错误信息，也应杜绝
    
    print("订单处理完成") # 哪怕数据库挂了，这里依然会打印成功
```



## 异常性能开销

异常发生的条件可预期，使用`if-raise`主动抛出，除了语义逻辑上更准确，便于理解和问题排查。另外，在性能开销上也低得多。

