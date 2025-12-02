import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Get Energy Rate Estimate",
  description: "Upload your business energy bill to get the lowest available rates."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.18),_transparent_55%),_radial-gradient(circle_at_bottom_right,_rgba(16,185,129,0.18),_transparent_55%)] text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}


