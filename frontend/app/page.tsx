import Link from "next/link";

import Navigation from "../components/Navigation";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navigation />

      <main>
        <section className="mx-auto max-w-7xl px-6 pb-20 pt-24">
          <div className="mx-auto max-w-4xl text-center">
            <div className="inline-flex rounded-full border border-blue-900 bg-blue-950/40 px-4 py-2 text-sm text-blue-300">
              Turn websites into RSS feeds
            </div>

            <h1 className="mt-7 text-5xl font-bold tracking-tight sm:text-6xl">
              Build an RSS feed from
              <span className="text-blue-500">
                {" "}any website.
              </span>
            </h1>

            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-gray-500">
              RSS Xtract lets you visually select
              article content from a website and
              generate a structured RSS feed without
              writing scraping code yourself.
            </p>

            <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row">
              <Link
                href="/create"
                className="rounded-xl bg-blue-600 px-7 py-4 font-semibold transition hover:bg-blue-500"
              >
                Create RSS Feed
              </Link>

              <Link
                href="/dashboard"
                className="rounded-xl border border-gray-700 px-7 py-4 font-semibold text-gray-300 transition hover:border-gray-500 hover:text-white"
              >
                View Dashboard
              </Link>
            </div>
          </div>
        </section>

        <section className="border-y border-gray-900 bg-gray-950/60">
          <div className="mx-auto grid max-w-7xl gap-px bg-gray-800 md:grid-cols-3">
            <Feature
              number="01"
              title="Preview"
              description="Enter a website URL and inspect the actual page inside RSS Xtract."
            />

            <Feature
              number="02"
              title="Select"
              description="Visually identify the article container and map title, link, date, image and other fields."
            />

            <Feature
              number="03"
              title="Generate"
              description="Save the configuration and turn it into a reusable scraping workflow and RSS feed."
            />
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-6 py-20">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Capability
              title="CSS Selectors"
              description="Precise field-level extraction using selectors."
            />

            <Capability
              title="JavaScript Sites"
              description="Playwright support for dynamically rendered pages."
            />

            <Capability
              title="Pagination"
              description="Follow next-page links to collect more articles."
            />

            <Capability
              title="Versioned Feeds"
              description="Keep scraper configurations versioned as they evolve."
            />
          </div>
        </section>
      </main>
    </div>
  );
}

function Feature({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-gray-950 p-8">
      <p className="text-sm font-bold text-blue-500">
        {number}
      </p>

      <h2 className="mt-4 text-xl font-semibold">
        {title}
      </h2>

      <p className="mt-3 text-sm leading-6 text-gray-500">
        {description}
      </p>
    </div>
  );
}

function Capability({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
      <h3 className="font-semibold">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-gray-500">
        {description}
      </p>
    </div>
  );
}