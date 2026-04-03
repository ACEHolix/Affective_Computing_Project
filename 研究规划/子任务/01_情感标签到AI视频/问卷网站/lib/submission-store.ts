import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";

export type SubmissionRecord = {
  file: string;
  submittedAt?: string;
  surveyVersion?: string;
  answers?: Record<string, unknown>;
  transformed?: Record<string, unknown>;
};

const submissionsDir = join(process.cwd(), "data", "submissions");

export async function listSubmissionFiles() {
  try {
    const files = await readdir(submissionsDir);
    return files.filter((file) => file.endsWith(".json")).sort().reverse();
  } catch {
    return [];
  }
}

export async function readSubmission(file: string): Promise<SubmissionRecord | null> {
  try {
    const raw = await readFile(join(submissionsDir, file), "utf-8");
    const parsed = JSON.parse(raw) as Omit<SubmissionRecord, "file">;
    return { file, ...parsed };
  } catch {
    return null;
  }
}

export async function listSubmissions() {
  const files = await listSubmissionFiles();
  const records = await Promise.all(files.map((file) => readSubmission(file)));
  return records.filter((item): item is SubmissionRecord => item !== null);
}
