# Exception 异常的架构设计：异常分类

【序言】

异常分类可从以下多维度切入：

**核心责任维度**

- **来源**：系统异常（外部/基础设施）vs 业务异常（内部规则）
- **责任方**：客户端错误（4xx）vs 服务器错误（5xx）

**运维监控维度**

- **严重程度**：致命/错误/警告/信息
- **可恢复性**：可重试/不可重试/可降级
- **影响范围**：用户/租户/服务/系统级

**技术架构维度**

- **生命周期阶段**：启动/运行/关闭
- **数据流阶段**：输入/处理/输出/存储
- **架构层次**：表现层/应用层/领域层/基础设施层

**商业考量维度**

- **SLA影响**：违例/风险/无影响

分类目的是指导处理策略，而非过度设计。对于绝大多数基础项目，按照**来源+责任方**来进行分类是合适的。

---

特别地，对于**来源**，从开发者角度来划分：

- 平台异常（外部异常、内置异常）：编程语言、开发框架、中间件、第三方库、远程调用等抛出的异常，由元开发者定义。
- 应用异常：由业务开发者定义的异常。

> 元开发者，指的是为开发者服务的开发者。

### 平台异常

由编程语言、运行时、框架、中间件等"元开发者"定义的异常，有四大来源：编程语言、操作系统/文件系统、网络/外部服务、数据库/中间件。

```Python
# 1. 语言运行时
def language_runtime():
    # 内存、类型、运算等基础错误
    try:
        x = 1 / 0                    # ZeroDivisionError
        y = int("abc")               # ValueError
        z = {}["nonexistent"]        # KeyError
    except (ZeroDivisionError, ValueError, KeyError) as e:
        print(f"语言运行时异常: {type(e).__name__}")

# 2. 操作系统/文件系统
def os_filesystem():
    # 文件、进程、权限等OS相关错误
    import os
    try:
        os.remove("/nonexistent.txt") # FileNotFoundError
        import subprocess
        subprocess.run(["invalid"])   # FileNotFoundError
    except OSError as e:
        print(f"操作系统异常: {e}")

# 3. 网络/外部服务，包括远程关系调用RPC
def network_external():
    # 网络连接、HTTP请求等
    import requests
    try:
        response = requests.get("http://invalid", timeout=1)
    except requests.exceptions.ConnectionError as e:
        print(f"网络异常: {e}")
    except requests.exceptions.Timeout as e:
        print(f"超时异常: {e}")

# 4. 数据库/中间件
def database_middleware():
    # 数据库连接、查询、事务等
    import sqlite3
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("INVALID SQL")   # sqlite3.OperationalError
    except sqlite3.Error as e:
        print(f"数据库异常: {e}")
```

开发者不需要定义平台异常，但需要对异常进行处理，在下一章节描述。

### 应用异常

又称为自定义异常，由业务开发者为了满足特定业务需求而创建的异常，反映业务规则、流程限制和领域逻辑，继承`Exception` 类创建新类`class AppException(Exception)`。应用异常的核心特征：

- 业务语义性：异常名称和消息反映业务概念，如：`InsufficientFundsException`（余额不足）

- 完全可控：开发者决定何时抛出、抛出什么，可以添加任何业务相关属性

- 层次结构化：可以建立有意义的继承体系，便于分类处理和监控

- 主动设计：作为业务逻辑的一部分，提前设计异常类型和场景

基于**防御性编程、Fail-Fast、用户友好、可观测性**四大核心原则，将自定义异常细分为**客户端异常、业务异常、服务端异常**三层架构，是当前企业级应用开发中**成熟且合理的分层异常治理方案**，相比单一自定义异常或原生异常混用的模式，具备显著的工程化优势。

#### 客户端异常 4xx

客户端异常是由**调用方（前端用户、第三方服务、内部调用方）**的行为或输入不符合服务约定而引发的异常，服务端本身无任何故障，责任完全在调用方。

**典型场景**

- 请求参数错误：参数缺失、参数类型不匹配、参数格式非法（如手机号格式错误、邮箱格式错误、ID 为非数字）
- 请求权限不足：未登录、登录过期、无接口访问权限、无资源操作权限
- 请求资源不存在：访问的接口路径错误、请求的文件 / 数据 ID 不存在
- 请求方式错误：使用 GET 请求调用仅支持 POST 的接口、请求头缺失必要字段
- 调用频率超限：触发接口限流、防刷规则

