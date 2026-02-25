import Link from 'next/link';
import { Shield, Search, AlertTriangle, Activity, ChevronRight, ArrowRight } from 'lucide-react';
import { PublicNav } from '@/components/public/nav';
import { PublicFooter } from '@/components/public/footer';

export const metadata = {
  title: '[PROJECT_NAME] — Food Safety Intelligence',
  description: 'Search restaurant inspection grades, active recalls, and outbreak advisories. Open-source food safety platform.',
};

const features = [
  {
    icon: Search,
    title: 'Restaurant Grades',
    description: 'Search any restaurant by name or location. See the latest inspection grade, score, and violation history — sourced directly from health department records.',
    href: '/search',
    cta: 'Find a restaurant',
    color: 'emerald',
  },
  {
    icon: AlertTriangle,
    title: 'Active Recalls',
    description: 'Live FDA and USDA FSIS recall database. Filter by hazard type, state, or product. New recalls sync automatically every night.',
    href: '/recalls',
    cta: 'Check recalls',
    color: 'red',
  },
  {
    icon: Activity,
    title: 'Outbreak Advisories',
    description: 'Anonymized, aggregated alerts when case clustering crosses investigation thresholds. No personally identifiable information is ever published.',
    href: '/advisories',
    cta: 'See advisories',
    color: 'amber',
  },
];

const stats = [
  { label: 'Establishments tracked', value: '—' },
  { label: 'Active recalls', value: '—' },
  { label: 'Inspections in database', value: '—' },
  { label: 'Data sources', value: 'FDA · USDA · 50 states' },
];

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <PublicNav />

      {/* Hero */}
      <section className="relative overflow-hidden bg-white border-b border-gray-100">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-20 sm:py-28">
          <div className="mx-auto max-w-2xl text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 mb-6">
              <Shield className="h-3.5 w-3.5" />
              Open-source · Apache 2.0
            </div>

            <h1 className="text-4xl font-black tracking-tight text-gray-900 sm:text-5xl leading-tight">
              Food safety data,{' '}
              <span className="text-emerald-600">open to everyone.</span>
            </h1>

            <p className="mt-5 text-lg text-gray-500 leading-relaxed">
              Restaurant inspection grades, FDA and USDA recall alerts, and anonymized outbreak
              advisories — aggregated, searchable, and free.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                href="/search"
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-emerald-700 transition-colors"
              >
                <Search className="h-4 w-4" />
                Search restaurants
              </Link>
              <Link
                href="/recalls"
                className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-3 text-sm font-semibold text-gray-700 hover:border-red-200 hover:text-red-700 transition-colors"
              >
                <AlertTriangle className="h-4 w-4" />
                Active recalls
              </Link>
            </div>
          </div>
        </div>

        {/* Background decoration */}
        <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-emerald-50 opacity-40 blur-3xl pointer-events-none" />
      </section>

      {/* Stats strip */}
      <section className="border-b border-gray-100 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-6">
          <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {stats.map(({ label, value }) => (
              <div key={label} className="text-center">
                <dt className="text-xs text-gray-400 uppercase tracking-wide">{label}</dt>
                <dd className="mt-0.5 text-lg font-bold text-gray-800">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* Feature cards */}
      <section className="mx-auto max-w-6xl px-4 sm:px-6 py-16 w-full">
        <div className="grid gap-6 sm:grid-cols-3">
          {features.map(({ icon: Icon, title, description, href, cta, color }) => (
            <Link
              key={title}
              href={href}
              className="group flex flex-col rounded-2xl border bg-white p-6 shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5"
            >
              <div className={`mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-${color}-50 text-${color}-600`}>
                <Icon className="h-5 w-5" />
              </div>
              <h2 className="font-semibold text-gray-900 group-hover:text-emerald-700 transition-colors">
                {title}
              </h2>
              <p className="mt-2 text-sm text-gray-500 leading-relaxed flex-1">{description}</p>
              <div className="mt-4 flex items-center gap-1 text-sm font-medium text-emerald-600">
                {cta} <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Open source CTA */}
      <section className="border-t border-gray-100 bg-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-16 text-center">
          <h2 className="text-2xl font-black text-gray-900">Built in the open.</h2>
          <p className="mt-3 text-gray-500 max-w-lg mx-auto text-sm leading-relaxed">
            [PROJECT_NAME] is community-driven and Apache 2.0 licensed. Health departments, developers,
            and domain experts are all welcome contributors.
          </p>
          <div className="mt-6 flex flex-col sm:flex-row justify-center gap-3">
            <a
              href="https://github.com/[org]/[PROJECT_NAME]"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:border-emerald-300 hover:text-emerald-700 transition-colors"
            >
              View on GitHub
            </a>
            <a
              href="https://github.com/[org]/[PROJECT_NAME]/blob/main/CONTRIBUTING.md"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-700 transition-colors"
            >
              Contribute <ChevronRight className="h-4 w-4" />
            </a>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
}
