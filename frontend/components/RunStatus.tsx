"use client";

import type { Feed } from "../lib/types";

interface RunStatusProps {
  feed: Feed;
  onRun?: () => void;
  running?: boolean;
}

export default function RunStatus({
  feed,
  onRun,
  running = false,
}: RunStatusProps) {
  const statusMessage = {
    created:
      "This feed has been created but has not been run yet.",
    ready:
      "The feed is ready to run.",
    running:
      "The scraper is currently running.",
    success:
      "The latest scraper run completed successfully.",
    failed:
      "The latest scraper run failed. The previous successful RSS output remains available.",
  };

  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
      <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
        <div>
          <p className="text-sm font-medium text-gray-400">
            Feed Status
          </p>

          <div className="mt-2 flex items-center gap-3">
            <span
              className={[
                "h-3 w-3 rounded-full",
                feed.status === "success"
                  ? "bg-green-500"
                  : feed.status === "failed"
                    ? "bg-red-500"
                    : feed.status ===
                        "running"
                      ? "bg-yellow-500"
                      : "bg-gray-500",
              ].join(" ")}
            />

            <span className="text-xl font-semibold capitalize">
              {feed.status}
            </span>
          </div>

          <p className="mt-2 text-sm text-gray-500">
            {
              statusMessage[
                feed.status
              ]
            }
          </p>
        </div>

        {onRun && (
          <button
            type="button"
            onClick={onRun}
            disabled={running}
            className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {running
              ? "Running..."
              : "Run Feed"}
          </button>
        )}
      </div>

      <div className="mt-6 grid gap-4 border-t border-gray-800 pt-5 sm:grid-cols-3">
        <div>
          <p className="text-xs text-gray-600">
            Last run
          </p>

          <p className="mt-1 text-sm text-gray-300">
            {feed.last_run_at
              ? new Date(
                  feed.last_run_at
                ).toLocaleString()
              : "Never"}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-600">
            Last successful run
          </p>

          <p className="mt-1 text-sm text-gray-300">
            {feed.last_success_at
              ? new Date(
                  feed.last_success_at
                ).toLocaleString()
              : "Never"}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-600">
            Articles
          </p>

          <p className="mt-1 text-sm text-gray-300">
            {feed.article_count}
          </p>
        </div>
      </div>

      {feed.last_error && (
        <div className="mt-5 rounded-xl border border-red-900 bg-red-950/30 p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-red-400">
            Last Error
          </p>

          <p className="mt-2 break-words text-sm text-red-300">
            {feed.last_error}
          </p>
        </div>
      )}
    </section>
  );
}