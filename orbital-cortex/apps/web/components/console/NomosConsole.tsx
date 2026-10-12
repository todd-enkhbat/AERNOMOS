"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import {
  apiErrorMessage,
  createMission,
  ensureAnonymousSession,
  listMissions,
  type MissionCreatePayload
} from "@/lib/api";

import { mountConsole } from "./engine";
import { CONSOLE_MARKUP } from "./markup";
import "./console.css";

/**
 * Nomos Console: Request, Missions, Network and Control on one surface.
 * The engine owns the canvas globe and chat DOM; this wrapper sizes the
 * surface below the site header and supplies the real mission API.
 */
export function NomosConsole() {
  const ref = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const routerRef = useRef(router);
  routerRef.current = router;

  useEffect(() => {
    const root = ref.current;
    if (!root) return;

    const size = () => {
      const top = root.getBoundingClientRect().top + window.scrollY;
      root.style.setProperty("--nc-h", `${Math.max(600, window.innerHeight - top)}px`);
      root.style.setProperty("--nc-top", `${Math.round(top + 8)}px`);
    };
    size();
    window.addEventListener("resize", size);

    const unmount = mountConsole(root, {
      async createMission(spec) {
        try {
          await ensureAnonymousSession();
          const created = await createMission(spec as MissionCreatePayload);
          return created.mission.id;
        } catch (err) {
          throw new Error(apiErrorMessage(err, "Could not save this mission."));
        }
      },
      async listMissions() {
        try {
          await ensureAnonymousSession();
          const { missions } = await listMissions();
          return missions.map((m) => ({ id: m.id, title: m.title }));
        } catch {
          return [];
        }
      },
      navigate: (href) => routerRef.current.push(href)
    });

    return () => {
      window.removeEventListener("resize", size);
      unmount();
    };
  }, []);

  return (
    <div
      className="nc"
      dangerouslySetInnerHTML={{ __html: `<div class="bg" aria-hidden="true"></div>${CONSOLE_MARKUP}` }}
      ref={ref}
    />
  );
}
