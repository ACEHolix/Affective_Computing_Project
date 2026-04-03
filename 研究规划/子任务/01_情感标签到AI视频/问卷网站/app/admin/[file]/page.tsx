import Link from "next/link";
import { notFound } from "next/navigation";
import { readSubmission } from "../../../lib/submission-store";

export default async function SubmissionDetailPage({
  params,
}: {
  params: Promise<{ file: string }>;
}) {
  const { file } = await params;
  const decoded = decodeURIComponent(file);
  const submission = await readSubmission(decoded);

  if (!submission) {
    notFound();
  }

  return (
    <main className="page-shell">
      <section className="panel">
        <p className="note">Admin / detail</p>
        <h1>{submission.file}</h1>
        <p className="lead">查看原始答卷、转换后的画像结果和 prompt package。</p>

        <div className="action-row">
          <Link className="button secondary" href="/admin">
            返回列表
          </Link>
        </div>

        <div style={{ marginTop: 24 }}>
          <h3>原始提交 JSON</h3>
          <pre className="code-block">{JSON.stringify(submission, null, 2)}</pre>
        </div>
      </section>
    </main>
  );
}
