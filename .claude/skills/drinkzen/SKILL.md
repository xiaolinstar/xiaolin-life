---
name: drinkzen
description: 饮品运营：按官方小程序菜单维护 Hugo 品牌与饮品页、drinkzen.cn 后台，生成小红书和大众点评共用 plog，记录发布、同步、纠错与复盘。
license: MIT
metadata:
  version: "2.2.0"
  author: xiaolin
  tags: ["drinkzen", "beverage", "tea", "milktea", "brand", "plog"]
---

# DrinkZen

从菜单核实、内容创作、后台维护到社媒发布与复盘的工作流。

## 工作流概览

| 阶段 | 输入 | 动作 | 产出 |
| --- | --- | --- | --- |
| 1. 菜单核实 | 品牌官方小程序 | 记录单品菜单、选项、价格、截图 | `menu.json` + `gallery/menu-screenshot.png` |
| 2. 营养计算 | 菜单 + 营养资料 | 搜索营养数据，计算配方营养表，推导评级 → **交叉校验** | 正文「营养与评级依据」段 |
| 3. 内容完善 | 前两步产出 | 补充制作方式、口感体验、点单提示 | 完整正文 |
| 4. 社媒分发 | 完整正文 + 已知热量/评级 | 生成共用 plog（标题/正文/标签/评论） | 正文末尾 `## plog 分发版` |
| 5. 发布跟踪 | 真实发布链接 | 记录发布事实，跟踪纠错与复盘 | 运营台账 |

**发布前提**：热量和评级已知才具备 plog 发布条件；数据不足时先完成计算，不发布「待核实」版本的 plog。

## 核心原则

### 计算模型优先

DrinkZen 的评测价值在于计算模型的一致性和客观性。

- 从参数表（原料用量 × 每 100ml 营养值）计算和推导结论，即使不完全准确也要给出结果
- 外部参考（检测报告、品牌官网、博主实测）放到参考资料区，供作者审查
- 计算模式不能变——这是保证所有饮品评测方法客观一致的基础
- Front matter 的评级从正文计算结果抽取，计算得出 C 级就写 C 级

### 正文与元数据分离

- **正文（index.md）**：只放读者需要的内容（产品速览、菜单选项、营养计算、口感体验、点单提示）
- **元数据**：存到 `menu.json`（菜单结构化数据）和 `gallery/`（截图证据）
- 正文不放采集日期、门店、操作日志等元信息

### 证据分级

| 类别 | 举例 | 处理方式 |
| --- | --- | --- |
| 品牌公开事实 | 供应商、原料种类、品牌历史 | 直接写，标来源 |
| 菜单事实 | 选项、默认值、加价 | 对照截图核实后写 |
| 计算推导 | 配方营养表、评级 | 保留计算结构，标注假设 |
| 第三方数据 | 检测报告、博主实测 | 放参考资料区，标注来源 |
| 作者体验 | 口感、风味描述 | 无实饮记录时不编 |

### 安全边界

- 后台写入先运行 `--dry-run --json`；已有用户授权覆盖该变更时继续执行，否则取得确认
- 不补造配方克重、体验、菜单选项或评级
- 不提供孕妇相关建议，不给「安全」「随便喝」等保证
- 本地运营台账的维护不代表已获得线上发布、后台写入或 Git 提交授权

## 阶段 1：菜单核实

**目标**：确认品牌官方小程序里该饮品的实际菜单选项。

### 具体动作

1. 打开品牌官方小程序，定位到目标饮品
2. 记录以下信息：
   - 品牌名、饮品官方名称（中英文）
   - 每个选项组：名称、可选值、默认值、单选/多选、加价
   - 价格（默认配置）
   - 产品描述（小程序上的文字说明）
3. 截图保存（包含饮品名、选项、价格）
4. 记录采集日期和数据来源

### 产出

**menu.json**（单品级菜单数据）：

```json
{
  "slug": "iced-latte",
  "brand": "Manner Coffee",
  "product": "冰拿铁 Iced Latte",
  "source": "official-miniapp",
  "collectedAt": "2026-10-11",
  "screenshot": "gallery/menu-screenshot.png",
  "options": [
    {
      "group": "规格",
      "key": "size",
      "selectionType": "single",
      "values": [
        {"label": "大冰杯 355ml", "default": true, "price": 0}
      ]
    }
  ],
  "defaultPrice": 20
}
```

