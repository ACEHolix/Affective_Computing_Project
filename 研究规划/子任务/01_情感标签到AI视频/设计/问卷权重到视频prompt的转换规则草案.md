# 问卷权重到视频 prompt 的转换规则草案

日期：2026-04-01

## 文档目的

本文件用于回答：

- 问卷得到的分数、权重和偏好字段，如何转成 AI 视频生成模型更容易理解的 prompt
- 为什么不建议直接把数字权重原样塞给模型
- 更稳妥的转换流程应该如何设计

## 先给结论

对于大多数通用 AI 视频生成模型，当前更稳的方式不是：

- 直接在 prompt 中写很多数字权重

而是：

1. 先在系统内部用数字做计算
2. 再把数字转成离散标签和语言描述
3. 再把这些语言描述组织成结构化 prompt

也就是说：

- `数字` 更适合内部排序
- `自然语言` 更适合喂给生成模型

## 一、为什么不建议直接把数字塞给模型

### 1. 通用视频生成模型通常不保证支持显式权重语法

例如：

- `beach:0.8`
- `sadness=0.7`
- `warm light=0.9`

这类写法如果模型文档没有明确说明支持，通常不会稳定生效。

### 2. 数字与视觉结果通常不是线性关系

即使模型能“看懂”一点数字，也不能假设：

- `0.7` 和 `0.8` 会稳定地产生清晰差异

### 3. 多个数字条件一起出现时容易冲突

例如：

- 海边 0.8
- 雨夜 0.7
- 复古 0.9
- 紧张 0.6
- 平静 0.5

模型常常不会像规则系统一样精确整合它们。

## 二、推荐的总体转换流程

当前建议把转换分成 5 步：

1. 问卷字段编码
2. 内部权重计算
3. 权重离散化
4. 标签到 prompt 片段映射
5. prompt 组装与候选排序

## 三、步骤 1：问卷字段编码

问卷输出的原始字段可以是：

- `preferred_scene_types`
- `preferred_visual_styles`
- `preferred_audio_elements`
- `emotion_theme_trigger_matrix`
- `theme_blacklist`
- `self_relevant_scenes`
- `sample_feedback_scores`

这些字段在系统内部先保持数值化。

例如：

```json
{
  "scene_weights": {
    "seaside": 0.85,
    "rainy_street": 0.72,
    "crowded_mall": 0.10
  },
  "style_weights": {
    "cinematic": 0.80,
    "nostalgic": 0.76,
    "anime": 0.20
  }
}
```

## 四、步骤 2：内部权重计算

### 作用

- 让不同来源的信号先在系统内部融合

### 可能融合的来源

1. 问卷显式偏好
2. 自我相关线索
3. 样例反馈
4. 风险约束
5. 阶段目标情绪

### 示例

某个阶段的场景总权重可以来自：

- 偏好分
- 自我相关加权
- 阶段情绪适配分
- 黑名单惩罚

例如：

```text
scene_score =
0.35 * preference_score +
0.30 * self_relevance_score +
0.25 * stage_emotion_match +
0.10 * sample_feedback_score -
blacklist_penalty
```

## 五、步骤 3：权重离散化

### 目的

- 把连续数字转成模型更容易“听懂”的等级描述

### 推荐离散档位

- `0.00 - 0.19` -> avoid
- `0.20 - 0.39` -> weak
- `0.40 - 0.59` -> moderate
- `0.60 - 0.79` -> strong
- `0.80 - 1.00` -> dominant

### 示例

如果：

- `seaside = 0.85`
- `rainy_street = 0.72`
- `crowded_mall = 0.10`

则转成：

- dominant seaside setting
- strong rainy street atmosphere
- avoid crowded mall scenes

## 六、步骤 4：标签到 prompt 片段映射

这一层是关键。

不要直接把所有词堆到一句话里，而应先把标签映射成不同类型的 prompt 片段。

## 1. 场景层

输入标签：

- `seaside`
- `rainy_street`
- `empty_room`

输出 prompt 片段：

- empty seaside road at dusk
- quiet rainy street at night
- dim personal room interior

## 2. 情绪层

输入标签：

- `positive_high_arousal`
- `low_arousal_negative`
- `recovery_to_neutral`

输出 prompt 片段：

- emotionally uplifting and energizing
- low-arousal melancholy and lonely atmosphere
- gradual emotional recovery toward calm neutrality

