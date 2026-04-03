import { NextRequest, NextResponse } from "next/server";

function unauthorizedResponse() {
  return new NextResponse("Admin authentication required.", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="subtask01-admin", charset="UTF-8"',
    },
  });
}

function decodeBasicAuth(header: string) {
  const [scheme, encoded] = header.split(" ");

  if (scheme !== "Basic" || !encoded) {
    return null;
  }

  try {
    const decoded = atob(encoded);
    const separatorIndex = decoded.indexOf(":");

    if (separatorIndex === -1) {
      return null;
    }

    return {
      username: decoded.slice(0, separatorIndex),
      password: decoded.slice(separatorIndex + 1),
    };
  } catch {
    return null;
  }
}

export function middleware(request: NextRequest) {
  const expectedUsername = process.env.ADMIN_USERNAME;
  const expectedPassword = process.env.ADMIN_PASSWORD;

  if (!expectedUsername || !expectedPassword) {
    return new NextResponse(
      "Admin credentials are not configured. Set ADMIN_USERNAME and ADMIN_PASSWORD on the server.",
      { status: 503 },
    );
  }

  const authorization = request.headers.get("authorization");

  if (!authorization) {
    return unauthorizedResponse();
  }

  const credentials = decodeBasicAuth(authorization);

  if (!credentials) {
    return unauthorizedResponse();
  }

  if (
    credentials.username !== expectedUsername ||
    credentials.password !== expectedPassword
  ) {
    return unauthorizedResponse();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"],
};
