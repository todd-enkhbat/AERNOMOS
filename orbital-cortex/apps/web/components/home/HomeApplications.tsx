import {
  ArrowRight, CloudCog, Flame, Globe2, Leaf, MapPinned,
  Radio, Satellite, Ship, Waves, Cpu, Clock, ShieldCheck
} from "lucide-react";
import Link from "next/link";

import { LiquidButton } from "@/components/liquid";
import styles from "./HomeApplications.module.css";

const applications = [
  [
    { label: "Maritime monitoring", icon: Ship },
    { label: "Agriculture", icon: Leaf },
    { label: "Disaster response", icon: Waves },
    { label: "Wildfire assessment", icon: Flame },
    { label: "Environmental change", icon: Globe2 }
  ],
  [
    { label: "Satellite imagery", icon: Satellite },
    { label: "Ground contact planning", icon: Radio },
    { label: "Data delivery", icon: Globe2 },
    { label: "Processing placement", icon: CloudCog },
    { label: "Remote sensing", icon: MapPinned }
  ],
  [
    { label: "Onboard vs cloud", icon: Satellite },
    { label: "Edge processing", icon: Cpu },
    { label: "Downlink windows", icon: Radio },
    { label: "Data residency", icon: ShieldCheck },
    { label: "Delivery deadlines", icon: Clock }
  ]
];

export function HomeApplications() {
  return (
    <section className={styles.applications} aria-labelledby="applications-title">
      <div className="page-shell">
        <div className={styles.heading}>
          <p className="chart-label text-gold">Built around your objective</p>
          <h2 id="applications-title">What do you need from space?</h2>
          <p>Find the imagery, contact windows, and processing path for your mission.</p>
        </div>

        <input className={styles.pause} type="checkbox" id="pause-applications" />
        <label className={styles.pauseLabel} htmlFor="pause-applications">
          <span className={styles.pauseText}>Pause motion</span>
          <span className={styles.resumeText}>Resume motion</span>
        </label>

        <div className={styles.bands}>
          {applications.map((row, index) => (
            <div className={styles.band} key={index}>
              <div className={`${styles.track} ${index === 1 ? styles.reverse : ""}`}>
                {[0, 1].map((copy) => (
                  <ul className={styles.group} key={copy} aria-hidden={copy === 1 ? true : undefined}>
                    {row.map(({ label, icon: Icon }) => (
                      <li key={label}>
                        <Link className={styles.application} href="/console" tabIndex={copy === 1 ? -1 : undefined}>
                          {label}<Icon aria-hidden size={20} strokeWidth={1.4} />
                        </Link>
                      </li>
                    ))}
                  </ul>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className={styles.action}>
          <LiquidButton className={styles.tryButton} href="/console" variant="primary">
            Try Nomos <ArrowRight aria-hidden size={18} />
          </LiquidButton>
          <p>Start with a plan. No account required.</p>
        </div>
      </div>
    </section>
  );
}