## 3. 风格层

输入标签：

- `cinematic`
- `nostalgic`
- `warm_low_saturation`

输出 prompt 片段：

- cinematic visual storytelling
- nostalgic film-like tone
- warm low-saturation color palette

## 4. 镜头层

输入标签：

- `slow_pacing`
- `long_take`
- `high_tension_camera`

输出 prompt 片段：

- slow camera movement
- long takes with gentle tracking
- increasing camera tension and tighter framing

## 5. 音频层

输入标签：

- `piano`
- `ambient_rain`
- `low_frequency_tension`

输出 prompt 片段：

- soft piano-driven soundtrack
- subtle rain ambience
- restrained low-frequency tension

## 6. 约束层

输入标签：

- `no_crowds`
- `no_hospital`
- `no_fast_flash`

输出 prompt 片段：

- avoid crowds
- avoid hospital-related imagery
- no flashing or rapid strobe-like cuts

## 七、步骤 5：prompt 组装

### 推荐结构

最终 prompt 建议按固定模板拼接：

1. `stage goal`
2. `scene`
3. `narrative / event`
4. `mood`
5. `visual style`
6. `camera / pacing`
7. `audio`
8. `avoid`

### 示例模板

```text
Stage goal:
Create a stage-1 positive activation video.

Scene:
An empty seaside road at dusk with open space and gentle wind.

Narrative:
A subtle sense of anticipation and reward, moving toward emotional uplift.

Mood:
Bright, uplifting, energizing.

Visual style:
Cinematic, nostalgic, warm low-saturation lighting.

Camera:
Slow forward tracking shot with gradually increasing energy.

Audio:
Soft piano with expanding ambient texture.

Avoid:
Crowds, hospital imagery, harsh noise, flashing edits.
```

## 八、推荐的映射方式

当前建议组合使用三种映射：

### 1. 标签映射

作用：

- 把问卷结果转成中间语义层

例如：

- `高自我相关海边` -> `scene = seaside`
- `低唤醒负向` -> `mood = melancholy`

### 2. 模板映射

作用：

- 把阶段目标组织成稳定的 prompt 框架

例如：

- 阶段 1 使用正向激活模板
- 阶段 3 使用低唤醒负向模板
- 阶段 5 使用恢复模板

### 3. 排序映射

作用：

- 对多个候选 prompt 或候选视频进行个体化排序

也就是说：

- prompt 不是只生成 1 个
- 可以先生成 3 到 5 个候选，再根据画像分数选最优

## 九、推荐的五阶段 prompt 转换思路

## 阶段 1：正向激活

高权重字段更适合映射到：

- 明亮场景
- 奖励感事件
- 节奏增强
- 上升型音乐

## 阶段 2：正向缓和

高权重字段更适合映射到：

- 保持正向但更稳定的场景
- 降低节奏
- 更开阔和安全的构图

## 阶段 3：低唤醒负向

高权重字段更适合映射到：

- 离别
- 错过
- 独处
- 空旷场景
- 稀疏音频

## 阶段 4：负向强化

高权重字段更适合映射到：

- 压迫感
- 不确定性
- 更强张力
- 高 arousal 负性线索

## 阶段 5：恢复段

高权重字段更适合映射到：

- 安全线索
- 稳定节奏
- 低冲突场景
- 柔和环境音

## 十、当前最推荐的系统做法

对于子任务 01，当前最推荐的是：

### 系统内部

- 用数字做：
  - 权重融合
  - 标签排序
  - 黑名单过滤
  - 候选选择

### 输出给模型时

- 用自然语言做：
  - 场景描述
  - 情绪描述
  - 风格描述
  - 镜头描述
  - 音频描述
  - 禁止项描述

## 十一、当前结论

最稳妥的做法不是：

- 问卷分数 -> 直接写进 prompt 里的数字

而是：

- 问卷分数 -> 系统内部权重
- 系统内部权重 -> 离散标签
- 离散标签 -> prompt 片段
- prompt 片段 -> 阶段化视频 prompt

这条路线更符合当前通用 AI 视频生成模型的实际使用方式，也更适合做可解释的研究系统。

## 下一步建议

下一步最适合继续补的文档有两个：

1. 五阶段每个阶段的 prompt 模板草案
2. 问卷字段到内容标签的映射表示例