**字段说明**：

- `slug`：与目录名、URL 一致的英文标识（kebab-case）
- `source`：`official-miniapp` / `official-website` / `third-party-report` / `blogger-test`
- `options[].selectionType`：`single`（单选）或 `multiple`（多选）
- `options[].values[].default`：布尔值，标记默认选项
- `options[].values[].price`：加价金额（元），默认选项为 0

**gallery/menu-screenshot.png**：菜单截图证据

### 易错点

- **把品牌通用模板当成单品实际选项**：比如冰美式根本没有换奶选项，不能补进去
- **用旧截图代替当前菜单**：菜单可能已变更，必须用最新截图
- **把独立饮品当成选项**：比如「燕麦拿铁」是独立单品，不是「拿铁」的换奶选项
- **未核实就写菜单事实**：比如「换燕麦奶 +5 元」必须从截图确认，不能从经验推断

### 正文写法

菜单核实完成后，在 `index.md` 中填写：

```markdown
## 产品速览

- **品牌 / 菜单项**：Manner Coffee / 冰拿铁 Iced Latte
- **系列**：Classic Coffee（经典咖啡系列）
- **默认配置**：大冰杯 355ml，牛奶，正常冰，默认浓度
- **价格**：¥20（默认配置）

## 菜单选项

| 选项组 | 可选值 | 默认值 | 加价 |
| --- | --- | --- | --- |
| 规格 | 大冰杯 355ml | 大冰杯 355ml | — |
| 奶搭配 | 牛奶 | 牛奶 | — |
| 冰 | 正常冰 / 少冰 / 去冰 | 正常冰 | — |
| 咖啡浓度 | 默认(推荐) / 低浓度 / 额外一份浓缩 / 额外两份浓缩 | 默认(推荐) | +¥5 / +¥5 |

**说明**：
- 无糖度选项
- 无换燕麦奶/脱脂奶选项
```

**注意**：正文只放读者需要的信息；采集日期、门店、截图路径等元数据放在 `menu.json`。

---

## 阶段 2：营养计算与评级

**目标**：根据菜单配方和原料营养数据，计算每 100ml 营养表，推导新加坡 Nutri-Grade 评级。

### 具体动作

1. **确定配方比例**
   - 根据杯容和菜单默认配置，推算各原料用量（浓缩咖啡 ml、牛奶 ml、冰 g）
   - 有效体积 = 杯容（冰块融化后计入总液体）
   - 品牌特定规格优先于行业通用值（如 Manner 一份浓缩 = 30ml，非通用双份 40ml）

2. **搜索原料营养数据**
   - 牛奶：查品牌营养成分表（foodtalks.cn、产品包装等），记录每 100ml 各项数值
   - 浓缩咖啡：行业通用值（热量极低，可近似忽略）
   - 饱和脂肪：中国标签不强制标注时，按乳制品脂肪酸组成研究推算（总脂肪 × 62-65%）

3. **计算配方营养表**
   - 各原料用量 × 每 100ml 营养值 = 该原料贡献量
   - 汇总后除以有效体积 × 100 = 每 100ml 数值

4. **推导评级**
   - **新加坡 Nutri-Grade**：
     - 糖扣减：总糖 − 有依据的乳糖/半乳糖 = 计入评级的糖（无依据不扣）
     - 按阈值判定糖等级和饱和脂肪等级，取较差项
     - 含非糖甜味剂时不能评 A
   - **上海"营养选择"**：
     - 糖口径：非乳源性糖（直接排除乳糖，不经过"总糖 − 乳糖"步骤）
     - 四项指标全部评定：非乳源性糖、饱和脂肪、反式脂肪、非糖甜味剂
     - 短板原则取最差项

5. **计算不同配置对比**
   - 遍历菜单中的浓度/杯型选项，计算各配置下的营养和评级
   - 确认评级是否因配置变化

### 产出

写入 `index.md` 的「营养与评级依据」段，包含：

