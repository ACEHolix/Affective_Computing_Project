# Monkey_reward 对接策略

## 文档目的

本文件用于把外部协作文档 `AGENT_COLLAB_GUIDE.md` 落地成当前子任务 3 可直接执行的接入策略。

核心目标不是修改 `Monkey_reward`，而是：

- 复用它已有的数据和运行环境
- 避免污染它的主线 workflow
- 为当前多模态 EEG GNN 子任务提供稳定的数据与环境来源

## 一、当前判断

根据协作文档，`Monkey_reward` 应被视为：

- 带真实数据的科研分析母仓库
- 带容器依赖的真实运行环境仓库
- 已有多个正式 workflow 的长期演化仓库

因此，当前子任务 3 对它的正确使用方式不是“在那边直接开新坑乱改”，而是：

1. 优先复用其已有数据与容器环境
2. 尽量通过绝对路径引用数据与输出目录
3. 如果确实要加新流程，放入独立 workflow
4. 不从 `legacy/` 默认引入新生产逻辑

## 二、与当前子任务 3 的关系

当前子任务 3 已经具备：

- 多模态 GNN 设计方案
- 数据样本组织格式
- 数据读取与导出模板
- 数据划分模板
- cross-subject 实验模板
- 原型代码骨架

而 `Monkey_reward` 更可能提供的是：

- 真实数据来源
- 真实预处理逻辑参考
- 容器运行环境
- 现有实验组织方式

换句话说：

- **本仓库负责新模型设计与新实验组织**
- **Monkey_reward 负责真实环境和现有数据体系**

## 三、推荐接入原则

### 1. 不复制环境

不要在本仓库重建一套与 `Monkey_reward` 平行的复杂环境。

优先方式：

- SSH 到当前机器
- 进入本仓库
- 通过 `senv` 或 `~/senv_auto.sh` 复用容器环境

### 2. 不复制数据

不要把 `Monkey_reward` 的预处理数据复制到本仓库再维护第二份。

优先方式：

- 通过绝对路径访问 `Preprocessed Data/`
- 如有必要，在本仓库只保存轻量索引、配置和映射文件

### 3. 不污染主线 workflow

若后续需要在 `Monkey_reward` 中新增实验流，应优先：

- 新建独立 workflow
- 保持与已有 `mainline_pipeline`、`CNN_Transformer_compare` 解耦

### 4. 不默认依赖 legacy

`legacy/` 只作为：

- 历史逻辑参考
- 对照实现来源
- 旧结果复现入口

不应作为当前新模型代码的默认 import 来源。

## 四、建议环境变量

如果后续要正式对接，建议统一采用以下环境变量：

```bash
export MONKEY_REPO=/home/tuoxiaoying/Documents/Pyproject/Monkey_reward
export MONKEY_DATA="$MONKEY_REPO/Preprocessed Data"
export MONKEY_OUTPUT="$MONKEY_REPO/outputs"
```

如果当前机器上的真实路径不同，后续只需要改这三项，不需要批量改代码。

## 五、当前最推荐的接入方式

### 模式 A：本仓库主导，远程复用环境

适合当前阶段。

执行逻辑：

1. 在本仓库维护新模型设计、配置和实验脚本
2. 运行时进入 `Monkey_reward` 对应容器环境
3. 通过绝对路径读取 `Monkey_reward` 数据
4. 输出结果到本仓库或约定输出目录

优点：

- 本仓库结构清晰
- 不污染母仓库
- 方便后续继续迭代模型

### 模式 B：在 Monkey_reward 中新建独立 workflow

适合后期进入正式实验阶段。

适用条件：

- 当前原型已经稳定
- 明确要跑真实完整流程
- 需要复用其现成训练和评估链路

建议目录形式：

```text
workflows/multimodal_gnn_baseline/
```

至少包含：

- `README.md`
- `TASK_MANUAL.md`
- `preprocess.py`
- `dataset.py`
- `runner.py`
- `run.sh`
- 可选 `model_*.py`

## 六、对当前子任务 3 的直接落地建议

当前最合理的推进顺序是：

1. 先在本仓库完成真实数据字段映射
2. 确认 `Monkey_reward` 中真实数据目录结构
3. 把本仓库的 `io_templates.py` / `export_dataset.py` 改成真实适配版
4. 只在需要真实跑通时，进入容器环境验证
5. 如果后续需要长期维护，再考虑反向沉淀到 `Monkey_reward/workflows/`

## 七、当前不建议立即做的事

- 不建议现在就把子任务 3 整套代码搬进 `Monkey_reward`
- 不建议现在就从 `legacy/` 到处 import
- 不建议因为宿主环境缺 `torch` 就判断 `Monkey_reward` 或当前原型有问题
- 不建议在未看 `git status --short` 的情况下改 `Monkey_reward` 里的现有 workflow

## 八、对当前代码原型的具体影响

后续如果进入真实数据适配，优先需要对接的是本仓库这些文件：

- `代码原型/src/io_templates.py`
- `代码原型/src/export_dataset.py`
- `代码原型/src/preprocess.py`
- `代码原型/src/split_dataset.py`
- `代码原型/configs/preprocess.yaml`

这些文件应当：

- 保持路径配置外置
- 不写死本地临时路径
- 支持从 `MONKEY_DATA` 读取输入

## 九、当前结论

对当前子任务 3 来说，`Monkey_reward` 最合适的角色是：

**数据与容器环境母仓库**

当前本仓库最合适的角色是：

**新模型、新实验设计与新原型实现工作区**

这两个仓库的关系应当是：

**松耦合复用，而不是硬耦合混写**

## 十、当前机器上的首次验证结果

当前已经在本仓库中新增并执行了：

- `代码原型/scripts/connect_monkey_reward.py`
- `代码原型/scripts/try_enter_monkey_env.sh`

首次验证结果如下：

- 默认候选路径下未发现 `Monkey_reward` 仓库
- 当前机器未发现 `senv`
- 当前机器未发现 `~/senv_auto.sh`

因此，当前结论不是“协作文档失效”，而是：

1. 当前机器和协作文档中的目标环境不是同一台
2. 或者真实路径与文档示例路径不一致

当前最合理的下一步是：

- 明确真实 `MONKEY_REPO` 路径
- 明确真实容器入口脚本位置
- 然后重新运行接入脚本和环境进入脚本
