import type {
  CreateFeedPayload,
  CreateVersionPayload,
  Feed,
  FeedRun,
  FeedVersion,
  PreviewResponse,
  ScraperConfiguration,
} from "./types";

export type { PreviewResponse } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

async function parseResponse<T>(
  response: Response
): Promise<T> {
  if (!response.ok) {
    let message = "Request failed";

    try {
      const data = await response.json();

      if (typeof data?.detail === "string") {
        message = data.detail;
      } else if (typeof data?.message === "string") {
        message = data.message;
      }
    } catch {
      try {
        const text = await response.text();

        if (text) {
          message = text;
        }
      } catch {
        // Keep default error message.
      }
    }

    throw new Error(message);
  }

  return response.json();
}

export async function previewWebsite(
  url: string
): Promise<PreviewResponse> {
  const response = await fetch(
    `${API_BASE_URL}/preview`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url,
      }),
    }
  );

  return parseResponse<PreviewResponse>(response);
}

export async function buildFeed(
  payload: {
    url: string;
    name: string;
    description?: string | null;
    refresh_interval_seconds?: number;
    configuration: ScraperConfiguration;
  }
): Promise<{
  feed_id: string;
  feed_version_id: string;
  version: string;
  reused: boolean;
  task_id: string | null;
  feed_url: string;
}> {
  const response = await fetch(
    `${API_BASE_URL}/feeds/build`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  return parseResponse(response);
}

export async function createSource(
  name: string,
  url: string
): Promise<{ message: string; source_id: string }> {
  const params = new URLSearchParams();

  params.set("name", name);
  params.set("url", url);

  const response = await fetch(
    `${API_BASE_URL}/sources/?${params.toString()}`,
    {
      method: "POST",
    }
  );

  return parseResponse(response);
}

export async function createFeed(
  payload: CreateFeedPayload
): Promise<{ message: string; feed_id: string }> {
  const response = await fetch(
    `${API_BASE_URL}/feeds/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  return parseResponse(response);
}

export async function createFeedVersion(
  feedId: string,
  payload: CreateVersionPayload
): Promise<{
  message: string;
  feed_version_id: string;
  version: string;
}> {
  const response = await fetch(
    `${API_BASE_URL}/feeds/${feedId}/versions`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  return parseResponse(response);
}

export async function createConfiguration(
  configuration: {
    feed_version_id: string;
  } & ScraperConfiguration
): Promise<{
  message: string;
  configuration_id: string;
}> {
  const response = await fetch(
    `${API_BASE_URL}/configurations/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(configuration),
    }
  );

  return parseResponse(response);
}

export async function getFeed(
  feedId: string
): Promise<Feed> {
  const response = await fetch(
    `${API_BASE_URL}/feeds/${feedId}`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  return parseResponse<Feed>(response);
}

export async function getFeedVersion(
  feedId: string
): Promise<FeedVersion> {
  const response = await fetch(
    `${API_BASE_URL}/feeds/${feedId}/version`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  return parseResponse<FeedVersion>(response);
}

export async function runFeed(
  feedId: string
): Promise<FeedRun> {
  const response = await fetch(
    `${API_BASE_URL}/feeds/${feedId}/run`,
    {
      method: "POST",
    }
  );

  return parseResponse<FeedRun>(response);
}

export function getFeedUrl(
  feedId: string
): string {
  return `${API_BASE_URL}/feed/${feedId}.xml`;
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}