- **配方营养计算表**：原料 → 各项营养 → 合计 → 每 100ml
- **新加坡 Nutri-Grade 评级表**：糖（扣减后）+ 饱和脂肪 → 最终评级
- **上海"营养选择"评级表**：非乳源性糖 + 饱和脂肪 + 反式脂肪 + 甜味剂 → 最终评级
- **不同浓度配置对比表**：各配置的热量、双评级
- **数据依据表**：每条数据的来源、类型、置信度
- **参考资料**：外部链接

### 交叉校验（自检 + 用户确认）

计算完成后，执行 Agent 按检查表自检，将结果附在输出末尾供用户审查。

| 检查项 | 自检内容 | 典型问题 |
| --- | --- | --- |
| 配方合理性 | 浓缩量是否符合该品牌实际规格？各原料之和是否等于杯容？ | 用通用双份 40ml 代替品牌实际 30ml |
| 数据一致性 | 每 100ml 数值 = 合计 ÷ 体积 × 100？不同配置的数值变化方向是否正确？ | 牛奶多了糖反而降了 |
| 新加坡糖扣减 | 总糖是否已扣减乳糖/半乳糖？扣减依据是否标注？计入评级的糖是否正确？ | 总糖 3.29g 直接判 B，未扣减乳糖（实际全为乳糖，应为 0→A） |
| 上海糖口径 | 是否使用非乳源性糖（排除乳糖）而非总糖？四项指标是否全部评定？ | 用总糖代替非乳源性糖，或漏评反式脂肪/甜味剂 |
| 阈值与取差 | 两套标准的阈值是否分别应用（不混用）？是否取较差项？甜味剂规则是否检查？ | 新加坡饱和脂肪 C + 糖 A 写成 B；上海阈值用新加坡的 |
| 置信度标注 | 推算值是否标了置信度？是否有数据被当成确定值写入？ | 饱和脂肪推算值未标注 |
| 菜单一致性 | 正文选项表与 menu.json 是否一致？加价、默认值是否匹配？ | 正文写"无换奶"但 menu.json 有换奶选项 |

**自检流程**：

1. 计算完成后，逐项过检查表
2. 每项标记状态：
   - **已核实**：有明确证据支持（如品牌官方数据、截图确认）
   - **推算/估算**：标注了置信度，数值合理但非精确
   - **存疑**：使用行业通用值但未核实品牌特定规格，或数据源不够可靠
3. 将自检结果以清单形式附在输出末尾，**存疑项加粗提醒用户关注**
4. 用户审查时重点看存疑项，确认或要求修正

**自检输出示例**：

```text
自检结果：
- [已核实] 配方合理性：Manner 一份浓缩 30ml，据豆瓣/大众点评用户核实客服
- [已核实] 数据一致性：每 100ml = 合计 ÷ 355 × 100，各配置变化方向正确
- [已核实] 新加坡糖扣减：总糖 3.29g 全为乳糖，扣减后 0g → A，依据：牛奶碳水全为乳糖
- [已核实] 上海糖口径：非乳源性糖 = 0g（无添加糖/果汁）→ A；四项指标全部评定
- [已核实] 阈值与取差：新加坡糖 A + 饱和脂肪 C → C ✓；上海短板 B ✓；两套阈值未混用
- [推算/估算] 饱和脂肪：牛奶总脂肪 × 63%，置信度中
- **存疑** 咖啡因 60mg/份：使用行业通用值，未找到 Manner 官方数据
```

**高风险场景可启用独立 subagent 审核**：

- 批量创建多个饮品页时
- 评级结果与历史记录差异大时
- 用户对自检结果有疑问时

### 易错点

- **用行业通用值代替品牌特定规格**：不同品牌的浓缩量、牛奶品牌不同，必须核实
- **饱和脂肪未标注推算**：中国标签不强制标示，推算值必须标置信度
- **有效体积算错**：冰饮按杯容（冰融化后），不按液体量
- **评级取错项**：取糖和饱和脂肪中较差的，不是取较好的
- **配置对比漏算**：额外浓缩/换杯型后的营养变化要逐配置计算

---

## 阶段 3：内容完善

**目标**：补充制作方式、口感体验、点单提示，使正文完整可读。

### 各段来源

