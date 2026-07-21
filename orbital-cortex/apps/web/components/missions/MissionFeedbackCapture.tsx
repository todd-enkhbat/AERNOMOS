"use client";

import { FormEvent, useState } from "react";

import { LiquidButton } from "@/components/liquid/LiquidButton";
import {
  apiErrorMessage,
  submitDesignPartnerRequest,
  submitMissionFeedback,
  type FeedbackRating
} from "@/lib/api";

const RATINGS: { value: FeedbackRating; label: string }[] = [
  { value: "yes", label: "Yes" },
  { value: "partly", label: "Partly" },
  { value: "no", label: "No" }
];

const COMMENT_MAX = 500;

const fieldClass =
  "mt-1 w-full rounded-lg border border-white/15 bg-void px-3 py-2 text-sm text-cream placeholder:text-muted-dark";

export function MissionFeedbackCapture({
  missionId,
  readOnly
}: {
  missionId: string;
  readOnly?: boolean;
}) {
  const [rating, setRating] = useState<FeedbackRating | null>(null);
  const [comment, setComment] = useState("");
  const [feedbackBusy, setFeedbackBusy] = useState(false);
  const [feedbackDone, setFeedbackDone] = useState(false);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [workEmail, setWorkEmail] = useState("");
  const [organization, setOrganization] = useState("");
  const [role, setRole] = useState("");
  const [missionType, setMissionType] = useState("");
  const [requestedIntegration, setRequestedIntegration] = useState("");
  const [permission, setPermission] = useState(false);
  const [honeypot, setHoneypot] = useState("");
  const [leadBusy, setLeadBusy] = useState(false);
  const [leadDone, setLeadDone] = useState(false);
  const [leadError, setLeadError] = useState<string | null>(null);

  if (readOnly) return null;

  async function onSubmitFeedback() {
    if (!rating || feedbackBusy || feedbackDone) return;
    setFeedbackBusy(true);
    setFeedbackError(null);
    try {
      await submitMissionFeedback(missionId, {
        rating,
        comment: comment.trim() || undefined
      });
      setFeedbackDone(true);
    } catch (error) {
      setFeedbackError(apiErrorMessage(error, "Could not submit feedback."));
    } finally {
      setFeedbackBusy(false);
    }
  }

  async function onSubmitLead(event: FormEvent) {
    event.preventDefault();
    if (!permission || leadBusy || leadDone) return;
    setLeadBusy(true);
    setLeadError(null);
    try {
      await submitDesignPartnerRequest({
        mission_id: missionId,
        name: name.trim(),
        work_email: workEmail.trim(),
        organization: organization.trim(),
        role: role.trim(),
        mission_type: missionType.trim(),
        requested_integration: requestedIntegration.trim(),
        permission_to_contact: true,
        website: honeypot
      });
      setLeadDone(true);
    } catch (error) {
      setLeadError(apiErrorMessage(error, "Could not submit request."));
    } finally {
      setLeadBusy(false);
    }
  }

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
        <p className="chart-label text-gold">Optional feedback</p>
        <h3 className="mt-3 font-serif text-2xl tracking-[-0.02em] text-cream">
          Was this plan useful?
        </h3>
        <p className="mt-2 text-sm leading-6 text-muted">
          A few clicks. Never required — your plan stays fully usable either way.
        </p>
        {feedbackDone ? (
          <p className="feedback-success-fade mt-5 text-sm text-cobalt">
            Thanks — feedback recorded.
          </p>
        ) : (
          <>
            <div className="mt-5 flex flex-wrap gap-2" role="group" aria-label="Plan usefulness">
              {RATINGS.map((option) => {
                const selected = rating === option.value;
                return (
                  <button
                    className={[
                      "rounded-lg border px-4 py-2 text-sm transition-colors duration-150",
                      selected
                        ? "border-gold/45 bg-gold/10 text-cream"
                        : "border-white/15 text-silver hover:border-white/30"
                    ].join(" ")}
                    key={option.value}
                    onClick={() => setRating(option.value)}
                    type="button"
                  >
                    {option.label}
                  </button>
                );
              })}
            </div>
            <label className="mt-4 block text-xs text-muted">
              Comment (optional, {COMMENT_MAX} chars max)
              <textarea
                className={fieldClass}
                maxLength={COMMENT_MAX}
                onChange={(event) => setComment(event.target.value)}
                rows={3}
                value={comment}
              />
            </label>
            {feedbackError ? <p className="mt-2 text-sm text-vermilion">{feedbackError}</p> : null}
            <div className="mt-4">
              <LiquidButton
                disabled={!rating || feedbackBusy}
                onClick={() => {
                  void onSubmitFeedback();
                }}
                variant="outline"
              >
                {feedbackBusy ? "Sending…" : "Send feedback"}
              </LiquidButton>
            </div>
          </>
        )}
      </div>

      <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5">
        <p className="chart-label text-gold">Design partner</p>
        <h3 className="mt-3 font-serif text-2xl tracking-[-0.02em] text-cream">
          Use this for a real mission
        </h3>
        <p className="mt-2 text-sm leading-6 text-muted">
          Optional. Tell us who to contact — we only store this privately.
        </p>
        {leadDone ? (
          <p className="feedback-success-fade mt-5 text-sm text-cobalt">
            Request received. We will follow up if appropriate.
          </p>
        ) : (
          <form className="mt-5 space-y-3" onSubmit={onSubmitLead}>
            <label className="block text-xs text-muted">
              Name
              <input className={fieldClass} onChange={(e) => setName(e.target.value)} required value={name} />
            </label>
            <label className="block text-xs text-muted">
              Work email
              <input
                className={fieldClass}
                onChange={(e) => setWorkEmail(e.target.value)}
                required
                type="email"
                value={workEmail}
              />
            </label>
            <label className="block text-xs text-muted">
              Organization
              <input
                className={fieldClass}
                onChange={(e) => setOrganization(e.target.value)}
                required
                value={organization}
              />
            </label>
            <label className="block text-xs text-muted">
              Role
              <input className={fieldClass} onChange={(e) => setRole(e.target.value)} required value={role} />
            </label>
            <label className="block text-xs text-muted">
              Mission type
              <input
                className={fieldClass}
                onChange={(e) => setMissionType(e.target.value)}
                required
                value={missionType}
              />
            </label>
            <label className="block text-xs text-muted">
              Requested integration
              <input
                className={fieldClass}
                onChange={(e) => setRequestedIntegration(e.target.value)}
                required
                value={requestedIntegration}
              />
            </label>
            {/* Honeypot — hidden from humans, bots often fill it */}
            <label
              aria-hidden="true"
              className="absolute -left-[9999px] h-0 w-0 overflow-hidden opacity-0"
              tabIndex={-1}
            >
              Website
              <input
                autoComplete="off"
                name="website"
                onChange={(e) => setHoneypot(e.target.value)}
                tabIndex={-1}
                value={honeypot}
              />
            </label>
            <label className="flex items-start gap-3 text-sm text-silver">
              <input
                checked={permission}
                className="mt-1"
                onChange={(e) => setPermission(e.target.checked)}
                type="checkbox"
              />
              <span>I give Nomos Orbital permission to contact me about this request.</span>
            </label>
            {leadError ? <p className="text-sm text-vermilion">{leadError}</p> : null}
            <LiquidButton disabled={!permission || leadBusy} type="submit" variant="outline">
              {leadBusy ? "Sending…" : "Request design-partner contact"}
            </LiquidButton>
          </form>
        )}
      </div>
    </div>
  );
}
