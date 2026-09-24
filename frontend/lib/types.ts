export type RenderingMode = "request" | "js";

export type FeedStatus =
  | "created"
  | "ready"
  | "running"
  | "success"
  | "failed";

export interface ArticleCandidate {
  tag: string;
  class: string[] | null;
  id: string | null;
  text: string;
}

export interface PreviewRequest {
  url: string;
}

export interface PreviewResponse {
  message: string;
  url: string;
  html_length: number;
  page_title: string | null;
  html: string;
  article_candidates: ArticleCandidate[];
}

export interface ScraperConfiguration {
  item_selector: string;
  title_selector: string | null;
  link_selector: string | null;
  date_selector: string | null;
  description_selector: string | null;
  image_selector: string | null;
  author_selector: string | null;
  category_selector: string | null;
  pagination_selector: string | null;
  rendering_mode: RenderingMode;
  max_items: number | null;
}

export interface FeedVersionSummary {
  id: string;
  version: string;
  status: FeedStatus;
  execution_count: number;
  last_execution_at: string | null;
  last_success_at: string | null;
  last_error: string | null;
}

export interface Feed {
  id: string;
  source_id: string;
  name: string;
  description: string | null;
  status: FeedStatus;
  refresh_interval_seconds: number;
  current_version: string;
  created_at: string;
  updated_at: string;
  last_run_at: string | null;
  last_success_at: string | null;
  last_error: string | null;
  article_count: number;
  source_url: string;
  versions: FeedVersionSummary[];
  feed_url: string;
}

export interface FeedDraft {
  url: string;
  name: string;
  description: string;
  configuration: ScraperConfiguration;
}

export interface FeedVersion {
  id: string;
  feed_id: string;
  version_major: number;
  version_minor: number;
  config_hash: string;
  config_path: string;
  script_path: string;
  status: FeedStatus;
  execution_count: number;
  last_execution_at: string | null;
  last_success_at: string | null;
  last_error: string | null;
  created_at: string;
}

export interface FeedRun {
  id: string;
  feed_version_id: string;
  started_at: string;
  finished_at: string | null;
  status: "running" | "success" | "failed";
  article_count: number;
  duration_ms: number | null;
  error_message: string | null;
}

export interface NormalizedArticle {
  guid: string;
  title: string;
  link: string;
  description: string | null;
  content: string | null;
  image_url: string | null;
  author: string | null;
  category: string | null;
  published_at: string | null;
}

export interface SelectorState {
  item: string;
  title: string;
  link: string;
  date: string;
  description: string;
  image: string;
  author: string;
  category: string;
  pagination: string;
}

export type SelectorField = keyof SelectorState;

export interface StoredFeed {
  feed: Feed;
  configuration: ScraperConfiguration;
}

export interface CreateFeedPayload {
  source_id: string;
  name: string;
  description?: string;
  refresh_interval_seconds: number;
}

export interface CreateVersionPayload {
  version_major: number;
  version_minor: number;
}

export interface ApiError {
  detail?: string;
  message?: string;
}
