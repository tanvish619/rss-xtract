"use client";

import type { RenderingMode as RenderingModeType } from "../lib/types";

interface RenderingModeProps {
  value: RenderingModeType;
  onChange: (
    value: RenderingModeType
  ) => void;
}

export default function RenderingMode({
  value,
  onChange,
}: RenderingModeProps) {
  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
      <h2 className="text-lg font-semibold">
        Rendering Mode
      </h2>

      <p className="mt-2 text-sm leading-6 text-gray-500">
        Choose how the scraper should load the
        website.
      </p>

      <div className="mt-5 space-y-3">
        <button
          type="button"
          onClick={() =>
            onChange("request")
          }
          className={[
            "w-full rounded-xl border p-4 text-left transition",
            value === "request"
              ? "border-blue-500 bg-blue-950/30"
              : "border-gray-800 bg-gray-950 hover:border-gray-700",
          ].join(" ")}
        >
          <p className="font-medium">
            HTTP Request
          </p>

          <p className="mt-1 text-xs leading-5 text-gray-500">
            Faster option for websites where the
            article HTML is already present in the
            initial response.
          </p>
        </button>

        <button
          type="button"
          onClick={() =>
            onChange("js")
          }
          className={[
            "w-full rounded-xl border p-4 text-left transition",
            value === "js"
              ? "border-blue-500 bg-blue-950/30"
              : "border-gray-800 bg-gray-950 hover:border-gray-700",
          ].join(" ")}
        >
          <p className="font-medium">
            JavaScript / Playwright
          </p>

          <p className="mt-1 text-xs leading-5 text-gray-500">
            Use a browser when content is rendered
            dynamically by JavaScript.
          </p>
        </button>
      </div>
    </section>
  );
}