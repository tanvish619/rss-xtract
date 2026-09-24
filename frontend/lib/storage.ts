import type {
  Feed,
  FeedDraft,
  ScraperConfiguration,
  StoredFeed,
} from "./types";

const DRAFT_KEY = "rss-xtract-draft";
const FEEDS_KEY = "rss-xtract-feeds";

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function saveDraft(
  draft: FeedDraft
): void {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.setItem(
    DRAFT_KEY,
    JSON.stringify(draft)
  );
}

export function getDraft(): FeedDraft | null {
  if (!isBrowser()) {
    return null;
  }

  const raw =
    window.localStorage.getItem(DRAFT_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as FeedDraft;
  } catch {
    return null;
  }
}

export function clearDraft(): void {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.removeItem(DRAFT_KEY);
}

export function saveStoredFeed(
  storedFeed: StoredFeed
): void {
  if (!isBrowser()) {
    return;
  }

  const feeds = getStoredFeeds();

  const existingIndex = feeds.findIndex(
    (item) =>
      item.feed.id === storedFeed.feed.id
  );

  if (existingIndex >= 0) {
    feeds[existingIndex] = storedFeed;
  } else {
    feeds.unshift(storedFeed);
  }

  window.localStorage.setItem(
    FEEDS_KEY,
    JSON.stringify(feeds)
  );
}

export function getStoredFeeds(): StoredFeed[] {
  if (!isBrowser()) {
    return [];
  }

  const raw =
    window.localStorage.getItem(FEEDS_KEY);

  if (!raw) {
    return [];
  }

  try {
    return JSON.parse(raw) as StoredFeed[];
  } catch {
    return [];
  }
}

export function getStoredFeed(
  feedId: string
): StoredFeed | null {
  const feeds = getStoredFeeds();

  return (
    feeds.find(
      (item) => item.feed.id === feedId
    ) || null
  );
}

export function deleteStoredFeed(
  feedId: string
): void {
  if (!isBrowser()) {
    return;
  }

  const feeds = getStoredFeeds().filter(
    (item) => item.feed.id !== feedId
  );

  window.localStorage.setItem(
    FEEDS_KEY,
    JSON.stringify(feeds)
  );
}

export function createLocalFeed(
  draft: FeedDraft
): StoredFeed {
  const now =
    new Date().toISOString();

  const feedId =
    crypto.randomUUID();

  const sourceId =
    crypto.randomUUID();

  const feed: Feed = {
    id: feedId,
    source_id: sourceId,
    name:
      draft.name.trim() ||
      "Untitled Feed",
    description:
      draft.description.trim() ||
      null,
    status: "created",
    refresh_interval_seconds: 1800,
    current_version: "v1.1",
    created_at: now,
    updated_at: now,
    last_run_at: null,
    last_success_at: null,
    last_error: null,
    article_count: 0,
    source_url: draft.url,
    versions: [],
    feed_url: `/feed/${feedId}.xml`,
  };

  const storedFeed: StoredFeed = {
    feed,
    configuration:
      draft.configuration,
  };

  saveStoredFeed(storedFeed);

  return storedFeed;
}

export function updateLocalFeed(
  feedId: string,
  updates: Partial<Feed>
): StoredFeed | null {
  const existing =
    getStoredFeed(feedId);

  if (!existing) {
    return null;
  }

  const updated: StoredFeed = {
    ...existing,
    feed: {
      ...existing.feed,
      ...updates,
      updated_at:
        new Date().toISOString(),
    },
  };

  saveStoredFeed(updated);

  return updated;
}

export function updateLocalConfiguration(
  feedId: string,
  configuration: ScraperConfiguration
): StoredFeed | null {
  const existing =
    getStoredFeed(feedId);

  if (!existing) {
    return null;
  }

  const updated: StoredFeed = {
    ...existing,
    configuration,
    feed: {
      ...existing.feed,
      updated_at:
        new Date().toISOString(),
    },
  };

  saveStoredFeed(updated);

  return updated;
}