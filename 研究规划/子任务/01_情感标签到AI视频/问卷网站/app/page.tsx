import Link from "next/link";

export default function HomePage() {
  return (
    <main className="page-shell">
      <section className="hero">
        <p className="note">Subtask 01 / Survey Prototype</p>
        <h1>个体化情绪诱发视频用户画像问卷</h1>
        <p className="lead">
          这是一个最小可运行的答题网站原型，用于收集用户画像，并为后续 AI 视频生成、个体化刺激选择和实验条件构建提供结构化输入。
        </p>

        <div className="grid-2">
          <div className="mini-card">
            <h3>当前原型包含</h3>
            <ul>
              <li>按模块分页的正式版问卷</li>
              <li>单选、多选、评分、矩阵评分、文本题</li>
              <li>浏览器本地自动保存</li>
              <li>提交后导出 JSON</li>
            </ul>
          </div>
          <div className="mini-card">
            <h3>下一步可扩展</h3>
            <ul>
              <li>接数据库保存真实答卷</li>
              <li>管理员导出 CSV</li>
              <li>问卷答案到画像 JSON 的自动转换</li>
              <li>问卷结果到五阶段 prompt 的自动生成</li>
            </ul>
          </div>
        </div>

        <div className="cta-row">
          <Link className="button" href="/survey">
            开始填写问卷
          </Link>
          <Link className="button secondary" href="/admin">
            查看提交结果
          </Link>
        </div>
      </section>
    </main>
  );
}
