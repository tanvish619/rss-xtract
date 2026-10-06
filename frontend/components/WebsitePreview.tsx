"use client";

import { useEffect, useMemo, useState } from "react";
import type { SelectorField } from "../lib/types";

export type VisualSelectorField = SelectorField;

interface WebsitePreviewProps {
  html: string;
  baseUrl?: string;
  activeField: VisualSelectorField;
  itemSelector?: string;
  onSelect: (
    field: VisualSelectorField,
    selector: string,
    tag: string
  ) => void;
}

interface SelectedElementMessage {
  type: "RSS_XTRACT_ELEMENT_SELECTED";
  field: VisualSelectorField;
  tag: string;
  selector: string;
  matchCount?: number;
}

export default function WebsitePreview({
  html,
  baseUrl,
  activeField,
  itemSelector = "",
  onSelect,
}: WebsitePreviewProps) {
  const [selectedSelector, setSelectedSelector] = useState("");
  const [selectedTag, setSelectedTag] = useState("");
  const [matchCount, setMatchCount] = useState<number | null>(null);

  const previewHtml = useMemo(() => {
    const parser = new DOMParser();
    const document = parser.parseFromString(html, "text/html");

    // Never execute scripts from the scraped website.
    document
      .querySelectorAll("script")
      .forEach((script) => script.remove());

    // Remove page-level anti-clickjacking styles that can hide
    // the document when the fetched page is rendered inside our iframe.
    document.querySelectorAll("style").forEach((style) => {
      const css = style.textContent || "";

      const isAntiClickjack =
        /anti[-_ ]?clickjack/i.test(style.id || "") ||
        (/body\s*\{[^}]*display\s*:\s*none/i.test(css) &&
          /important/i.test(css));

      if (isAntiClickjack) {
        style.remove();
      }
    });

    // Strip cookie banners, GDPR consent overlays, and modal backdrops
    // so they never block the preview iframe or prevent clicks on articles.
    const cookieSelectors = [
      "[id*='onetrust']", "[class*='onetrust']", ".onetrust-pc-dark-filter",
      "[id*='CookieReports']", "[class*='CookieReports']", "[id*='wscr']", "[class*='wscr']",
      "[id*='cookiebanner']", "[id*='cookie-banner']", "[id*='cookie-consent']", "[id*='CookieConsent']",
      "[id*='CybotCookiebot']", "[class*='CybotCookiebot']", "#CybotCookiebotDialog", "#CybotCookiebotDialogBodyUnderlay",
      "[id*='didomi']", "[class*='didomi']",
      "[id*='usercentrics']", "[class*='usercentrics']",
      "[class*='cookie-overlay']", "[class*='cookie-backdrop']", "[class*='consent-banner']", "[class*='consent-modal']",
      "[class*='modal-backdrop']", ".modal-backdrop", ".overlay-backdrop",
      "section.cookie-component", "#onetrust-consent-sdk",
      "#prefilterableLoader", "[id*='prefilterableLoader']", "[id*='loader-overlay']",
      "[class*='loader-overlay']", "[class*='loading-overlay']", "[class*='spinner-overlay']",
      "[class*='js-banner-xf']", "[class*='banner-xf']", "[class*='modal-cookiebanner']",
      "[class*='cookieBanner']", "[class*='cookie-banner']", "[class*='cookies-region']",
      "#cookies-banner", "#cookie-form", "[id*='cookies-banner']", "[id*='modalCookies']",
      "[id*='tarteaucitron']", "[class*='tarteaucitron']", "#axeptio_overlay",
      ".modal-cookiebanner__module", ".modal-cookiebanner__main-container"
    ];

    cookieSelectors.forEach((sel) => {
      try {
        document.querySelectorAll(sel).forEach((el) => el.remove());
      } catch (e) {}
    });

    if (baseUrl) {
      // 1. Prepend <base> tag for any other relative lookups
      const existingBase = document.querySelector("base");
      if (existingBase) {
        existingBase.setAttribute("href", baseUrl);
      } else {
        const base = document.createElement("base");
        base.setAttribute("href", baseUrl);
        if (document.head) {
          document.head.prepend(base);
        } else {
          document.documentElement.prepend(base);
        }
      }

      // 2. Explicitly rewrite relative stylesheet and image URLs to absolute URLs
      // to ensure full cross-origin CSS styling inside the sandboxed iframe
      try {
        const baseObj = new URL(baseUrl);
        document.querySelectorAll("link[href]").forEach((link) => {
          const href = link.getAttribute("href");
          if (href && !href.startsWith("data:") && !href.startsWith("blob:") && !href.startsWith("http://") && !href.startsWith("https://") && !href.startsWith("//")) {
            try {
              link.setAttribute("href", new URL(href, baseUrl).href);
            } catch (e) {}
          } else if (href && href.startsWith("//")) {
            link.setAttribute("href", `${baseObj.protocol}${href}`);
          }
        });

        document.querySelectorAll("img[src], source[srcset]").forEach((img) => {
          const src = img.getAttribute("src");
          if (src && !src.startsWith("data:") && !src.startsWith("blob:") && !src.startsWith("http://") && !src.startsWith("https://") && !src.startsWith("//")) {
            try {
              img.setAttribute("src", new URL(src, baseUrl).href);
            } catch (e) {}
          } else if (src && src.startsWith("//")) {
            img.setAttribute("src", `${baseObj.protocol}${src}`);
          }
        });
      } catch (e) {}
    }

    const selectorScript = document.createElement("script");

    const safeActiveField = JSON.stringify(activeField);
    const safeItemSelector = JSON.stringify(itemSelector || "");

    selectorScript.textContent = `
      (function () {

        var ACTIVE_FIELD = ${safeActiveField};
        var ITEM_SELECTOR = ${safeItemSelector};

        function escapeSelector(value) {
          if (
            window.CSS &&
            typeof window.CSS.escape === "function"
          ) {
            return window.CSS.escape(value);
          }

          return String(value).replace(
            /([ !"#$%&'()*+,./:;<=>?@[\\\\\\\\\\\\]^\\\`{|}~])/g,
            "\\\\\\\\$1"
          );
        }

        var GENERIC_CLASSES = [
          "active", "hover", "focus", "selected", "open", "closed", "hide", "show",
          "d-flex", "d-block", "d-none", "flex", "grid", "row", "col", "container",
          "w-100", "h-100", "wrapper", "clearfix", "section", "main", "content", "body"
        ];

        var NON_ARTICLE_TAGS = ["nav", "header", "footer", "aside", "form", "script", "style", "noscript", "menu"];
        var ARTICLE_SEMANTIC_KEYWORDS = [
          "article", "news", "press", "card", "story", "post", "entry", "teaser", "release",
          "item", "media", "report", "result", "record", "listing", "publication", "notice",
          "blog", "feed-item", "filterable"
        ];
        var WRAPPER_KEYWORDS = [
          "wrapper", "container", "parent", "litcomplet", "collection", "archive", "content",
          "section", "main", "body", "results-wrapper", "list-wrap", "table-body"
        ];

        function isNonArticleArea(el) {
          var curr = el;
          while (curr && curr.nodeType === 1 && curr.tagName.toLowerCase() !== "body" && curr.tagName.toLowerCase() !== "html") {
            var tag = curr.tagName.toLowerCase();
            if (NON_ARTICLE_TAGS.indexOf(tag) !== -1) {
              return true;
            }
            var role = (curr.getAttribute("role") || "").toLowerCase();
            if (role === "navigation" || role === "banner" || role === "contentinfo" || role === "search") {
              return true;
            }
            var cls = (curr.className || "").toString().toLowerCase();
            var id = (curr.id || "").toLowerCase();
            for (var i = 0; i < ["nav", "menu", "footer", "breadcrumb", "pagination"].length; i++) {
              var kw = ["nav", "menu", "footer", "breadcrumb", "pagination"][i];
              if (cls.indexOf(kw) !== -1 || id.indexOf(kw) !== -1) {
                return true;
              }
            }
            curr = curr.parentElement;
          }
          return false;
        }

        function filterClasses(classList) {
          return Array.from(classList || [])
            .filter(function(c) {
              if (
                !c ||
                typeof c !== "string" ||
                c.startsWith("ng-") ||
                c.startsWith("v-") ||
                c.startsWith("data-") ||
                c.startsWith("_") ||
                c.startsWith("css-") ||
                c.startsWith("jsx-")
              ) {
                return false;
              }

              if (c.indexOf(":") !== -1 || c.indexOf("[") !== -1 || c.match(/^[0-9]/)) {
                return false;
              }

              return GENERIC_CLASSES.indexOf(c.toLowerCase()) === -1;
            });
        }

        function getSimpleSelector(element, isRelative) {
          var tag = element.tagName.toLowerCase();

          if (
            !isRelative &&
            element.id &&
            !element.id.match(/\\d{2,}/)
          ) {
            return tag + "#" + escapeSelector(element.id);
          }

          var classes = filterClasses(element.classList).slice(0, 2);

          if (classes.length > 0) {
            return (
              tag +
              classes
                .map(function (c) {
                  return "." + escapeSelector(c);
                })
                .join("")
            );
          }

          return tag;
        }

        function getCommonSelector(element) {
          var current = element;
          var candidateContainers = [];
          var depth = 0;

          while (
            current &&
            current.nodeType === 1 &&
            current.tagName.toLowerCase() !== "body" &&
            current.tagName.toLowerCase() !== "html"
          ) {
            depth++;
            if (!isNonArticleArea(current)) {
              var tag = current.tagName.toLowerCase();
              var classes = filterClasses(current.classList);
              var parent = current.parentElement;

              if (parent) {
                var semanticClass = classes.find(function(c) {
                  var low = c.toLowerCase();
                  var isWrap = WRAPPER_KEYWORDS.some(function(w) { return low.indexOf(w) !== -1; });
                  if (isWrap) return false;
                  return ARTICLE_SEMANTIC_KEYWORDS.some(function(kw) { return low.indexOf(kw) !== -1; });
                });

                var isWrapperClass = classes.some(function(c) {
                  var low = c.toLowerCase();
                  return WRAPPER_KEYWORDS.some(function(w) { return low.indexOf(w) !== -1; });
                });

                var baseSelectors = [];
                if (semanticClass) {
                  baseSelectors.push(tag + "." + escapeSelector(semanticClass));
                  baseSelectors.push("." + escapeSelector(semanticClass));
                }
                if (classes.length > 0) {
                  baseSelectors.push(tag + "." + escapeSelector(classes[0]));
                  baseSelectors.push("." + escapeSelector(classes[0]));
                  if (classes.length >= 2) {
                    baseSelectors.push(tag + "." + escapeSelector(classes[0]) + "." + escapeSelector(classes[1]));
                  }
                }
                if (tag === "article") {
                  baseSelectors.push("article");
                }
                if (tag === "li" && (parent.tagName.toLowerCase() === "ul" || parent.tagName.toLowerCase() === "ol")) {
                  var pClasses = filterClasses(parent.classList);
                  if (pClasses.length > 0) {
                    baseSelectors.push("." + escapeSelector(pClasses[0]) + " > li");
                  }
                }

                // Build candidate selectors
                var candSelectors = [];
                baseSelectors.forEach(function(bs) {
                  candSelectors.push(bs);
                  if (parent.tagName.toLowerCase() !== "body" && parent.tagName.toLowerCase() !== "html") {
                    var pCls = filterClasses(parent.classList);
                    if (pCls.length > 0) {
                      candSelectors.push("." + escapeSelector(pCls[0]) + " > " + bs);
                    }
                  }
                });

                candSelectors.forEach(function(sel) {
                  try {
                    var matched = document.querySelectorAll(sel);
                    var validMatches = Array.from(matched).filter(function(el) { return !isNonArticleArea(el); });
                    var matchCount = validMatches.length;

                    if (matchCount >= 2 && matchCount <= 200) {
                      var score = 0;
                      if (matchCount >= 3 && matchCount <= 60) score += 35;
                      else score += 15;

                      if (semanticClass || sel.indexOf("article") !== -1) score += 50;
                      if (classes.length > 0) score += 20;

                      // Depth bonus: strongly prefer the immediate repeating card container close to the click
                      score += Math.max(0, 40 - depth * 6);

                      // Check if items contain headings or links
                      var hasHeadings = validMatches.some(function(m) { return m.querySelector("h1, h2, h3, h4, h5, h6"); });
                      var hasLinks = validMatches.some(function(m) { return m.querySelector("a[href]") || m.tagName.toLowerCase() === "a"; });
                      var textLen = current.textContent ? current.textContent.trim().length : 0;

                      if (hasHeadings) score += 25;
                      if (hasLinks) score += 25;
                      if (textLen >= 25 && textLen <= 2500) score += 20;

                      // Penalize wrapper containers
                      if (isWrapperClass || sel.indexOf("wrapper") !== -1 || sel.indexOf("container") !== -1) {
                        score -= 80;
                      }

                      // Penalize bare generic tags
                      if (sel === "div" || sel === "section" || sel.endsWith(" > div")) {
                        score -= 70;
                      }

                      candidateContainers.push({
                        selector: sel,
                        count: matchCount,
                        score: score
                      });
                    }
                  } catch (e) {}
                });
              }
            }
            current = current.parentElement;
          }

          if (candidateContainers.length > 0) {
            candidateContainers.sort(function(a, b) { return b.score - a.score; });
            return candidateContainers[0].selector;
          }

          // Fallback
          var fallbackClasses = filterClasses(element.classList);
          if (fallbackClasses.length > 0) {
            return element.tagName.toLowerCase() + "." + escapeSelector(fallbackClasses[0]);
          }
          return element.tagName.toLowerCase();
        }

        function getRelativeSelector(element, stopAt) {
          if (!element || element === stopAt) {
            return "";
          }

          var tag = element.tagName.toLowerCase();
          var classes = filterClasses(element.classList);

          var allItems = [];
          try {
            if (ITEM_SELECTOR) {
              allItems = Array.from(document.querySelectorAll(ITEM_SELECTOR));
            }
          } catch (e) {}

          var candidates = [];

          // 1. Semantic Tag patterns
          if (["h1", "h2", "h3", "h4", "h5", "h6", "time", "img", "p", "a", "span", "strong", "em"].indexOf(tag) !== -1) {
            candidates.push(tag);
          }

          if (tag === "a" || element.querySelector("a")) {
            candidates.push("h1 a", "h2 a", "h3 a", "h4 a", "h5 a", "h6 a", "a");
          }

          // 2. Class patterns
          classes.forEach(function(c) {
            candidates.push("." + escapeSelector(c));
            candidates.push(tag + "." + escapeSelector(c));
          });

          if (classes.length >= 2) {
            candidates.push("." + escapeSelector(classes[0]) + "." + escapeSelector(classes[1]));
            candidates.push(tag + "." + escapeSelector(classes[0]) + "." + escapeSelector(classes[1]));
          }

          // 3. Hierarchical path
          var parts = [];
          var current = element;
          while (current && current.nodeType === 1 && current !== stopAt) {
            var sel = getSimpleSelector(current, true);
            parts.unshift(sel);
            current = current.parentElement;
          }
          if (parts.length > 0) {
            candidates.push(parts.join(" > "));
            candidates.push(parts.join(" "));
          }

          // Score and validate candidates across all items
          var bestCand = "";
          var bestScore = -999;

          for (var i = 0; i < candidates.length; i++) {
            var cand = candidates[i];
            try {
              var foundInStopAt = stopAt.querySelector(cand);
              if (
                foundInStopAt === element ||
                (foundInStopAt && foundInStopAt.contains(element)) ||
                element.contains(foundInStopAt)
              ) {
                if (allItems.length <= 1) {
                  return cand;
                }

                // Test across all items
                var coverage = 0;
                var totalMatches = 0;
                for (var j = 0; j < allItems.length; j++) {
                  var m = allItems[j].querySelectorAll(cand);
                  if (m.length > 0) coverage++;
                  totalMatches += m.length;
                }

                var candScore = coverage * 20 - Math.abs(totalMatches - coverage) * 10;
                if (candScore > bestScore) {
                  bestScore = candScore;
                  bestCand = cand;
                }
              }
            } catch (e) {}
          }

          return bestCand || (parts.length > 0 ? parts.join(" > ") : tag);
        }

        function findFieldElement(target, field, itemRoot) {
          if (!target) return target;

          if (field === "title") {
            var tag = target.tagName.toLowerCase();
            if (["h1", "h2", "h3", "h4", "h5", "h6"].indexOf(tag) !== -1) return target;
            var cls = (target.className || "").toString().toLowerCase();
            if (cls.indexOf("title") !== -1 || cls.indexOf("headline") !== -1 || cls.indexOf("header") !== -1) return target;

            if (itemRoot && itemRoot !== target) {
              var heading = target.closest("h1, h2, h3, h4, h5, h6, [class*='title'], [class*='headline'], [class*='header']");
              if (heading && itemRoot.contains(heading)) {
                return heading;
              }
              var innerHeading = target.querySelector("h1, h2, h3, h4, h5, h6, [class*='title'], [class*='headline']");
              if (innerHeading) return innerHeading;
            }
            return target;
          }

          if (field === "link") {
            if (target.tagName.toLowerCase() === "a") return target;
            var parentA = target.closest("a[href]");
            if (parentA) return parentA;
            var childA = target.querySelector("a[href]");
            if (childA) return childA;
            if (itemRoot && itemRoot.tagName.toLowerCase() === "a") return itemRoot;
            return target;
          }

          if (field === "date") {
            var tag = target.tagName.toLowerCase();
            if (tag === "time" || target.hasAttribute("datetime")) return target;
            var dateEl = target.closest("time, [datetime], [class*='date'], [class*='time'], [class*='published'], [class*='timestamp'], [class*='posted']");
            if (dateEl && (!itemRoot || itemRoot.contains(dateEl))) return dateEl;
            var innerDate = target.querySelector("time, [datetime], [class*='date'], [class*='time'], [class*='published']");
            if (innerDate) return innerDate;
            return target;
          }

          if (field === "image") {
            if (target.tagName.toLowerCase() === "img" || target.tagName.toLowerCase() === "picture") return target;
            var childImg = target.querySelector("img, picture");
            if (childImg) return childImg;
            var imgEl = target.closest("img, picture, [class*='thumb'], [class*='image'], [class*='photo'], [class*='media'], [style*='background']");
            if (imgEl && (!itemRoot || itemRoot.contains(imgEl))) return imgEl;
            return target;
          }

          if (field === "description") {
            var descEl = target.closest("p, [class*='desc'], [class*='summary'], [class*='excerpt'], [class*='text'], [class*='snippet'], [class*='body']");
            if (descEl && (!itemRoot || itemRoot.contains(descEl)) && descEl !== itemRoot) return descEl;
            var innerP = target.querySelector("p, [class*='desc'], [class*='summary'], [class*='excerpt'], [class*='text']");
            if (innerP) return innerP;
            return target;
          }

          if (field === "author") {
            var authEl = target.closest("[class*='author'], [class*='byline'], [rel='author']");
            if (authEl && (!itemRoot || itemRoot.contains(authEl))) return authEl;
            return target;
          }

          if (field === "category") {
            var catEl = target.closest("[class*='category'], [class*='section'], [class*='tag'], [rel='category'], [class*='badge'], [class*='pill']");
            if (catEl && (!itemRoot || itemRoot.contains(catEl))) return catEl;
            return target;
          }

          return target;
        }

        function clearSelection(field) {
          document
            .querySelectorAll(
              '[data-rss-xtract-field="' + field + '"]'
            )
            .forEach(function(element) {
              element.removeAttribute(
                "data-rss-xtract-field"
              );
            });
        }

        document.addEventListener(
          "mouseover",
          function(event) {
            var target = event.target;

            if (!(target instanceof Element)) {
              return;
            }

            var hoverSelector = target.tagName.toLowerCase();

            if (ACTIVE_FIELD === "item") {
              hoverSelector = getCommonSelector(target);
            } else if (ACTIVE_FIELD === "pagination") {
              hoverSelector = getSimpleSelector(
                target,
                false
              );
            } else {
              if (ITEM_SELECTOR) {
                try {
                  var itemRoot =
                    target.closest(ITEM_SELECTOR);

                  if (itemRoot) {
                    var relSel = getRelativeSelector(
                      target,
                      itemRoot
                    );

                    if (relSel) {
                      hoverSelector =
                        ITEM_SELECTOR +
                        " " +
                        relSel;
                    }
                  }
                } catch (e) {}
              }

              if (
                !hoverSelector ||
                hoverSelector === target.tagName.toLowerCase()
              ) {
                hoverSelector =
                  getCommonSelector(target);
              }
            }

            try {
              document
                .querySelectorAll(hoverSelector)
                .forEach(function(el) {
                  el.setAttribute(
                    "data-rss-xtract-hover",
                    "true"
                  );
                });
            } catch (e) {
              target.setAttribute(
                "data-rss-xtract-hover",
                "true"
              );
            }
          }
        );

        document.addEventListener(
          "mouseout",
          function() {
            document
              .querySelectorAll(
                '[data-rss-xtract-hover="true"]'
              )
              .forEach(function(el) {
                el.removeAttribute(
                  "data-rss-xtract-hover"
                );
              });
          }
        );

        document.addEventListener(
          "click",
          function(event) {
            event.preventDefault();
            event.stopPropagation();

            var target = event.target;

            if (!(target instanceof Element)) {
              return;
            }

            if (ACTIVE_FIELD === "item") {
              var commonSelector =
                getCommonSelector(target);

              clearSelection("item");

              var matchedCount = 0;

              try {
                var matched =
                  document.querySelectorAll(
                    commonSelector
                  );

                matchedCount = matched.length;

                matched.forEach(function(el) {
                  el.setAttribute(
                    "data-rss-xtract-field",
                    "item"
                  );
                });
              } catch (e) {
                target.setAttribute(
                  "data-rss-xtract-field",
                  "item"
                );

                matchedCount = 1;
              }

              window.parent.postMessage(
                {
                  type:
                    "RSS_XTRACT_ELEMENT_SELECTED",
                  field: "item",
                  tag:
                    target.tagName.toLowerCase(),
                  selector: commonSelector,
                  matchCount: matchedCount
                },
                "*"
              );

              return;
            }

            if (ACTIVE_FIELD === "pagination") {
              var paginationSelector =
                getSimpleSelector(
                  target,
                  false
                );

              clearSelection("pagination");

              target.setAttribute(
                "data-rss-xtract-field",
                "pagination"
              );

              window.parent.postMessage(
                {
                  type:
                    "RSS_XTRACT_ELEMENT_SELECTED",
                  field: "pagination",
                  tag:
                    target.tagName.toLowerCase(),
                  selector:
                    paginationSelector,
                  matchCount: 1
                },
                "*"
              );

              return;
            }

            if (!ITEM_SELECTOR) {
              window.parent.postMessage(
                {
                  type:
                    "RSS_XTRACT_SELECTOR_ERROR",
                  message:
                    "Select the article/item boundary first."
                },
                "*"
              );

              return;
            }

            var itemRoot = null;

            try {
              itemRoot =
                target.closest(ITEM_SELECTOR);
            } catch (error) {
              window.parent.postMessage(
                {
                  type:
                    "RSS_XTRACT_SELECTOR_ERROR",
                  message:
                    "The item selector is not valid CSS."
                },
                "*"
              );

              return;
            }

            if (!itemRoot) {
              window.parent.postMessage(
                {
                  type:
                    "RSS_XTRACT_SELECTOR_ERROR",
                  message:
                    "Click an element inside the selected article/item boundary."
                },
                "*"
              );

              return;
            }

            var selected = findFieldElement(
              target,
              ACTIVE_FIELD,
              itemRoot
            );

            if (
              selected !== itemRoot &&
              !itemRoot.contains(selected)
            ) {
              selected = target;
            }

            var relativeSelector =
              getRelativeSelector(
                selected,
                itemRoot
              );

            if (
              !relativeSelector &&
              selected !== itemRoot
            ) {
              window.parent.postMessage(
                {
                  type:
                    "RSS_XTRACT_SELECTOR_ERROR",
                  message:
                    "Could not create a selector inside the selected item."
                },
                "*"
              );

              return;
            }

            clearSelection(ACTIVE_FIELD);

            var fieldMatches = 0;

            try {
              var fullFieldSelector =
                relativeSelector
                  ? ITEM_SELECTOR +
                    " " +
                    relativeSelector
                  : ITEM_SELECTOR;

              var matches =
                document.querySelectorAll(
                  fullFieldSelector
                );

              fieldMatches = matches.length;

              matches.forEach(function(el) {
                el.setAttribute(
                  "data-rss-xtract-field",
                  ACTIVE_FIELD
                );
              });
            } catch (e) {
              selected.setAttribute(
                "data-rss-xtract-field",
                ACTIVE_FIELD
              );

              fieldMatches = 1;
            }

            window.parent.postMessage(
              {
                type:
                  "RSS_XTRACT_ELEMENT_SELECTED",
                field: ACTIVE_FIELD,
                tag:
                  selected.tagName.toLowerCase(),
                selector:
                  relativeSelector,
                matchCount: fieldMatches
              },
              "*"
            );
          },
          true
        );

        var style = document.createElement("style");

        style.textContent =
          "html, body {" +
          "  overflow: auto !important;" +
          "  position: static !important;" +
          "  height: auto !important;" +
          "}" +
          "[id*='onetrust'], [class*='onetrust']," +
          "[id*='CookieReports'], [class*='CookieReports']," +
          "[id*='cookiebanner'], [id*='cookie-banner'], [id*='cookie-consent']," +
          "[id*='CybotCookiebot'], [class*='CybotCookiebot']," +
          "[id*='didomi'], [class*='didomi']," +
          "[id*='usercentrics'], [class*='usercentrics']," +
          ".onetrust-pc-dark-filter, .modal-backdrop, .overlay-backdrop," +
          "[class*='cookie-overlay'], [class*='cookie-backdrop']," +
          "#prefilterableLoader, [id*='prefilterableLoader'], [id*='loader-overlay']," +
          "[class*='loader-overlay'], [class*='loading-overlay'], [class*='spinner-overlay']," +
          "[class*='js-banner-xf'], [class*='banner-xf'], [class*='modal-cookiebanner']," +
          "[class*='cookieBanner'], [class*='cookie-banner'], [class*='cookies-region']," +
          "#cookies-banner, #cookie-form, [id*='cookies-banner'], [id*='modalCookies']," +
          "[id*='tarteaucitron'], [class*='tarteaucitron'], #axeptio_overlay," +
          ".modal-cookiebanner__module, .modal-cookiebanner__main-container," +
          "section.cookie-component, #CybotCookiebotDialog, #CybotCookiebotDialogBodyUnderlay {" +
          "  display: none !important;" +
          "  visibility: hidden !important;" +
          "  pointer-events: none !important;" +
          "  z-index: -999 !important;" +
          "}" +
          '[data-rss-xtract-hover="true"] {' +
          "outline: 2px solid #2563eb !important;" +
          "outline-offset: 2px !important;" +
          "cursor: crosshair !important;" +
          "}" +
          '[data-rss-xtract-field="item"] {' +
          "outline: 3px solid #dc2626 !important;" +
          "outline-offset: 3px !important;" +
          "}" +
          '[data-rss-xtract-field="title"],' +
          '[data-rss-xtract-field="link"],' +
          '[data-rss-xtract-field="date"],' +
          '[data-rss-xtract-field="description"],' +
          '[data-rss-xtract-field="image"],' +
          '[data-rss-xtract-field="author"],' +
          '[data-rss-xtract-field="category"] {' +
          "outline: 3px solid #16a34a !important;" +
          "outline-offset: 2px !important;" +
          "}" +
          '[data-rss-xtract-field="pagination"] {' +
          "outline: 3px solid #9333ea !important;" +
          "outline-offset: 2px !important;" +
          "}";

        document.head.appendChild(style);
      })();
    `;

    document.body.appendChild(selectorScript);

    return (
      "<!DOCTYPE html>" +
      document.documentElement.outerHTML
    );
  }, [html, baseUrl, activeField, itemSelector]);

  useEffect(() => {
    setSelectedSelector("");
    setSelectedTag("");
    setMatchCount(null);
  }, [activeField]);

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (!event.data) {
        return;
      }

      if (
        event.data.type ===
        "RSS_XTRACT_SELECTOR_ERROR"
      ) {
        setSelectedTag("Error");
        setSelectedSelector(
          event.data.message ||
            "Unable to select element."
        );
        setMatchCount(null);
        return;
      }

      if (
        event.data.type !==
        "RSS_XTRACT_ELEMENT_SELECTED"
      ) {
        return;
      }

      const data =
        event.data as SelectedElementMessage;

      setSelectedTag(data.tag);
      setSelectedSelector(data.selector);
      setMatchCount(data.matchCount ?? null);

      onSelect(
        data.field,
        data.selector,
        data.tag
      );
    };

    window.addEventListener(
      "message",
      handleMessage
    );

    return () => {
      window.removeEventListener(
        "message",
        handleMessage
      );
    };
  }, [onSelect]);

  const fieldLabel =
    activeField === "item"
      ? "Article / Item Boundary"
      : activeField === "pagination"
        ? "Pagination / Next Page"
        : activeField.charAt(0).toUpperCase() +
          activeField.slice(1);

  return (
    <div className="overflow-hidden rounded-2xl border border-gray-800 bg-gray-900">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800 px-5 py-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-blue-400">
            Visual Selector
          </p>

          <p className="mt-1 text-sm text-gray-300">
            Select{" "}
            <span className="font-semibold text-white">
              {fieldLabel}
            </span>{" "}
            in the preview
          </p>
        </div>

        <div className="flex items-center gap-2">
          {matchCount !== null && (
            <span className="rounded-full bg-blue-900/60 px-2.5 py-1 text-xs font-medium text-blue-300 border border-blue-700/50">
              {matchCount} match
              {matchCount === 1 ? "" : "es"}
            </span>
          )}

          <div className="rounded-lg bg-gray-950 px-3 py-2 font-mono text-xs text-gray-400">
            {selectedTag
              ? `${selectedTag} → ${
                  selectedSelector || "(self)"
                }`
              : "Click an element"}
          </div>
        </div>
      </div>

      <div className="h-[620px] bg-white">
        <iframe
          title="Website Preview"
          srcDoc={previewHtml}
          sandbox="allow-scripts"
          className="h-full w-full border-0"
        />
      </div>
    </div>
  );
}