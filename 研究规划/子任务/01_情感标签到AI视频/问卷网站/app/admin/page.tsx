import Link from "next/link";
import { listSubmissions } from "../../lib/submission-store";

export default async function AdminPage() {
  const submissions = await listSubmissions();

  return (
    <main className="page-shell">
      <section className="panel">
        <p className="note">Admin / submissions</p>
        <h1>提交结果管理页</h1>
        <p className="lead">
          当前页面直接读取服务器上的 <code>data/submissions</code> 目录，用于快速查看已提交问卷、画像结果与生成输入。
        </p>

        <div className="action-row">
          <Link className="button secondary" href="/">
            返回首页
          </Link>
          <Link className="button" href="/survey">
            打开问卷页
          </Link>
        </div>

        {submissions.length === 0 ? (
          <div className="empty-state" style={{ marginTop: 28 }}>
            目前还没有提交记录。
          </div>
        ) : (
          <div className="submission-list" style={{ marginTop: 28 }}>
            {submissions.map((item) => {
              const answers = item.answers ?? {};
              const answerCount = Object.keys(answers).length;
              const transformed = item.transformed as Record<string, unknown> | undefined;
              const generationInputs =
                transformed && typeof transformed === "object"
                  ? (transformed.generationInputs as Record<string, unknown> | undefined)
                  : undefined;

              return (
                <article className="submission-card" key={item.file}>
                  <div>
                    <h3>{item.file}</h3>
                    <p className="note">提交时间：{item.submittedAt ?? "未知"}</p>
                    <p className="note">答卷字段数：{answerCount}</p>
                    <p className="note">
                      主场景：
                      {Array.isArray(generationInputs?.dominantScenes)
                        ? (generationInputs?.dominantScenes as string[]).join(", ")
                        : "无"}
                    </p>
                  </div>
                  <div className="action-row">
                    <Link className="button ghost" href={`/admin/${encodeURIComponent(item.file)}`}>
                      查看详情
                    </Link>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}
