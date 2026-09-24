"use client";

interface PaginationConfigProps {
  value: string;
  activeField: string;
  onChange: (value: string) => void;
  onSelectField: () => void;
}

export default function PaginationConfig({
  value,
  activeField,
  onChange,
  onSelectField,
}: PaginationConfigProps) {

  const paginationActive =
    activeField === "pagination";

  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
      <p className="text-sm font-medium text-blue-400">
        Step 3
      </p>

      <h2 className="mt-1 text-xl font-semibold">
        Pagination
      </h2>

      <p className="mt-2 text-sm leading-6 text-gray-500">
        Optional. Specify the CSS selector for the
        link that takes the scraper to the next
        page.
      </p>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-purple-900/60 bg-purple-950/30 p-4">

        <div>

          <p className="text-sm font-medium text-purple-300">

            {paginationActive
              ? "Pagination selection active"
              : "Select the Next Page link"}

          </p>

          <p className="mt-1 text-xs text-gray-500">

            {paginationActive
              ? "Click the Next / Load More button anywhere on the preview."
              : "The element can be outside the article boundary."}

          </p>

        </div>

        <button
          type="button"
          onClick={onSelectField}
          className={[
            "shrink-0 rounded-lg px-3 py-2 text-xs font-semibold text-white transition",
            paginationActive
              ? "bg-purple-600"
              : "border border-gray-700 bg-gray-900 text-gray-300 hover:border-purple-500 hover:text-white",
          ].join(" ")}
        >

          {paginationActive
            ? "Selecting..."
            : "Select in preview"}

        </button>

      </div>

      <div className="mt-5">
        <label
          htmlFor="pagination-selector"
          className="mb-2 block text-sm font-medium text-gray-300"
        >
          Next page selector
        </label>

        <input
          id="pagination-selector"
          value={value}
          onChange={(event) =>
            onChange(event.target.value)
          }
          placeholder="a.next-page, .pagination .next"
          className="w-full rounded-xl border border-gray-700 bg-gray-950 px-4 py-3 font-mono text-sm text-white outline-none placeholder:text-gray-700 focus:border-blue-500"
        />
      </div>

      <div className="mt-4 rounded-lg bg-gray-950 px-4 py-3 text-xs text-gray-600">
        Leave empty if the website has no
        pagination.
      </div>
    </section>
  );
}