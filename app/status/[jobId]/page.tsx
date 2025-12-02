import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type JobStatus = {
  job_id: string;
  status: string;
  content: unknown;
  linked_job_id: string | null;
  enqueued_at: string | null;
  started_at: string | null;
  ended_at: string | null;
  exc_info: string | null;
};

async function fetchJobStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${API_BASE}/status/${encodeURIComponent(jobId)}`, {
    cache: "no-store"
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch job status (${res.status})`);
  }

  return res.json();
}

export default async function StatusPage({
  params
}: {
  params: { jobId: string };
}) {
  const { jobId } = params;

  let data: JobStatus | null = null;
  let error: string | null = null;

  try {
    data = await fetchJobStatus(jobId);
  } catch (err) {
    error =
      err instanceof Error ? err.message : "Something went wrong fetching status.";
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <section className="relative w-full max-w-2xl overflow-hidden rounded-2xl border border-slate-700/60 bg-slate-900/80 p-8 shadow-[0_24px_80px_rgba(15,23,42,0.90)] backdrop-blur">
        <div className="pointer-events-none absolute -inset-40 -z-10 bg-[radial-gradient(circle_at_0_0,rgba(56,189,248,0.18),transparent_55%),radial-gradient(circle_at_100%_0,rgba(56,189,248,0.14),transparent_55%)]" />

        <header className="mb-6">
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-slate-50">
            Job status
            <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_14px_rgba(16,185,129,0.8)]" />
          </h1>
          <p className="mt-1.5 text-sm text-slate-400">
            Tracking analysis request <span className="font-mono text-xs">{jobId}</span>
          </p>
        </header>

        {error ? (
          <div className="rounded-xl border border-red-400/50 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : data ? (
          <div className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-slate-700/70 bg-slate-900/70 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Status
                </p>
                <p className="mt-1 inline-flex items-center gap-2 text-sm font-semibold text-slate-50">
                  <span
                    className={`h-2 w-2 rounded-full ${
                      data.status === "finished"
                        ? "bg-emerald-400"
                        : data.status === "failed"
                          ? "bg-red-400"
                          : "bg-amber-300"
                    }`}
                  />
                  {data.status}
                </p>
              </div>

              <div className="rounded-xl border border-slate-700/70 bg-slate-900/70 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Timeline
                </p>
                <dl className="mt-1 space-y-1.5 text-xs text-slate-300">
                  <div className="flex gap-2">
                    <dt className="w-20 text-slate-500">Enqueued</dt>
                    <dd className="flex-1 truncate">
                      {data.enqueued_at ? new Date(data.enqueued_at).toLocaleString() : "—"}
                    </dd>
                  </div>
                  <div className="flex gap-2">
                    <dt className="w-20 text-slate-500">Started</dt>
                    <dd className="flex-1 truncate">
                      {data.started_at ? new Date(data.started_at).toLocaleString() : "—"}
                    </dd>
                  </div>
                  <div className="flex gap-2">
                    <dt className="w-20 text-slate-500">Finished</dt>
                    <dd className="flex-1 truncate">
                      {data.ended_at ? new Date(data.ended_at).toLocaleString() : "—"}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>

            <div className="rounded-xl border border-slate-700/70 bg-slate-900/70 p-4">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Content (JSON)
              </p>
              <div className="mt-2 max-h-64 overflow-auto rounded-lg bg-slate-950/60 p-3 text-xs text-slate-200">
                {data.content
                  ? typeof data.content === "string"
                    ? data.content
                    : JSON.stringify(data.content, null, 2)
                  : data.status === "finished"
                    ? "Job finished with no content."
                    : "Your PDF is still being analyzed. Refresh this page in a moment to see the output."}
              </div>
            </div>

            {data.linked_job_id && (
              <div className="flex items-center justify-between rounded-xl border border-slate-700/70 bg-slate-900/70 p-4 text-xs text-slate-300">
                <div>
                  <p className="font-medium text-slate-200">Follow-up analysis available</p>
                  <p className="mt-0.5 text-[0.7rem] text-slate-500">
                    View the key information extracted from this bill.
                  </p>
                </div>
                <Link
                  href={`/status/${encodeURIComponent(data.linked_job_id)}`}
                  className="inline-flex items-center gap-1 rounded-full border border-sky-400/70 px-3 py-1.5 text-[0.7rem] font-medium text-sky-100 transition hover:bg-sky-500/10"
                >
                  View linked job
                  <span aria-hidden>→</span>
                </Link>
              </div>
            )}

            {data.exc_info && (
              <div className="rounded-xl border border-red-400/40 bg-red-500/5 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-red-300">
                  Error details
                </p>
                <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap break-words text-xs text-red-200">
                  {data.exc_info}
                </pre>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-slate-300">Loading job status…</p>
        )}

        <footer className="mt-6 flex items-center justify-between text-xs text-slate-500">
          <Link
            href="/"
            className="inline-flex items-center gap-1 rounded-full border border-slate-600/70 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:border-sky-400 hover:text-sky-200"
          >
            <span aria-hidden>←</span>
            New estimate
          </Link>
          <span className="text-[0.68rem] uppercase tracking-wide text-slate-500">
            Auto-refresh by reloading this page
          </span>
        </footer>
      </section>
    </main>
  );
}


