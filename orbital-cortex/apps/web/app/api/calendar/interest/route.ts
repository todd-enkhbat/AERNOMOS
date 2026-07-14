import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

type InterestBody = {
  name?: string;
  email?: string;
  organization?: string;
  role?: string;
  eventInterest?: string;
  message?: string;
};

function isEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

export async function POST(request: Request) {
  let body: InterestBody;
  try {
    body = (await request.json()) as InterestBody;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  const name = (body.name ?? "").trim();
  const email = (body.email ?? "").trim().toLowerCase();
  const organization = (body.organization ?? "").trim();
  const role = (body.role ?? "").trim();
  const eventInterest = (body.eventInterest ?? "").trim();
  const message = (body.message ?? "").trim();

  if (name.length < 2) {
    return NextResponse.json({ error: "Name is required." }, { status: 400 });
  }
  if (!isEmail(email)) {
    return NextResponse.json({ error: "A valid email is required." }, { status: 400 });
  }
  if (organization.length < 2) {
    return NextResponse.json({ error: "Organization is required." }, { status: 400 });
  }

  const payload = {
    receivedAt: new Date().toISOString(),
    name,
    email,
    organization,
    role: role || null,
    eventInterest: eventInterest || null,
    message: message || null,
    source: "calendar-interest"
  };

  // Interest inbox wiring is [TBD]. Persist to logs for now so ops can recover submissions.
  console.info("[calendar-interest]", JSON.stringify(payload));

  return NextResponse.json({
    ok: true,
    message: "Interest received. We will follow up if there is a fit."
  });
}
