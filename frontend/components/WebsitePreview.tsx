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
}

export default function WebsitePreview({
  html,
  baseUrl,
  activeField,
  itemSelector = "",
  onSelect,
}: WebsitePreviewProps) {
  const [selectedSelector, setSelectedSelector] =
    useState("");

  const [selectedTag, setSelectedTag] =
    useState("");

  const previewHtml = useMemo(() => {
    const parser = new DOMParser();
    const document = parser.parseFromString(
      html,
      "text/html"
    );

    // Never execute scripts from the scraped website.
    document
      .querySelectorAll("script")
      .forEach((script) => script.remove());

    if (baseUrl) {
      const existingBase =
        document.querySelector("base");

      if (existingBase) {
        existingBase.setAttribute(
          "href",
          baseUrl
        );
      } else {
        const base =
          document.createElement("base");

        base.setAttribute("href", baseUrl);
        document.head.prepend(base);
      }
    }

    const selectorScript =
      document.createElement("script");

    const safeActiveField =
      JSON.stringify(activeField);

    const safeItemSelector =
      JSON.stringify(itemSelector || "");

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

        function getSimpleSelector(element) {

          var selector =
            element.tagName.toLowerCase();

          /*
           * Prefer ID when available.
           */
          if (element.id) {
            return (
              selector +
              "#" +
              escapeSelector(element.id)
            );
          }

          /*
           * Use up to two classes.
           */
          var classes = Array.from(
            element.classList || []
          )
            .filter(Boolean)
            .slice(0, 2);

          if (classes.length > 0) {

            selector += classes
              .map(function (className) {
                return (
                  "." +
                  escapeSelector(className)
                );
              })
              .join("");
          }

          return selector;
        }

        function getCommonSelector(element) {
          var current = element;
          var bestSelector = "";

          while (
            current &&
            current.nodeType === 1 &&
            current.tagName.toLowerCase() !== "body" &&
            current.tagName.toLowerCase() !== "html"
          ) {
            var selector = current.tagName.toLowerCase();
            var classes = Array.from(current.classList || []).filter(Boolean).slice(0, 2);
            
            if (classes.length > 0) {
              selector += classes.map(function(c) { return "." + escapeSelector(c); }).join("");
            }

            // Check if this element has siblings with the same tag (and class if it has classes)
            var parent = current.parentElement;
            if (parent) {
              var similarSiblings = Array.from(parent.children).filter(function(child) {
                if (child === current) return false;
                if (child.tagName !== current.tagName) return false;
                // If the current element has classes, require the sibling to share at least the first class
                if (classes.length > 0) {
                   return child.classList.contains(classes[0]);
                }
                return true;
              });

              if (similarSiblings.length > 0) {
                // This is a repeating element! It's the perfect item boundary.
                return selector;
              }
            }

            // Fallback: keep the first class-based selector we saw in case no repeating siblings exist
            if (!bestSelector && classes.length > 0) {
               bestSelector = selector;
            }

            current = parent;
          }

          return bestSelector || element.tagName.toLowerCase();
        }

        function getSelector(
          element,
          stopAt
        ) {
          var parts = [];
          var current = element;

          while (
            current &&
            current.nodeType === 1 &&
            current !== stopAt
          ) {
            var selector = getSimpleSelector(current);
            var parent = current.parentElement;

            if (parent) {
              var sameTag = Array.from(parent.children).filter(function (child) {
                return child.tagName === current.tagName;
              });

              // Only append nth-of-type if it's not the topmost relative element directly under the stopAt boundary.
              // This ensures maximum cross-item matching even if the user selected a boundary that is slightly too high (like an outer wrapper).
              if (sameTag.length > 1 && parent !== stopAt) {
                var index = sameTag.indexOf(current) + 1;
                selector += ":nth-of-type(" + index + ")";
              }
            }

            parts.unshift(selector);
            current = parent;
          }

          return parts.join(" > ");
        }

        /*
         * Find the actual element the user
         * intended to select.
         */
        function findFieldElement(
          target,
          field
        ) {

          var fieldMap = {

            title:
              "h1, h2, h3, h4, h5, h6, .title, .headline",

            link:
              "a[href], area[href]",

            date:
              "time, [datetime], .date, .published, .published-date",

            description:
              "p, .description, .summary, .excerpt",

            image:
              "img, picture",

            author:
              ".author, .byline, [rel='author']",

            category:
              ".category, .section, [rel='category']"
          };

          var selector =
            fieldMap[field];

          if (!selector) {
            return target;
          }

          try {

            var closest =
              target.closest(selector);

            if (closest) {
              return closest;
            }

          } catch (error) {
            console.error(
              "Field selector error:",
              error
            );
          }

          return target;
        }

        function clearSelection(field) {

          document
            .querySelectorAll(
              '[data-rss-xtract-field="' +
                field +
                '"]'
            )
            .forEach(function (element) {

              element.removeAttribute(
                "data-rss-xtract-field"
              );

            });
        }

        /*
         * Hover effect.
         */
        document.addEventListener(
          "mouseover",
          function (event) {
            var target = event.target;
            if (!(target instanceof Element)) {
              return;
            }

            var hoverSelector = target.tagName.toLowerCase();
            if (ACTIVE_FIELD === "item") {
               hoverSelector = getCommonSelector(target);
            } else if (ACTIVE_FIELD === "pagination") {
               hoverSelector = getSelector(target);
            } else {
               // For fields, highlight similar elements inside the items if ITEM_SELECTOR exists
               if (ITEM_SELECTOR) {
                  try {
                    var itemRoot = target.closest(ITEM_SELECTOR);
                    if (itemRoot) {
                      var relSel = getSelector(target, itemRoot);
                      if (relSel) {
                        hoverSelector = ITEM_SELECTOR + " " + relSel;
                      }
                    }
                  } catch (e) {}
               }
               // Fallback if not inside item or error
               if (!hoverSelector || hoverSelector === target.tagName.toLowerCase()) {
                  hoverSelector = getCommonSelector(target);
               }
            }

            try {
              document.querySelectorAll(hoverSelector).forEach(function (el) {
                el.setAttribute("data-rss-xtract-hover", "true");
              });
            } catch (e) {
              target.setAttribute("data-rss-xtract-hover", "true");
            }
          }
        );

        document.addEventListener(
          "mouseout",
          function (event) {
            document.querySelectorAll('[data-rss-xtract-hover="true"]').forEach(function (el) {
              el.removeAttribute("data-rss-xtract-hover");
            });
          }
        );

        /*
         * Main selection handler.
         */
        document.addEventListener(
          "click",
          function (event) {

            event.preventDefault();
            event.stopPropagation();

            var target = event.target;

            if (!(target instanceof Element)) {
              return;
            }

            /*
             * ==========================
             * ITEM / BOUNDARY SELECTION
             * ==========================
             *
             * Produce a common selector that
             * matches ALL repeated siblings,
             * not just the one that was clicked.
             */
            if (ACTIVE_FIELD === "item") {

              var commonSelector =
                getCommonSelector(target);

              clearSelection("item");

              /*
               * Highlight every element that
               * matches the common selector.
               */
              try {
                document
                  .querySelectorAll(commonSelector)
                  .forEach(function (el) {
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
              }

              window.parent.postMessage(
                {
                  type:
                    "RSS_XTRACT_ELEMENT_SELECTED",

                  field: "item",

                  tag:
                    target.tagName.toLowerCase(),

                  selector: commonSelector
                },
                "*"
              );

              return;
            }

            /*
             * ==========================
             * PAGINATION SELECTION
             * ==========================
             *
             * Pagination lives outside the
             * article boundary — skip the
             * item-boundary check entirely.
             */
            if (ACTIVE_FIELD === "pagination") {

              var paginationSelector =
                getSelector(target);

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

                  selector: paginationSelector
                },
                "*"
              );

              return;
            }

            /*
             * ==========================
             * FIELD SELECTION
             * ==========================
             */

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
                target.closest(
                  ITEM_SELECTOR
                );

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

            /*
             * Find the appropriate element
             * for the requested field.
             */
            var selected =
              findFieldElement(
                target,
                ACTIVE_FIELD
              );

            /*
             * Make sure the selected field
             * is actually inside the article.
             */
            if (
              selected !== itemRoot &&
              !itemRoot.contains(selected)
            ) {

              selected = target;
            }

            /*
             * Generate selector relative
             * to the article boundary.
             */
            var relativeSelector =
              getSelector(
                selected,
                itemRoot
              );

            if (!relativeSelector) {

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

            try {
              document.querySelectorAll(ITEM_SELECTOR + " " + relativeSelector).forEach(function(el) {
                 el.setAttribute("data-rss-xtract-field", ACTIVE_FIELD);
              });
            } catch(e) {
              selected.setAttribute(
                "data-rss-xtract-field",
                ACTIVE_FIELD
              );
            }

            window.parent.postMessage(
              {
                type:
                  "RSS_XTRACT_ELEMENT_SELECTED",

                field: ACTIVE_FIELD,

                tag:
                  selected.tagName.toLowerCase(),

                selector:
                  relativeSelector
              },
              "*"
            );

          },
          true
        );

        /*
         * Selection styling.
         */
        var style =
          document.createElement("style");

        style.textContent =

          '[data-rss-xtract-hover="true"] {' +
          'outline: 2px solid #2563eb !important;' +
          'outline-offset: 2px !important;' +
          'cursor: crosshair !important;' +
          '}' +

          '[data-rss-xtract-field="item"] {' +
          'outline: 3px solid #dc2626 !important;' +
          'outline-offset: 3px !important;' +
          '}' +

          '[data-rss-xtract-field="title"],' +
          '[data-rss-xtract-field="link"],' +
          '[data-rss-xtract-field="date"],' +
          '[data-rss-xtract-field="description"],' +
          '[data-rss-xtract-field="image"],' +
          '[data-rss-xtract-field="author"],' +
          '[data-rss-xtract-field="category"] {' +
          'outline: 3px solid #16a34a !important;' +
          'outline-offset: 2px !important;' +
          '}' +

          '[data-rss-xtract-field="pagination"] {' +
          'outline: 3px solid #9333ea !important;' +
          'outline-offset: 2px !important;' +
          '}';

        document.head.appendChild(style);

      })();
    `;

    document.body.appendChild(
      selectorScript
    );

    return (
      "<!DOCTYPE html>" +
      document.documentElement.outerHTML
    );

  }, [
    html,
    baseUrl,
    activeField,
    itemSelector,
  ]);

  /*
   * Reset the display when changing
   * selection mode.
   */
  useEffect(() => {

    setSelectedSelector("");
    setSelectedTag("");

  }, [activeField]);

  /*
   * Receive selection from iframe.
   */
  useEffect(() => {

    const handleMessage = (
      event: MessageEvent
    ) => {

      if (!event.data) {
        return;
      }

      /*
       * Selection error.
       */
      if (
        event.data.type ===
        "RSS_XTRACT_SELECTOR_ERROR"
      ) {

        setSelectedTag("Error");

        setSelectedSelector(
          event.data.message ||
            "Unable to select element."
        );

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

      setSelectedSelector(
        data.selector
      );

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
      : activeField
          .charAt(0)
          .toUpperCase() +
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
            </span>

            {" "}in the preview

          </p>

        </div>

        <div className="rounded-lg bg-gray-950 px-3 py-2 font-mono text-xs text-gray-400">

          {selectedTag
            ? `${selectedTag} \u2192 ${selectedSelector}`
            : "Click an element"}

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