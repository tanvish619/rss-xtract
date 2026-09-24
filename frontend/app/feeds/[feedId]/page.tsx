"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import {
  useEffect,
  useState,
} from "react";

import Navigation from "../../../components/Navigation";
import RunStatus from "../../../components/RunStatus";

import {
  getFeed,
  getFeedUrl,
  runFeed,
} from "../../../lib/api";

import type {
  Feed,
} from "../../../lib/types";

export default function FeedDetailsPage() {
  const params = useParams();

  const feedId =
    typeof params.feedId === "string"
      ? params.feedId
      : "";

  const [feed, setFeed] =
    useState<Feed | null>(null);

  const [copied, setCopied] =
    useState(false);

  const [running, setRunning] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    if (!feedId) {
      return;
    }

    async function loadFeed() {
      try {
        setLoading(true);
        setError("");

        const result =
          await getFeed(feedId);

        setFeed(result);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load feed."
        );
      } finally {
        setLoading(false);
      }
    }

    loadFeed();
  }, [feedId]);

  function handleCopy() {
    if (!feedId) {
      return;
    }

    navigator.clipboard.writeText(
      getFeedUrl(feedId)
    );

    setCopied(true);

    window.setTimeout(
      () => setCopied(false),
      2000
    );
  }

  async function handleRun() {
    if (!feedId || running) {
      return;
    }

    try {
      setRunning(true);
      setError("");

      await runFeed(feedId);

      const refreshed =
        await getFeed(feedId);

      setFeed(refreshed);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to run feed."
      );
    } finally {
      setRunning(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-white">
        <Navigation />

        <main className="mx-auto max-w-4xl px-6 py-20 text-center">
          <p className="text-gray-400">
            Loading feed...
          </p>
        </main>
      </div>
    );
  }

  if (!feed) {
    return (
      <div className="min-h-screen bg-gray-950 text-white">
        <Navigation />

        <main className="mx-auto max-w-4xl px-6 py-20 text-center">
          <h1 className="text-3xl font-bold">
            Feed Not Found
          </h1>

          <p className="mt-3 text-gray-500">
            {error ||
              "This feed could not be found."}
          </p>

          <Link
            href="/dashboard"
            className="mt-6 inline-flex rounded-xl bg-blue-600 px-5 py-3 font-semibold hover:bg-blue-500"
          >
            Back to Dashboard
          </Link>
        </main>
      </div>
    );
  }

  const feedUrl =
    getFeedUrl(feed.id);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navigation />

      <main className="mx-auto max-w-7xl px-6 py-10">
        <Link
          href="/dashboard"
          className="text-sm text-gray-500 hover:text-white"
        >
          ← Back to Dashboard
        </Link>

        {error && (
          <div className="mt-6 rounded-xl border border-red-900 bg-red-950/40 px-5 py-4 text-sm text-red-300">
            {error}
          </div>
        )}

        <div className="mt-6 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-medium uppercase tracking-wider text-blue-400">
              RSS Feed
            </p>

            <h1 className="mt-2 text-4xl font-bold">
              {feed.name}
            </h1>

            {feed.description && (
              <p className="mt-3 max-w-2xl text-gray-500">
                {feed.description}
              </p>
            )}
          </div>

          <Link
            href="/create"
            className="rounded-xl border border-gray-700 px-5 py-3 text-sm font-semibold text-gray-300 hover:border-gray-500 hover:text-white"
          >
            Create Another
          </Link>
        </div>

        <section className="mt-8 rounded-2xl border border-gray-800 bg-gray-900 p-6">
          <p className="text-sm font-medium text-gray-400">
            RSS Endpoint
          </p>

          <div className="mt-3 flex flex-col gap-3 sm:flex-row">
            <div className="min-w-0 flex-1 overflow-hidden rounded-xl border border-gray-800 bg-gray-950 px-4 py-3">
              <code className="break-all text-sm text-blue-300">
                {feedUrl}
              </code>
            </div>

            <button
              type="button"
              onClick={handleCopy}
              className="rounded-xl bg-gray-800 px-5 py-3 text-sm font-semibold hover:bg-gray-700"
            >
              {copied
                ? "Copied!"
                : "Copy URL"}
            </button>
          </div>
        </section>

        <div className="mt-8">
          <RunStatus
            feed={feed}
            onRun={handleRun}
            running={running}
          />
        </div>

        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
            <h2 className="text-lg font-semibold">
              Feed Information
            </h2>

            <div className="mt-5 space-y-5">
              <InfoRow
                label="Status"
                value={feed.status}
              />

              <InfoRow
                label="Current version"
                value={feed.current_version}
              />

              <InfoRow
                label="Article count"
                value={String(feed.article_count)}
              />

              <InfoRow
                label="Feed ID"
                value={feed.id}
              />

              <InfoRow
                label="Source URL"
                value={feed.source_url}
              />

              <InfoRow
                label="Created"
                value={new Date(
                  feed.created_at
                ).toLocaleString()}
              />

              <InfoRow
                label="Updated"
                value={new Date(
                  feed.updated_at
                ).toLocaleString()}
              />
            </div>
          </section>

          <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
            <h2 className="text-lg font-semibold">
              Versions
            </h2>

            <div className="mt-5 space-y-3">
              {feed.versions.map(
                (version) => (
                  <div
                    key={version.id}
                    className="rounded-xl border border-gray-800 bg-gray-950 p-4"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">
                        {version.version}
                      </span>

                      <span className="text-sm text-gray-400">
                        {version.status}
                      </span>
                    </div>

                    <div className="mt-2 text-sm text-gray-500">
                      Executions:{" "}
                      {version.execution_count}
                    </div>
                  </div>
                )
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

function InfoRow({
  label,
  value,
}: {
  label: string;
  value: string | null;
}) {
  return (
    <div className="border-b border-gray-800 pb-4 last:border-0 last:pb-0">
      <p className="text-xs text-gray-600">
        {label}
      </p>

      <p className="mt-1 break-all text-sm text-gray-300">
        {value || "Not available"}
      </p>
    </div>
  );
}
