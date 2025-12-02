"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type UploadResponse = {
  job_id: string;
  document_id: string;
  filename: string;
};

export default function GetEstimatePage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!email || !file) {
      setError("Please provide both your email and a PDF of your energy bill.");
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `Upload failed with status ${response.status}`);
      }

      const data: UploadResponse = await response.json();
      // eslint-disable-next-line no-console
      console.log("Upload response", data);

      router.push(`/status/${encodeURIComponent(data.job_id)}`);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Something went wrong while submitting your request.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <section className="relative w-full max-w-xl overflow-hidden rounded-2xl border border-slate-700/60 bg-slate-900/80 p-8 shadow-[0_24px_80px_rgba(15,23,42,0.90)] backdrop-blur">
        <div className="pointer-events-none absolute -inset-40 -z-10 bg-[radial-gradient(circle_at_0_0,rgba(56,189,248,0.18),transparent_55%),radial-gradient(circle_at_100%_0,rgba(129,140,248,0.18),transparent_55%)]" />

        <header className="mb-7">
          <h1 className="flex items-center gap-2 text-3xl font-semibold tracking-tight text-slate-50">
            Get Estimate
            <span className="inline-flex h-2 w-2 rounded-full bg-sky-400 shadow-[0_0_14px_rgba(56,189,248,0.8)]" />
          </h1>
          <p className="mt-1.5 text-sm text-slate-400">
            Get the lowest energy rates for your business by securely uploading your latest
            bill.
          </p>
        </header>

        <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="text-xs font-medium text-slate-300">
              Business email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="rounded-xl border border-slate-700/70 bg-slate-900/70 px-3 py-2.5 text-sm text-slate-100 outline-none ring-sky-500/60 transition focus:border-sky-400 focus:ring-2 focus:ring-offset-0"
              placeholder="you@company.com"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="bill" className="text-xs font-medium text-slate-300">
              Upload energy bill (.pdf)
            </label>
            <input
              id="bill"
              type="file"
              accept="application/pdf"
              required
              onChange={(e) => {
                const selectedFile = e.target.files?.[0] ?? null;
                setFile(selectedFile);
              }}
              className="cursor-pointer rounded-xl border border-slate-700/70 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 file:mr-4 file:rounded-lg file:border-0 file:bg-sky-500/10 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-sky-300 hover:file:bg-sky-500/20 focus-visible:border-sky-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500/60"
            />
            <p className="text-xs text-slate-500">
              We only use this to analyze your current rates.
            </p>
          </div>

          {error && (
            <p className="mt-1 rounded-lg border border-red-400/50 bg-red-500/10 px-3 py-2 text-xs text-red-300">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="mt-1 inline-flex items-center justify-center gap-1.5 rounded-full bg-gradient-to-r from-sky-400 to-sky-500 px-5 py-2.5 text-sm font-semibold text-slate-950 shadow-[0_18px_40px_rgba(8,47,73,0.9)] transition hover:from-sky-300 hover:to-sky-400 hover:shadow-[0_22px_44px_rgba(8,47,73,0.95)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 active:translate-y-px active:scale-95 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? "Submitting…" : "Get Estimate"}
            <span aria-hidden className="text-xs">
              →
            </span>
          </button>
        </form>
      </section>
    </main>
  );
}


