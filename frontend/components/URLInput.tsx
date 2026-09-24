"use client";

interface URLInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading?: boolean;
}

export default function URLInput({
  value,
  onChange,
  onSubmit,
  loading = false,
}: URLInputProps) {
  return (
    <div>
      <label
        htmlFor="website-url"
        className="mb-2 block text-sm font-medium text-gray-300"
      >
        Website URL
      </label>

      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          id="website-url"
          type="url"
          value={value}
          onChange={(event) =>
            onChange(event.target.value)
          }
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              onSubmit();
            }
          }}
          placeholder="https://example.com/news"
          className="min-w-0 flex-1 rounded-xl border border-gray-700 bg-gray-950 px-4 py-3.5 text-white outline-none placeholder:text-gray-600 focus:border-blue-500"
        />

        <button
          type="button"
          onClick={onSubmit}
          disabled={loading}
          className="rounded-xl bg-blue-600 px-7 py-3.5 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading
            ? "Loading..."
            : "Preview Website"}
        </button>
      </div>
    </div>
  );
}