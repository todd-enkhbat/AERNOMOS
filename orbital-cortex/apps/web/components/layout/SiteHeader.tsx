"use client";

import { ArrowUpRight, Menu, Search, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { NomosMark } from "@/components/brand/NomosMark";
import styles from "./SiteHeader.module.css";

const primary = [
  { href: "/console", label: "Try Nomos" },
  { href: "/capabilities", label: "Capabilities" },
  { href: "/about", label: "About" },
  { href: "/docs", label: "Docs" }
];
const secondary = [
  { href: "/missions", label: "Missions" },
  { href: "/dashboard", label: "Control" },
  { href: "/network", label: "Network atlas" },
  { href: "/examples", label: "Example missions" },
  { href: "/calendar", label: "Industry calendar" }
];

export function SiteHeader() {
  const pathname = usePathname();
  const [query, setQuery] = useState("");
  const dialog = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const search = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const close = () => { dialog.current?.close(); setOpen(false); setQuery(""); };
  const show = () => { dialog.current?.showModal(); setOpen(true); };

  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const shortcut = (event: KeyboardEvent) => {
      if (event.key === "/" && !(event.target instanceof HTMLInputElement)) {
        event.preventDefault(); search.current?.focus();
      }
    };
    document.addEventListener("keydown", shortcut);
    return () => { document.body.style.overflow = previous; document.removeEventListener("keydown", shortcut); };
  }, [open]);

  const results = [...primary, ...secondary].filter(item => item.label.toLowerCase().includes(query.toLowerCase()));
  const navLink = (item: typeof primary[number]) => (
    <Link key={item.href} href={item.href} onClick={close} aria-current={pathname === item.href ? "page" : undefined}>{item.label}</Link>
  );

  return (
    <header className={styles.header}>
      <div className={styles.bar}>
        <Link className={styles.brand} href="/" aria-label="Nomos Orbital home">
          <NomosMark size={36} />
          <span><strong>Nomos</strong><span>Orbital</span></span>
        </Link>
        <nav className={styles.desktop} aria-label="Primary">{primary.map(navLink)}</nav>
        <button ref={trigger} className={styles.menuButton} aria-label="Open navigation" aria-haspopup="dialog" aria-expanded={open} aria-controls="site-navigation" onClick={show}><Menu size={27} strokeWidth={1.5} /></button>
      </div>
      <dialog ref={dialog} id="site-navigation" className={styles.drawer} aria-label="Site navigation" onCancel={close} onClose={() => { setOpen(false); setQuery(""); trigger.current?.focus(); }} onClick={event => { if (event.target === dialog.current && event.clientX < dialog.current.getBoundingClientRect().left) close(); }}>
        <div className={styles.drawerInner}>
          <div className={styles.drawerTop}>
            <Link href="/" aria-label="Nomos Orbital home" onClick={close}><NomosMark size={36} /></Link>
            <button className={styles.close} aria-label="Close navigation" onClick={close} autoFocus><X size={26} strokeWidth={1.5} /></button>
          </div>
          <nav className={styles.primary} aria-label="Explore Nomos">{primary.map(navLink)}</nav>
          <nav className={styles.secondary} aria-label="More from Nomos">{secondary.map(navLink)}</nav>
          <div className={styles.searchArea}>
            <label className={styles.search}><Search size={23} strokeWidth={1.5} /><input ref={search} value={query} onChange={event => setQuery(event.target.value)} placeholder="Search" aria-label="Search navigation" aria-controls="navigation-results" /><kbd>/</kbd></label>
            {query && <nav id="navigation-results" className={styles.results} aria-label="Search results">{results.length ? results.map(navLink) : <p role="status">No matching pages.</p>}</nav>}
          </div>
          <Link className={styles.action} href="/console" onClick={close}>Run a request <ArrowUpRight size={19} /></Link>
        </div>
      </dialog>
    </header>
  );
}
