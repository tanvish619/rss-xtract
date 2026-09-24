"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navigation() {
  const pathname = usePathname();

  const links = [
    {
      href: "/",
      label: "Home",
    },
    {
      href: "/dashboard",
      label: "Dashboard",
    },
    {
      href: "/create",
      label: "Create Feed",
    },
  ];

  return (
    <header className="border-b border-gray-800 bg-gray-950/95">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link
          href="/"
          className="text-xl font-bold tracking-tight"
        >
          RSS <span className="text-blue-500">Xtract</span>
        </Link>

        <nav className="flex items-center gap-2">
          {links.map((link) => {
            const active =
              pathname === link.href;

            return (
              <Link
                key={link.href}
                href={link.href}
                className={[
                  "rounded-lg px-4 py-2 text-sm transition",
                  active
                    ? "bg-blue-600 text-white"
                    : "text-gray-400 hover:bg-gray-900 hover:text-white",
                ].join(" ")}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}