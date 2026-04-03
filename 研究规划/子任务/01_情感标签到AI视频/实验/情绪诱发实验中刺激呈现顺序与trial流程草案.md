# 情绪诱发实验中刺激呈现顺序与 trial 流程草案

日期：2026-03-31

## 文档目的

本文件用于回答：

- 在情绪诱发相关论文中，刺激一般按照什么顺序出现
- 为什么实验中不能随意排列刺激
- 如果迁移到子任务 01 的视频诱发实验，推荐采用什么 trial 流程和 block 设计

## 先给结论

情绪诱发实验中的刺激顺序通常不会随意安排。

研究者一般会控制以下几个问题：

1. 顺序效应
2. 残留情绪
3. 习惯化
4. 疲劳
5. 评分偏移

因此，主流论文中最常见的设计是：

- baseline
- fixation
- stimulus
- rating
- recovery / washout

同时在整体顺序上采用：

- randomized
- counterbalanced
- pseudo-randomized
- block design

## 一、为什么刺激顺序很重要

如果刺激顺序不加控制，常见问题包括：

### 1. 前一条刺激会污染后一条刺激

例如：

- 刚看完强烈悲伤片段
- 下一条中性视频的评分可能也会偏负

### 2. 连续同类型刺激会导致习惯化

例如：

- 连续多个恐惧刺激后，后续反应可能逐渐变弱

### 3. 后半段更容易疲劳

例如：

- 后面的刺激可能只是因为被试累了而评分下降

### 4. 强负性刺激可能带来伦理和恢复问题

例如：

- 实验结束时仍停留在强负性状态

因此，大多数论文会在顺序设计上做控制。

## 二、文献中最常见的单 trial 顺序

## 1. 基线期

常见形式：

- 静息注视
- 空屏
- fixation cross

常见时长：

- 10 到 60 秒

目的：

- 记录基线生理状态
- 让被试从上一 trial 恢复

## 2. 准备提示 / fixation

常见形式：

- 注视十字
- “请准备观看下一条刺激”

常见时长：

- 1 到 5 秒

目的：

- 统一进入刺激前的注意状态

## 3. 刺激呈现

常见形式：

- 图片
- 音乐
- 电影片段
- VR 视频

常见时长：

- 图片：1 到 6 秒
- 电影片段：20 到 120 秒
- VR 刺激：更长，常见几十秒到几分钟

## 4. 即时评分

常见形式：

- SAM
- valence / arousal 评分
- discrete emotion rating
- 强度评分

常见时长：

- 5 到 20 秒

目的：

- 尽可能在情绪尚未消退前采集主观反应

## 5. 恢复期 / washout

常见形式：

- fixation
- 中性空屏
- 休息

常见时长：

- 10 到 30 秒

目的：

- 尽量减弱上一刺激的 carryover effect

## 三、整体刺激顺序的常见设计

## 1. 完全随机

做法：

- 所有刺激随机打乱

优点：

- 简单

缺点：

- 可能连续出现过多同类型刺激
- 不一定能有效控制情绪残留

适用情况：

- 图片类、短刺激类实验更常见

## 2. 伪随机

做法：

- 整体随机
- 但增加约束，例如：
  - 不允许 3 个强负性连续出现
  - 不允许同一情绪类别连续出现过多

优点：

- 比完全随机更稳

适用情况：

- 视频刺激实验最常用

## 3. 平衡 / counterbalance

做法：

- 不同被试使用不同刺激顺序
- 或 block 顺序互换

优点：

- 可以减弱固定顺序带来的系统偏差

适用情况：

- 样本量足够时
- 条件数较少时

## 4. block design

做法：

- 先按条件分 block
- block 内再随机或伪随机

优点：

- 便于 EEG/fMRI/EDA 分析
- 便于实验控制

缺点：

- 容易出现 block 内情绪堆积

适用情况：

- 当实验更关注条件间比较，而不是完全自然化体验

## 四、不同刺激材料常见的顺序模式

## 1. 图片刺激

常见顺序：

- fixation
- image
- rating
- short inter-trial interval

特点：

- 易于随机化
- carryover 相对较小

