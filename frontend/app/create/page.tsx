"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import Navigation from "../../components/Navigation";
import URLInput from "../../components/URLInput";
import WebsitePreview, {
  type VisualSelectorField,
} from "../../components/WebsitePreview";
import SelectorPanel from "../../components/SelectorPanel";
import FieldMapper from "../../components/FieldMapper";
import PaginationConfig from "../../components/PaginationConfig";
import RenderingMode from "../../components/RenderingMode";
import MaxItemsConfig from "../../components/MaxItemsConfig";

import {
  previewWebsite,
  buildFeed,
} from "../../lib/api";

import {
  saveDraft,
} from "../../lib/storage";

import type {
  PreviewResponse,
  ScraperConfiguration,
  SelectorState,
} from "../../lib/types";

const emptySelectors: SelectorState = {
  item: "",
  title: "",
  link: "",
  date: "",
  description: "",
  image: "",
  author: "",
  category: "",
  pagination: "",
};

export default function CreateFeedPage() {
  const router = useRouter();

  const [url, setUrl] = useState("");
  const [preview, setPreview] =
    useState<PreviewResponse | null>(null);

  const [selectors, setSelectors] =
    useState<SelectorState>(emptySelectors);

  const [renderingMode, setRenderingMode] =
    useState<"request" | "js">("request");

  const [feedName, setFeedName] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [step, setStep] =
    useState(1);

  const [activeSelection, setActiveSelection] =
    useState<VisualSelectorField>("item");

  const [maxItems, setMaxItems] =
    useState<number | null>(50);

  useEffect(() => {
    saveDraft({
      url,
      name: feedName,
      description,
      configuration: {
        item_selector: selectors.item,
        title_selector: selectors.title || null,
        link_selector: selectors.link || null,
        date_selector: selectors.date || null,
        description_selector:
          selectors.description || null,
        image_selector: selectors.image || null,
        author_selector: selectors.author || null,
        category_selector:
          selectors.category || null,
        pagination_selector:
          selectors.pagination || null,
        rendering_mode: renderingMode,
        max_items: maxItems,
      },
    });
  }, [
    url,
    feedName,
    description,
    selectors,
    renderingMode,
    maxItems,
  ]);

  async function handlePreview() {
    if (!url.trim()) {
      setError("Enter a website URL first.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const result =
        await previewWebsite(url.trim());

      setPreview(result);
      setStep(2);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to preview website."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleSelectorChange(
    field: keyof SelectorState,
    value: string
  ) {
    setSelectors((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function handleVisualSelection(
    field: VisualSelectorField,
    selector: string,
    _tag: string
  ) {
    setSelectors((current) => ({
      ...current,
      [field]: selector,
    }));

    /*
     * Keep the selected field as the active mode.
     * The user can click another "Select in preview"
     * button to change the mode.
     */
    setActiveSelection(field);
  }

  async function handleCreateFeed() {
    if (!url.trim()) {
      setError("Website URL is required.");
      return;
    }

    if (!selectors.item.trim()) {
      setError(
        "Select an article/item container before creating the feed."
      );
      return;
    }

    if (!feedName.trim()) {
      setError("Give your feed a name.");
      return;
    }

    const configuration: ScraperConfiguration = {
      item_selector: selectors.item,
      title_selector: selectors.title || null,
      link_selector: selectors.link || null,
      date_selector: selectors.date || null,
      description_selector:
        selectors.description || null,
      image_selector: selectors.image || null,
      author_selector: selectors.author || null,
      category_selector:
        selectors.category || null,
      pagination_selector:
        selectors.pagination || null,
      rendering_mode: renderingMode,
      max_items: maxItems,
    };

    setError("");
    setLoading(true);

    try {
      const result = await buildFeed({
        url: url.trim(),
        name: feedName.trim(),
        description: description.trim() || null,
        refresh_interval_seconds: 1800,
        configuration,
      });

      router.push(`/feeds/${result.feed_id}`);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to create RSS feed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navigation />

      <main className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-10">
          <p className="text-sm font-medium uppercase tracking-wider text-blue-400">
            RSS Xtract
          </p>

          <h1 className="mt-2 text-4xl font-bold">
            Create RSS Feed
          </h1>

          <p className="mt-3 max-w-2xl text-gray-400">
            Select content from any website and
            turn it into a structured RSS feed.
          </p>
        </div>

        <div className="mb-8 flex items-center gap-3">
          {[1, 2, 3].map((number) => (
            <div
              key={number}
              className="flex items-center gap-3"
            >
              <div
                className={[
                  "flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold",
                  step >= number
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800 text-gray-500",
                ].join(" ")}
              >
                {number}
              </div>

              {number < 3 && (
                <div className="h-px w-10 bg-gray-800" />
              )}
            </div>
          ))}
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-900 bg-red-950/40 px-5 py-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {step === 1 && (
          <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
            <h2 className="text-xl font-semibold">
              1. Enter Website
            </h2>

            <p className="mt-2 text-sm text-gray-500">
              Start with the page containing the
              articles you want in your RSS feed.
            </p>

            <div className="mt-6">
              <URLInput
                value={url}
                onChange={setUrl}
                onSubmit={handlePreview}
                loading={loading}
              />
            </div>
          </section>
        )}

        {step >= 2 && preview && (
          <>
            <section className="mb-8">
              <WebsitePreview
                html={preview.html}
                baseUrl={preview.url}
                activeField={activeSelection}
                itemSelector={selectors.item}
                onSelect={handleVisualSelection}
              />
            </section>

            <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
              <div>
                <SelectorPanel
                  selectors={selectors}
                  activeField={activeSelection}
                  onChange={handleSelectorChange}
                  onSelectField={setActiveSelection}
                />

                <div className="mt-8">
                  <FieldMapper
                    selectors={selectors}
                    activeField={activeSelection}
                    hasItemSelector={Boolean(
                      selectors.item.trim()
                    )}
                    onChange={handleSelectorChange}
                    onSelectField={setActiveSelection}
                  />
                </div>

                <div className="mt-8">
                  <PaginationConfig
                    value={selectors.pagination}
                    activeField={activeSelection}
                    onChange={(value) =>
                      handleSelectorChange(
                        "pagination",
                        value
                      )
                    }
                    onSelectField={() =>
                      setActiveSelection(
                        "pagination"
                      )
                    }
                  />
                </div>

                <div className="mt-8">
                  <MaxItemsConfig
                    value={maxItems}
                    onChange={setMaxItems}
                  />
                </div>
              </div>

              <aside className="space-y-6">
                <RenderingMode
                  value={renderingMode}
                  onChange={setRenderingMode}
                />

                <div className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
                  <h2 className="text-lg font-semibold">
                    Feed Details
                  </h2>

                  <div className="mt-5 space-y-4">
                    <div>
                      <label className="mb-2 block text-sm text-gray-400">
                        Feed name
                      </label>

                      <input
                        value={feedName}
                        onChange={(event) =>
                          setFeedName(
                            event.target.value
                          )
                        }
                        placeholder="My News Feed"
                        className="w-full rounded-lg border border-gray-700 bg-gray-950 px-4 py-3 text-sm outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="mb-2 block text-sm text-gray-400">
                        Description
                      </label>

                      <textarea
                        value={description}
                        onChange={(event) =>
                          setDescription(
                            event.target.value
                          )
                        }
                        placeholder="Articles from this website..."
                        rows={4}
                        className="w-full resize-none rounded-lg border border-gray-700 bg-gray-950 px-4 py-3 text-sm outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleCreateFeed}
                  disabled={loading}
                  className="w-full rounded-xl bg-blue-600 px-5 py-4 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "Creating RSS Feed..."
                    : "Create RSS Feed"}
                </button>
              </aside>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
