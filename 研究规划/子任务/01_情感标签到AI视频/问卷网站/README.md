# 问卷网站原型

## 目的

这是子任务 01 的最小问卷网站原型，用于：

- 收集用户画像
- 导出结构化问卷答案
- 为后续的个体化视频生成和实验设计提供输入

## 当前功能

- 首页说明页
- 多步骤正式版问卷
- 管理员页面，可查看提交结果
- 单选、多选、评分、矩阵评分、文本题
- 浏览器本地自动保存
- 提交后导出 JSON
- 提交后自动生成用户画像 JSON
- 提交后自动生成五阶段 prompt package
- 本地保存答卷到 `data/submissions/`

## 启动方式

```bash
npm install
npm run dev
```

默认地址：

- `http://localhost:3000`

## 构建验证

```bash
npm run build
```

## 目录结构

- `app/`
  - 页面和全局样式
- `components/SurveyForm.tsx`
  - 多步骤问卷表单主体
- `lib/survey-schema.ts`
  - 问卷 schema 定义
- `lib/submission-store.ts`
  - 本地提交记录读取

## 下一步建议

1. 增加后端持久化
2. 增加管理员导出 CSV
4. 增加画像到五阶段 prompt 的转换逻辑
5. 增加问卷结果列表与管理页
