import Link from 'next/link';
import { Shield } from 'lucide-react';

export function PublicFooter() {
  return (
    <footer className="mt-auto border-t border-gray-100 bg-white">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          {/* Brand */}
          <div className="col-span-2 sm:col-span-1">
            <Link href="/" className="flex items-center gap-2 font-bold text-gray-900">
              <div className="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-600 text-white">
                <Shield className="h-4 w-4" />
              </div>
              <span className="text-sm">[PROJECT_NAME]</span>
            </Link>
            <p className="mt-3 text-xs text-gray-400 leading-relaxed">
              Open-source food safety intelligence. Built for public health.
            </p>
          </div>

          {/* Public */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Public</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/search" className="hover:text-emerald-700">Find Restaurants</Link></li>
              <li><Link href="/recalls" className="hover:text-emerald-700">Recalls</Link></li>
              <li><Link href="/advisories" className="hover:text-emerald-700">Advisories</Link></li>
            </ul>
          </div>

          {/* Platform */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Platform</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/dashboard" className="hover:text-emerald-700">Operator Login</Link></li>
              <li>
                <a href="https://github.com/[org]/[PROJECT_NAME]" className="hover:text-emerald-700" target="_blank" rel="noopener noreferrer">
                  GitHub
                </a>
              </li>
              <li>
                <a href="https://github.com/[org]/[PROJECT_NAME]/blob/main/docs/" className="hover:text-emerald-700" target="_blank" rel="noopener noreferrer">
                  Docs
                </a>
              </li>
            </ul>
          </div>

          {/* Project */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">Project</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <a href="https://github.com/[org]/[PROJECT_NAME]/blob/main/CONTRIBUTING.md" className="hover:text-emerald-700" target="_blank" rel="noopener noreferrer">
                  Contribute
                </a>
              </li>
              <li>
                <a href="https://github.com/[org]/[PROJECT_NAME]/blob/main/SECURITY.md" className="hover:text-emerald-700" target="_blank" rel="noopener noreferrer">
                  Security
                </a>
              </li>
              <li>
                <a href="https://github.com/[org]/[PROJECT_NAME]/blob/main/ROADMAP.md" className="hover:text-emerald-700" target="_blank" rel="noopener noreferrer">
                  Roadmap
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-gray-100 pt-6 text-xs text-gray-400">
          <p>&copy; {new Date().getFullYear()} [PROJECT_NAME] Contributors. Apache 2.0.</p>
          <p>Data sourced from FDA, USDA FSIS, and participating health departments.</p>
        </div>
      </div>
    </footer>
  );
}