| 段落 | 来源 | 说明 |
| --- | --- | --- |
| 制作方式调查 | 菜单 + 行业常识 | 3-5 步简述，不展开工艺细节 |
| 口感体验 | Agent 起草 → 用户确认 | 简短自然，像真人评价；用户可修改或替换为实饮记录 |
| 点单与饮用提示 | 菜单选项 + 营养结果 | 提醒浓度、咖啡因、换奶限制等 |
| 数据依据 + 参考资料 | 阶段 1-2 产出汇总 | 已在阶段 2 完成 |

### 口感体验写法

- Agent 默认起草一段简短体验（2-3 句），写入正文
- 提示用户：如有实饮体验可替换，无则保留 Agent 版本
- 语气自然，不写工艺说明，不用"丝滑""醇厚"等空泛词
- 可提及温度、苦甜平衡、奶感强弱等具体感受

---

## 阶段 5：发布跟踪

**目标**：记录真实发布事实，跟踪纠错与复盘，形成运营闭环。

### 前提

- 阶段 4 已完成（plog 已生成）
- 用户已在小红书/大众点评实际发布，或已完成线上纠错
- **不能**在仅生成文案时执行 `record`——必须有真实链接和时间

### 具体动作

#### 5.1 关联后台产品（link）

登记 DrinkZen 后台产品 ID 和菜单证据，建立 origin 与后台的关联。

```bash
python3 scripts/drinkzen-operations.py link \
  --article content/drinkzen/manner/iced-latte/index.md \
  --product-id PRODUCT_ID \
  --menu-evidence gallery/menu-screenshot.png \
  --menu-checked-at 2026-10-11
```

- `--product-id`：DrinkZen 后台实际产品 ID（不明时留空）
- `--menu-evidence`：菜单截图路径（与 menu.json 的 screenshot 一致）
- `--menu-checked-at`：菜单核实日期

#### 5.2 登记发布（record）

实际发布后，登记平台链接和时间。每个平台各一条记录。

```bash
python3 scripts/drinkzen-operations.py record \
  --article content/drinkzen/manner/iced-latte/index.md \
  --platform xiaohongshu \
  --url https://www.xiaohongshu.com/explore/ACTUAL_POST_ID \
  --published-at 2026-10-11T14:30:00+08:00 \
  --note 首次发布
```

- `--platform`：`xiaohongshu` 或 `dianping`
- `--url`：实际发布链接（不能编造）
- `--published-at`：ISO 8601 格式时间
- `--note`：发布说明（首次发布 / 纠错 / 更新等）

记录会自动保存 origin 和 plog 的 SHA-256 摘要，用于后续版本比对。

#### 5.3 登记效果数据（metrics）

发布后约 24 小时、7 天收集平台数据。

```bash
python3 scripts/drinkzen-operations.py metrics \
  --article content/drinkzen/manner/iced-latte/index.md \
  --platform xiaohongshu \
  --observed-at 2026-10-12T14:30:00+08:00 \
  --views 100 --likes 5 --saves 2 \
  --note 24小时数据
```

- 未知值不填（不填为 null，不当作 0）
- 可记录字段：`--views` `--likes` `--saves` `--comments` `--profile-visits` `--miniapp-visits` `--product-queries`
- 小程序访问等归因数据需实际埋点证据，不能从笔记浏览量推算

#### 5.4 登记跟进事项（note）

外部菜单变化但正文尚未修正时，登记待办。

```bash
# 登记跟进事项
python3 scripts/drinkzen-operations.py note \
  --article content/drinkzen/manner/iced-latte/index.md \
  --text "菜单已变更：新增换燕麦奶选项，待核对正文和后台"

# 处理完成后标记解决
python3 scripts/drinkzen-operations.py note \
  --article content/drinkzen/manner/iced-latte/index.md \
  --resolved
```

#### 5.5 查看状态（status）

```bash
python3 scripts/drinkzen-operations.py status
```

输出示例：

```text
content/drinkzen/manner/iced-latte/index.md: menu=已核实 product=已关联 xiaohongshu=已发布(2026-10-11) / dianping=未登记
```

状态含义：

