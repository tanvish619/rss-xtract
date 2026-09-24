"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import Navigation from "../../components/Navigation";
import FeedCard from "../../components/FeedCard";

import {
  getStoredFeeds,
} from "../../lib/storage";

import type {
  StoredFeed,
} from "../../lib/types";

export default function DashboardPage() {
  const [feeds, setFeeds] =
    useState<StoredFeed[]>([]);

  useEffect(() => {
    setFeeds(getStoredFeeds());
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navigation />

      <main className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-col justify-between gap-6 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-medium uppercase tracking-wider text-blue-400">
              RSS Xtract
            </p>

            <h1 className="mt-2 text-4xl font-bold">
              Dashboard
            </h1>

            <p className="mt-3 text-gray-500">
              Manage your generated RSS feeds.
            </p>
          </div>

          <Link
            href="/create"
            className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            + Create Feed
          </Link>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-gray-800 bg-gray-900 p-5">
            <p className="text-sm text-gray-500">
              Total Feeds
            </p>

            <p className="mt-2 text-3xl font-bold">
              {feeds.length}
            </p>
          </div>

          <div className="rounded-2xl border border-gray-800 bg-gray-900 p-5">
            <p className="text-sm text-gray-500">
              Successful
            </p>

            <p className="mt-2 text-3xl font-bold text-green-400">
              {
                feeds.filter(
                  (item) =>
                    item.feed.status ===
                    "success"
                ).length
              }
            </p>
          </div>

          <div className="rounded-2xl border border-gray-800 bg-gray-900 p-5">
            <p className="text-sm text-gray-500">
              Failed
            </p>

            <p className="mt-2 text-3xl font-bold text-red-400">
              {
                feeds.filter(
                  (item) =>
                    item.feed.status ===
                    "failed"
                ).length
              }
            </p>
          </div>
        </div>

        <section className="mt-10">
          {feeds.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-gray-800 bg-gray-900/50 px-6 py-16 text-center">
              <div className="mx-auto max-w-md">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-950 text-2xl">
                  RSS
                </div>

                <h2 className="mt-5 text-xl font-semibold">
                  No feeds yet
                </h2>

                <p className="mt-2 text-sm leading-6 text-gray-500">
                  Create your first RSS feed by
                  selecting article elements from a
                  website.
                </p>

                <Link
                  href="/create"
                  className="mt-6 inline-flex rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold hover:bg-blue-500"
                >
                  Create Your First Feed
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid gap-5 md:grid-cols-2">
              {feeds.map((item) => (
                <FeedCard
                  key={item.feed.id}
                  feed={item.feed}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}