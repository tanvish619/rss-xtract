"use client";

import type { SelectorState } from "../lib/types";
import type { VisualSelectorField } from "./WebsitePreview";

interface FieldMapperProps {
  selectors: SelectorState;
  activeField: VisualSelectorField;
  hasItemSelector: boolean;

  onChange: (
    field: keyof SelectorState,
    value: string
  ) => void;

  onSelectField: (
    field: VisualSelectorField
  ) => void;
}

interface FieldDefinition {
  key: Exclude<
    VisualSelectorField,
    "item"
  >;

  label: string;
  description: string;
  placeholder: string;
  required?: boolean;
}

const fields: FieldDefinition[] = [

  {
    key: "title",
    label: "Title",
    description:
      "The article headline.",
    placeholder:
      ".title, h2, .headline",
    required: true,
  },

  {
    key: "link",
    label: "Link",
    description:
      "The article URL element.",
    placeholder:
      "a.title-link, h2 a",
    required: true,
  },

  {
    key: "date",
    label: "Date",
    description:
      "Publication date or timestamp.",
    placeholder:
      "time, .published-date",
  },

  {
    key: "description",
    label: "Description",
    description:
      "Short article summary.",
    placeholder:
      ".summary, .excerpt",
  },

  {
    key: "image",
    label: "Image",
    description:
      "Article thumbnail or image.",
    placeholder:
      "img.thumbnail",
  },

  {
    key: "author",
    label: "Author",
    description:
      "Article author.",
    placeholder:
      ".author, .byline",
  },

  {
    key: "category",
    label: "Category",
    description:
      "Article category or section.",
    placeholder:
      ".category, .section",
  },
];

export default function FieldMapper({
  selectors,
  activeField,
  hasItemSelector,
  onChange,
  onSelectField,
}: FieldMapperProps) {

  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">

      <div>

        <p className="text-sm font-medium text-blue-400">
          Step 2
        </p>

        <h2 className="mt-1 text-xl font-semibold">
          Map Article Fields
        </h2>

        <p className="mt-2 text-sm leading-6 text-gray-500">

          Select a field below, then click the
          corresponding element inside the article
          in the preview.

        </p>

      </div>

      {!hasItemSelector && (

        <div className="mt-5 rounded-xl border border-amber-900/60 bg-amber-950/30 px-4 py-3 text-xs text-amber-300">

          Select the article/item boundary first.
          Field selection is scoped to that
          boundary.

        </div>

      )}

      <div className="mt-6 space-y-4">

        {fields.map((field) => {

          const selected =
            activeField === field.key;

          return (

            <div
              key={field.key}
              className="rounded-xl border border-gray-800 bg-gray-950 p-4"
            >

              <div className="flex items-center justify-between gap-4">

                <div>

                  <label
                    htmlFor={`selector-${field.key}`}
                    className="text-sm font-medium text-gray-200"
                  >

                    {field.label}

                    {field.required && (
                      <span className="ml-1 text-red-400">
                        *
                      </span>
                    )}

                  </label>

                  <p className="mt-1 text-xs text-gray-600">
                    {field.description}
                  </p>

                </div>

                <button
                  type="button"
                  disabled={!hasItemSelector}
                  onClick={() =>
                    onSelectField(
                      field.key
                    )
                  }
                  className={[
                    "shrink-0 rounded-lg px-3 py-2 text-xs font-semibold transition",

                    selected
                      ? "bg-green-600 text-white"
                      : "border border-gray-700 bg-gray-900 text-gray-300 hover:border-blue-500 hover:text-white",

                    !hasItemSelector
                      ? "cursor-not-allowed opacity-40"
                      : "",
                  ].join(" ")}
                >

                  {selected
                    ? "Selecting..."
                    : "Select in preview"}

                </button>

              </div>

              <input
                id={`selector-${field.key}`}
                value={
                  selectors[field.key]
                }
                onChange={(event) =>
                  onChange(
                    field.key,
                    event.target.value
                  )
                }
                placeholder={
                  field.placeholder
                }
                className="mt-3 w-full rounded-lg border border-gray-800 bg-gray-900 px-3 py-2.5 font-mono text-sm text-white outline-none placeholder:text-gray-700 focus:border-blue-500"
              />

            </div>

          );
        })}

      </div>

    </section>
  );
}