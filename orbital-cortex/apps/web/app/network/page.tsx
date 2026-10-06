"use client";

import dynamic from "next/dynamic";
import Image from "next/image";
import { OrbitalField } from "@/components/visual/OrbitalField";
import { useEffect, useState } from "react";

import { InlineNotice } from "@/components/InlineNotice";
import { apiErrorMessage, getNodes } from "@/lib/api";

import styles from "./NetworkPage.module.css";

const NetworkConsole = dynamic(
  () =>
    import("@/components/platform/NetworkConsole").then((m) => m.NetworkConsole),
  { ssr: false, loading: () => <div className="liquid-glass liquid-glass--card min-h-[320px] animate-pulse" /> }
);

export default function NetworkPage() {
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        await getNodes();
        if (!mounted) {
          return;
        }
      } catch (error) {
        if (mounted) {
          setNotice(apiErrorMessage(error));
        }
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="relative pb-6">
      <section className={styles.hero}>
        <Image
          alt="Long-exposure orbital light trails photographed against deep space"
          className={styles.heroImage}
          fill
          priority
          sizes="100vw"
          src="/images/archive/orbital-star-trails.jpg"
        />
        <div aria-hidden className={styles.heroScrim} />
        <OrbitalField />
        <div className={`page-shell ${styles.heroContent}`}>
          <div className={styles.heroStatement}>
            <p className="chart-label text-gold-bright">Network / Ground atlas</p>
            <h1>See the infrastructure behind the route.</h1>
            <p>
              Nomos combines sourced ground locations, public orbital data, contact
              geometry, and represented compute constraints to explain which path can
              fulfill a request, and which cannot.
            </p>
          </div>
          <div className={styles.layerRail} aria-label="Infrastructure layers">
            {[
              ["01", "Orbital", "Public catalogs, orbital geometry, and communication opportunities."],
              ["02", "Ground", "Reference station locations and the handoff constraints a route must respect."],
              ["03", "Cloud", "Customer-controlled and represented processing environments for feasible delivery patterns."]
            ].map(([index, name, detail]) => (
              <div className={styles.layer} key={name}>
                <span>{index}</span>
                <strong>{name}</strong>
                <p>{detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {notice ? <div className={`page-shell ${styles.notice}`}><InlineNotice message={notice} /></div> : null}

      <section className={styles.consoleSection}>
        <NetworkConsole />
      </section>

    </div>
  );
}
