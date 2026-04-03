import { NextRequest, NextResponse } from "next/server";
import { transformAnswersToProfile } from "../../../lib/profile-transform";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const answers = body?.answers ?? {};
  const transformed = transformAnswersToProfile(answers);
  return NextResponse.json(transformed);
}
