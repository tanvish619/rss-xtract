"use client";

import type { SelectorState } from "../lib/types";
import type { VisualSelectorField } from "./WebsitePreview";

interface SelectorPanelProps {
  selectors: SelectorState;
  activeField: VisualSelectorField;
  onChange: (
    field: keyof SelectorState,
    value: string
  ) => void;
  onSelectField: (
    field: VisualSelectorField
  ) => void;
}

export default function SelectorPanel({
  selectors,
  activeField,
  onChange,
  onSelectField,
}: SelectorPanelProps) {

  const boundaryActive =
    activeField === "item";

  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">

      <div>

        <p className="text-sm font-medium text-blue-400">
          Step 1
        </p>

        <h2 className="mt-1 text-xl font-semibold">
          Select Article Container
        </h2>

        <p className="mt-2 text-sm leading-6 text-gray-500">
          First select one complete article/card.
          This becomes the parent scope for all
          other selectors.
        </p>

      </div>

      <div className="mt-6 rounded-xl border border-blue-900/60 bg-blue-950/30 p-4">

        <div className="flex flex-wrap items-center justify-between gap-3">

          <div>

            <p className="text-sm font-medium text-blue-300">

              {boundaryActive
                ? "Boundary selection active"
                : "Boundary selected"}

            </p>

            <p className="mt-1 text-xs text-gray-500">

              {boundaryActive
                ? "Click the outer container of one article/card in the preview."
                : "You can reselect the boundary at any time."}

            </p>

          </div>

          <button
            type="button"
            onClick={() =>
              onSelectField("item")
            }
            className={[
              "rounded-lg px-4 py-2 text-sm font-semibold text-white transition",
              boundaryActive
                ? "bg-blue-600"
                : "bg-gray-700 hover:bg-gray-600",
            ].join(" ")}
          >

            {boundaryActive
              ? "Selecting Boundary"
              : "Select Boundary"}

          </button>

        </div>

      </div>

      <div className="mt-6">

        <label
          htmlFor="item-selector"
          className="mb-2 block text-sm font-medium text-gray-300"
        >
          Item selector
        </label>

        <input
          id="item-selector"
          value={selectors.item}
          onChange={(event) =>
            onChange(
              "item",
              event.target.value
            )
          }
          placeholder="article, .post, .news-item"
          className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 font-mono text-sm text-white outline-none placeholder:text-gray-700 focus:border-blue-500"
        />

        <p className="mt-2 text-xs text-gray-600">
          All title, link, date, image, etc.
          selectors will be searched inside this
          element.
        </p>

      </div>

    </section>
  );
}