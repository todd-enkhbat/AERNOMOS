import dynamic from "next/dynamic";
import Image from "next/image";
import Link from "next/link";

import { FadeIn } from "@/components/motion/primitives";

const AboutScrollStory = dynamic(
  () =>
    import("@/components/about/AboutScrollStory").then((m) => m.AboutScrollStory),
  { ssr: false }
);

export default function AboutPage() {
  return (
    <div className="pb-6">
      <div className="relative overflow-hidden">
        <div className="absolute inset-0">
          <Image
            alt=""
            aria-hidden
            className="object-cover object-center opacity-30"
            fill
            priority
            sizes="100vw"
            src="/images/voyager-heritage.png"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-void/50 via-void/90 to-void" />
        </div>
        <div className="page-shell relative py-12 md:py-16">
          <FadeIn>
            <p className="chart-label text-gold">About</p>
            <h1 className="display mt-2 max-w-2xl text-3xl leading-tight text-cream md:text-5xl">
              Law, signal, and plasma discipline.
            </h1>
            <p className="prose-compact mt-3 max-w-xl text-muted">
              Scroll to spin the Golden Record. Three lineages define Nomos Orbital:
              the Greek idea of order, the Voyager disc as distilled downlink, and
              Columbia plasma physics as engineering culture.
            </p>
            <Link className="btn-gold mt-6 inline-flex" href="/#demo">
              Run live demo
            </Link>
          </FadeIn>
        </div>
      </div>

      <AboutScrollStory />

      <section className="section-gap page-shell">
        <div className="aave-glass max-w-2xl p-6 sm:p-8">
          <p className="chart-label text-gold">Nomos Orbital</p>
          <h2 className="display mt-2 text-2xl text-cream">One name on the door.</h2>
          <div className="prose-compact mt-4">
            <p>
              The repo behind the product is AERNOMOS. The company you interact
              with is Nomos Orbital. Same stack, same API, production at
              api.nomosorbital.com.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