- `menu=未核实`：台账未登记菜单证据
- `menu=已核实`：已登记菜单证据和核实日期
- `product=待关联`：未登记后台产品 ID
- `product=已关联`：已登记后台产品 ID
- `xiaohongshu=未登记`：未发布
- `xiaohongshu=已发布(日期)`：已登记发布链接
- `xiaohongshu=待同步`：origin/plog 版本与记录不一致，需重新发布

### 产出

运营台账 `data/drinkzen-operations.json`，结构：

```json
{
  "schema_version": 1,
  "articles": {
    "content/drinkzen/manner/iced-latte/index.md": {
      "product_id": "abc123",
      "menu_evidence": "gallery/menu-screenshot.png",
      "menu_checked_at": "2026-10-11",
      "followup": null,
      "platforms": {
        "xiaohongshu": {
          "history": [
            {
              "url": "https://www.xiaohongshu.com/explore/xxx",
              "published_at": "2026-10-11T14:30:00+08:00",
              "origin_sha": "sha256:...",
              "plog_sha": "sha256:...",
              "note": "首次发布",
              "metrics": [
                {
                  "observed_at": "2026-10-12T14:30:00+08:00",
                  "views": 100,
                  "likes": 5,
                  "saves": 2,
                  "note": "24小时数据"
                }
              ]
            }
          ]
        }
      }
    }
  }
}
```

### 纠错流程

1. 发现菜单/营养数据/评级需修正 → 更新 origin 和 plog
2. `status` 检出 origin/plog 摘要变化 → 已发布平台显示"待同步"
3. 在各平台完成线上修正
4. 用 `record` 登记修正链接和时间（history 保留旧版本记录）
5. `status` 恢复"已发布"

### 易错点

- **在仅生成文案时执行 record**：必须有真实链接和时间才能记录
- **把 draft: false 当作已发布**：draft 状态不等于发布状态，必须以台账记录为准
- **编造小程序归因数据**：小程序访问、搜索等需实际埋点，不能从笔记浏览量推算
- **用观测时间 0 填充未知值**：未知值留空（null），不当作 0
- **台账不提交 Git**：运营台账须与内容一起备份/提交

---

## 后台维护（独立模块，待迭代）

> **说明**：本节与主干流程（阶段 1-5）独立，按需调用。当前 drinkzen-admin 功能尚不成熟，后续会持续迭代。

**适用场景**：

- 批量关联饮品页与 drinkzen.cn 后台产品 ID
- 同步 Hugo 页面的评级/营养数据到后台
- 校验后台数据与 Hugo 页面的一致性
- 批量更新品牌或饮品元信息

**操作前检查**：

1. 确认目标饮品页已完成阶段 1-2（菜单已核实、评级已计算）
2. 读取 `data/drinkzen-operations.json` 查看当前关联状态
3. 运行 `python3 scripts/drinkzen-operations.py status` 确认待处理项

**核心动作**：

| 动作 | 说明 | 命令示例 |
| --- | --- | --- |
| link | 关联后台产品 ID | `drinkzen-admin link --page <path> --product-id <id>` |
| sync | 同步评级到后台 | `drinkzen-admin sync --brand <brand> --dry-run` |
| verify | 校验数据一致性 | `drinkzen-admin verify --all` |
| update | 批量更新元信息 | `drinkzen-admin update --brand <brand> --field <field>` |

**安全约束**：

- 所有写入操作先运行 `--dry-run --json`，确认无误再执行
- 已有用户授权覆盖的变更可直接执行，否则需确认
- 后台操作记录写入 `data/drinkzen-operations.json` 的 `admin_log` 字段

**API 参考**：详见 [admin.md](references/admin.md)

---

## 按任务读取

| 任务 | 参考 |
| --- | --- |
| 品牌页、单品页、菜单映射 | [content.md](references/content.md) |
| 评级或营养数据 | [ratings.md](references/ratings.md) + [search-guide.md](references/search-guide.md) |
| 后台资料、菜单模板、投稿审核 | [admin.md](references/admin.md) |
| 两平台共用 plog | [social 入口](references/README.md) + [plog 模板](templates/plog-template.md) |
| 发布记录、同步纠错、效果复盘 | [operations.md](references/operations.md) |