#### 业务异常 299

业务异常是**在服务端逻辑正常执行、请求参数合法的前提下，因业务规则不满足、业务流程无法继续推进**而引发的异常，属于业务层面的预期性阻断，而非系统故障。业务异常可以归属于正常的业务逻辑，因此可将其划分到状态码2xx序列，自行定义一个特定值或区间值，便于进行异常处理。

**典型场景**

- 业务规则校验：账户余额不足、商品库存不足、用户已存在、订单状态不支持当前操作、验证码错误
- 业务流程阻断：重复提交订单、未实名认证无法发起提现、商品已下架无法购买
- 业务逻辑限制：转账金额超出单日限额、用户账号已冻结

#### 服务端异常 5XX

服务端异常是**由服务自身的代码缺陷、基础设施故障、依赖服务不可用**引发的异常，责任完全在服务提供方，属于非预期的系统级故障。

**典型场景**

- 代码逻辑错误：空指针异常、数组越界、类型转换异常、死循环、算法逻辑 bug

- 基础设施故障：数据库连接失败、Redis 宕机、MQ 消息发送失败、磁盘空间不足

- 依赖服务异常：调用第三方接口超时、内部微服务调用失败、熔断降级触发

- 资源耗尽：线程池耗尽、内存溢出、文件句柄不足

#### 异常分类举例

基于主键id查询用户信息，返回空，属于客户端异常

基于主键id查询到用户信息，但用户信息是加密的只允许特定人员查看，返回业务异常。

基于主键id查询用户信息，数据库不可用，则返回系统异常。



举例说明，一个审批流程，最后一个环节需要部门领导申请，但是部门领导没有该审批系统的权限，导致工单直接被卡住。这种业务异常的稽核规则应该前置，在提单子的时候应直接抛出异常：该流程需要部门领导审批，没有查询到您所属部门领导的账户信息，请核实后在提单子。

#### 架构设计理念

防御性编程：需要对可能发生的异常进行捕获，并处理。

Fail-Fast：外部请求在每一层都进行防御，如果存在异常，直接抛出，避免异常向下传递。

用户友好：所有的底层异常都要封装转换，向用户返回

可观测性：便于对HTTP状态码进行指标采集和监控。



#### 编程设计

这三类在服务端开发范式中，与`Controller-Service-Repository`三层对应。

【Controller-Service-Repository三层架构】

Controller：

Service：

Respository：





**异常层次架构**

```
Exception (Python内置顶层父类，所有异常根节点，仅作为底层捕获源)
└─ AppBaseException (可选抽象基类，封装通用属性：错误码/提示/HTTP状态码，推荐使用)
   ├─ ClientException (客户端异常根类，接口层抛出)
   │  ├─ ValidationException (参数校验：格式/非空/范围错误)
   │  ├─ AuthenticationException (认证：未登录/Token过期/认证失败)
   │  └─ AuthorizationException (授权：无接口/资源操作权限)
   │
   ├─ BizException (业务异常根类，业务层抛出)
   │  ├─ BusinessRuleException (通用业务规则：余额/库存不足、规则校验失败)
   │  ├─ ResourceException (资源：不存在/已被占用/已删除)
   │  └─ StateException (状态：订单/商品状态不支持当前操作)
   │
   └─ ServerException (服务端异常根类，数据/依赖层抛出，承接所有系统异常转换)
      ├─ InfrastructureException (基础设施异常：数据库/缓存/MQ/文件系统故障)
      ├─ ExternalServiceException (外部服务异常：第三方/内部平台调用超时/连接失败)
      ├─ UnexpectedException (预期内系统异常：可捕获的原生异常转换，如KeyError/IndexError)
      └─ UnknownException (未知异常：未专门处理的原生异常/未预见异常，最终兜底)
```

自定义异常设计实践：

> 避免过度设计，参数可根据业务需求添加

```python
@dataclass
class AppException(Exception)
    message: str
    error_code: str  # 业务错误码
    http_status: int = 200  # HTTP状态码
    details: dict | None = None # 异常详情，上下文信息

@dataclass
class ClientException(AppException)
		message = "客户端异常"
  	http_status = 400

@dataclass
class BizException(AppException)
		message = "业务异常"
    http_status = 299

@dataclass
class ServerException(AppException)
		message = "服务器异常"
  	http_status = 500
```


