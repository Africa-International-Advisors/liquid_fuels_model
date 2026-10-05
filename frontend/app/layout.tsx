import type { Metadata } from "next";
import { Navigation } from "@/components/navigation";
import "./globals.css";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: { default: "Liquid fuels ? Model handbook", template: "%s ? Liquid fuels" }, description: "Documentation for the SACU liquid fuels model: demand drivers, assumptions and architecture.", robots: {index: false, follow: false} };
export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
  return <html lang="en"><body><a className="skip-link" href="#main">Skip to content</a><div className="app-shell"><Navigation/><div className="main-shell"><div className="topbar"><span>INSIGHTS <span className="topbar-divider">/</span> RESEARCH &amp; MODELLING</span><span className="draft-badge">PROVISIONAL MODEL</span></div><main id="main" tabIndex={-1}>{children}</main><footer className="page-footer"><span>Liquid fuels model ? Internal documentation</span><span>Source files remain the reference.</span></footer></div></div></body></html>;
}