## 2. 电影片段 / 短视频刺激

常见顺序：

- baseline
- fixation
- clip
- rating
- rest

特点：

- carryover 更明显
- 更需要 recovery
- 更适合伪随机或 block 设计

## 3. VR / 沉浸式刺激

常见顺序：

- baseline
- device adaptation
- stimulus
- retrospective rating
- recovery

特点：

- 沉浸更强
- 残留更明显
- 更需要较长恢复期

## 五、文献支持的几个关键点

### 1. 电影片段更强，但也更容易产生残留效应

参考：

- Emotion Elicitation: A Comparison of Pictures and Films
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4756121/

启发：

- 视频比图片更适合你的项目
- 但必须更认真处理顺序和恢复期

### 2. 电影刺激库研究会特别关注 clip 长度与可恢复性

参考：

- E-MOVIE: Experimental MOVies for Induction of Emotions in neuroscience
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6776321/

启发：

- clip 不宜过长
- 过长会增加 disengagement 难度和后续污染

### 3. affect induction 元分析支持程序设计对效果很重要

参考：

- The manipulation of affect: A meta-analysis of affect induction procedures
  https://pubmed.ncbi.nlm.nih.gov/31971408/

启发：

- 诱发效果不只取决于刺激内容，也取决于程序本身

## 六、对子项目 01 的推荐 trial 流程

如果你要做视频情绪诱发实验，建议先采用如下标准 trial：

### 推荐 trial

1. 基线静息
   - 20 到 30 秒

2. fixation
   - 2 到 3 秒

3. 视频刺激
   - 15 到 45 秒

4. 即时评分
   - valence
   - arousal
   - intensity
   - self-relevance
   - liking

5. 恢复期
   - 15 到 30 秒

### 若采集生理信号

建议额外记录：

- baseline window
- stimulus window
- post-stimulus recovery window

## 七、对子项目 01 的推荐整体顺序

### 推荐方案 A：伪随机 mixed design

做法：

- 所有情绪条件混合
- 但限制：
  - 不连续出现 2 到 3 个强负性刺激
  - 同一情绪类别不连续出现过多

适合：

- 你想更接近真实推荐或真实观看场景

### 推荐方案 B：block + block 内随机

做法：

- 一个 block 一种目标情绪
- block 内刺激顺序随机
- block 顺序在不同被试之间 counterbalance

适合：

- 你更看重实验控制和条件比较

### 推荐方案 C：个体化条件与非个体化条件交叉

做法：

- 同一个被试既看：
  - personalized stimuli
  - generic stimuli
- 顺序做 counterbalance

适合：

- 直接验证“个体化是否优于通用刺激”

## 八、负性刺激的推荐处理方式

对于悲伤、恐惧、厌恶、压迫类视频，建议：

1. 不连续排列多个强负性 trial
2. 中间插 neutral 或低强度刺激
3. 每个负性 trial 后保留足够恢复期
4. 实验尾声使用中性或正性刺激做情绪恢复

原因：

- 降低 carryover
- 降低伦理风险
- 改善被试体验

## 九、如果你的目标是“个体化诱发”

推荐的最小实验比较方式是：

1. 通用刺激条件
2. 基于问卷个性化的刺激条件
3. 基于样例反馈校准后的个性化刺激条件

三种条件之间采用：

- counterbalanced order

每个条件内部采用：

- pseudo-randomized order

这样最容易验证：

- 个体化是否真的提高了诱发强度

## 十、当前结论

在情绪诱发论文中，刺激一般不会随意出现。

最常见的结构是：

- baseline
- fixation
- stimulus
- rating
- recovery

最常见的顺序控制方式是：

- randomization
- pseudo-randomization
- counterbalancing
- block design

如果迁移到子任务 01，最推荐的是：

- 采用视频级 trial
- 每个 trial 后立即评分
- 强负性刺激之间插恢复期
- 用伪随机和 counterbalance 控制顺序

## 下一步建议

下一步最适合继续补的文档有两个：

1. 子任务 01 个体化情绪诱发实验流程总草案
2. 个体化与通用刺激对照实验设计草案
