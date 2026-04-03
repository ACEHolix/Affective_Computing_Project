import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { NextRequest, NextResponse } from "next/server";
import { transformAnswersToProfile } from "../../../lib/profile-transform";

function safeTimestamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const answers = body?.answers ?? {};
  const transformed = transformAnswersToProfile(answers);

  const payload = {
    submittedAt: new Date().toISOString(),
    surveyVersion: "2026-04-01",
    answers,
    transformed,
  };

  const dir = join(process.cwd(), "data", "submissions");
  await mkdir(dir, { recursive: true });

  const filename = `submission-${safeTimestamp()}.json`;
  const filepath = join(dir, filename);
  await writeFile(filepath, JSON.stringify(payload, null, 2), "utf-8");

  return NextResponse.json({
    ok: true,
    savedTo: filepath,
    transformed,
  });
}
