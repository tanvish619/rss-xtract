"use client";

import Link from "next/link";

import type { Feed } from "../lib/types";

interface FeedCardProps {
  feed: Feed;
}

export default function FeedCard({
  feed,
}: FeedCardProps) {
  const statusClasses = {
    created:
      "bg-gray-800 text-gray-300",
    ready:
      "bg-blue-950 text-blue-300",
    running:
      "bg-yellow-950 text-yellow-300",
    success:
      "bg-green-950 text-green-300",
    failed:
      "bg-red-950 text-red-300",
  };

  const statusClass =
    statusClasses[feed.status] ||
    statusClasses.created;

  return (
    <Link
      href={`/feeds/${feed.id}`}
      className="group block rounded-2xl border border-gray-800 bg-gray-900 p-6 transition hover:border-gray-700 hover:bg-gray-900/80"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h3 className="truncate text-lg font-semibold text-white group-hover:text-blue-400">
            {feed.name}
          </h3>

          <p className="mt-1 truncate text-sm text-gray-500">
            {feed.source_url}
          </p>
        </div>

        <span
          className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium capitalize ${statusClass}`}
        >
          {feed.status}
        </span>
      </div>

      {feed.description && (
        <p className="mt-4 line-clamp-2 text-sm leading-6 text-gray-400">
          {feed.description}
        </p>
      )}

      <div className="mt-6 grid grid-cols-2 gap-4 border-t border-gray-800 pt-5 sm:grid-cols-4">
        <div>
          <p className="text-xs text-gray-600">
            Version
          </p>

          <p className="mt-1 text-sm font-medium text-gray-300">
            {feed.current_version}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-600">
            Articles
          </p>

          <p className="mt-1 text-sm font-medium text-gray-300">
            {feed.article_count}
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-600">
            Refresh
          </p>

          <p className="mt-1 text-sm font-medium text-gray-300">
            {Math.round(
              feed.refresh_interval_seconds /
                60
            )}{" "}
            min
          </p>
        </div>

        <div>
          <p className="text-xs text-gray-600">
            Created
          </p>

          <p className="mt-1 text-sm font-medium text-gray-300">
            {new Date(
              feed.created_at
            ).toLocaleDateString()}
          </p>
        </div>
      </div>
    </Link>
  );
}