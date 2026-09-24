"use client";

import { useState } from "react";

interface MaxItemsConfigProps {
  value: number | null;
  onChange: (value: number | null) => void;
}

const PRESET_OPTIONS = [
  { label: "10", value: 10 },
  { label: "25", value: 25 },
  { label: "50", value: 50 },
  { label: "100", value: 100 },
  { label: "250", value: 250 },
  { label: "500", value: 500 },
  { label: "1000", value: 1000 },
];

export default function MaxItemsConfig({
  value,
  onChange,
}: MaxItemsConfigProps) {

  /*
   * Track whether the user is typing a custom
   * number. We store the raw string so they can
   * edit freely before we parse it.
   */
  const [customInput, setCustomInput] =
    useState("");

  const [showCustom, setShowCustom] =
    useState(false);

  const isUnlimited = value === null;

  /*
   * Determine which preset button (if any)
   * is currently active.
   */
  const activePreset =
    !isUnlimited && !showCustom &&
    PRESET_OPTIONS.some((o) => o.value === value)
      ? value
      : null;

  const isCustomActive =
    !isUnlimited && showCustom;

  function handlePresetClick(preset: number) {
    setShowCustom(false);
    setCustomInput("");
    onChange(preset);
  }

  function handleCustomChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const raw = event.target.value;
    setCustomInput(raw);

    const parsed = parseInt(raw, 10);

    if (
      !isNaN(parsed) &&
      parsed >= 1 &&
      parsed <= 10_000
    ) {
      onChange(parsed);
    }
  }

  function handleCustomBlur() {
    const parsed = parseInt(customInput, 10);

    if (
      isNaN(parsed) ||
      parsed < 1 ||
      parsed > 10_000
    ) {
      /*
       * Invalid — reset to the previous valid
       * value or the default.
       */
      setCustomInput(
        value !== null ? String(value) : "50"
      );

      if (value === null) {
        onChange(50);
      }
    }
  }

  function handleUnlimitedChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    if (event.target.checked) {
      setShowCustom(false);
      setCustomInput("");
      onChange(null);
    } else {
      onChange(50);
    }
  }

  function openCustom() {
    setShowCustom(true);
    setCustomInput(
      value !== null ? String(value) : "50"
    );
    if (value === null) {
      onChange(50);
    }
  }

  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">

      <p className="text-sm font-medium text-blue-400">
        Step 4
      </p>

      <h2 className="mt-1 text-xl font-semibold">
        Maximum Items
      </h2>

      <p className="mt-2 text-sm leading-6 text-gray-500">
        Maximum number of article items to include
        in the generated RSS feed. Applies after
        all pages are scraped.
      </p>

      {/*
       * Preset buttons
       */}
      <div className="mt-5 flex flex-wrap gap-2">

        {PRESET_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            disabled={isUnlimited}
            onClick={() =>
              handlePresetClick(option.value)
            }
            className={[
              "rounded-lg px-4 py-2 text-sm font-semibold transition",
              activePreset === option.value
                ? "bg-blue-600 text-white"
                : "border border-gray-700 bg-gray-950 text-gray-300 hover:border-blue-500 hover:text-white",
              isUnlimited
                ? "cursor-not-allowed opacity-40"
                : "",
            ].join(" ")}
          >
            {option.label}
          </button>
        ))}

        {/*
         * Custom value button
         */}
        <button
          type="button"
          disabled={isUnlimited}
          onClick={openCustom}
          className={[
            "rounded-lg px-4 py-2 text-sm font-semibold transition",
            isCustomActive
              ? "bg-blue-600 text-white"
              : "border border-gray-700 bg-gray-950 text-gray-300 hover:border-blue-500 hover:text-white",
            isUnlimited
              ? "cursor-not-allowed opacity-40"
              : "",
          ].join(" ")}
        >
          Custom
        </button>

      </div>

      {/*
       * Custom input field — only visible when
       * the user clicked "Custom"
       */}
      {showCustom && !isUnlimited && (

        <div className="mt-4">

          <label
            htmlFor="max-items-custom"
            className="mb-2 block text-sm font-medium text-gray-300"
          >
            Custom limit
            <span className="ml-2 text-xs text-gray-500">
              (1 – 10,000)
            </span>
          </label>

          <input
            id="max-items-custom"
            type="number"
            min={1}
            max={10_000}
            value={customInput}
            onChange={handleCustomChange}
            onBlur={handleCustomBlur}
            placeholder="e.g. 75"
            className="w-40 rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 font-mono text-sm text-white outline-none placeholder:text-gray-700 focus:border-blue-500"
          />

        </div>

      )}

      {/*
       * Current selected value display
       */}
      {!isUnlimited && !showCustom && (

        <div className="mt-4 rounded-lg bg-gray-950 px-4 py-3 text-xs text-gray-400">
          RSS feed will contain at most{" "}
          <span className="font-semibold text-white">
            {value}
          </span>{" "}
          items.
        </div>

      )}

      {isUnlimited && (

        <div className="mt-4 rounded-lg bg-gray-950 px-4 py-3 text-xs text-gray-400">
          All matching items will be included
          — no limit applied.
        </div>

      )}

      {/*
       * No limit / All checkbox
       */}
      <label className="mt-5 flex cursor-pointer items-center gap-3">

        <input
          type="checkbox"
          id="max-items-unlimited"
          checked={isUnlimited}
          onChange={handleUnlimitedChange}
          className="h-4 w-4 cursor-pointer accent-blue-500"
        />

        <span className="text-sm text-gray-300">
          No limit — include all matching items
        </span>

      </label>

    </section>
  );
}
