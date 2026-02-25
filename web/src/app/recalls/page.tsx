import { Suspense } from 'react';
import Link from 'next/link';
import { AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react';
import { PublicNav } from '@/components/public/nav';
import { PublicFooter } from '@/components/public/footer';
import { SearchInput, FilterSelect } from '@/components/public/search-input';
import { RecallCard, RecallCardSkeleton } from '@/components/public/recall-card';
import { getRecalls } from '@/lib/public-api';

export const metadata = {
  title: 'Food Recalls — HealthGuard',
  description: 'Active FDA and USDA food safety recalls. Filter by hazard, state, or product.',
};

const PAGE_SIZE = 20;

const US_STATES = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN',
  'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV',
  'NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
  'TX','UT','VT','VA','WA','WV','WI','WY','DC',
];

interface SearchParams {
  search?: string;
  hazard?: string;
  state?: string;
  source?: string;
  status?: string;
  offset?: string;
}

async function RecallResults({ searchParams }: { searchParams: SearchParams }) {
  const offset = parseInt(searchParams.offset ?? '0', 10);

  let data;
  try {
    data = await getRecalls({
      search: searchParams.search,
      hazard: searchParams.hazard,
      state: searchParams.state,
      source: searchParams.source,
      status: searchParams.status ?? 'active',
      page_size: PAGE_SIZE,
      offset,
    });
  } catch {
    return (
      <p className="col-span-full py-12 text-center text-sm text-gray-400">
        Could not load recalls. Make sure the API is running.
      </p>
    );
  }

  if (data.results.length === 0) {
    return (
      <div className="col-span-full py-16 text-center">
        <p className="text-gray-500 font-medium">No recalls found for these filters.</p>
        <p className="text-sm text-gray-400 mt-1">Try removing some filters or selecting "All" status.</p>
      </div>
    );
  }

  const buildHref = (o: number) => {
    const params = new URLSearchParams();
    if (searchParams.search) params.set('search', searchParams.search);
    if (searchParams.hazard) params.set('hazard', searchParams.hazard);
    if (searchParams.state) params.set('state', searchParams.state);
    if (searchParams.source) params.set('source', searchParams.source);
    if (searchParams.status) params.set('status', searchParams.status);
    if (o > 0) params.set('offset', String(o));
    const s = params.toString();
    return `/recalls${s ? `?${s}` : ''}`;
  };

  const hasPrev = offset > 0;
  const hasNext = offset + PAGE_SIZE < data.total;

  return (
    <>
      {data.results.map((r) => (
        <RecallCard key={r.id} recall={r} />
      ))}

      {/* Pagination */}
      <div className="col-span-full flex items-center justify-between border-t border-gray-100 pt-4 mt-2">
        <p className="text-xs text-gray-400">
          {offset + 1}–{Math.min(offset + PAGE_SIZE, data.total)} of {data.total}
        </p>
        <div className="flex gap-2">
          {hasPrev ? (
            <Link href={buildHref(offset - PAGE_SIZE)} className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-600 hover:border-red-200 hover:text-red-700 transition-colors">
              <ChevronLeft className="h-4 w-4" /> Prev
            </Link>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-300 cursor-not-allowed">
              <ChevronLeft className="h-4 w-4" /> Prev
            </span>
          )}
          {hasNext ? (
            <Link href={buildHref(offset + PAGE_SIZE)} className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-600 hover:border-red-200 hover:text-red-700 transition-colors">
              Next <ChevronRight className="h-4 w-4" />
            </Link>
          ) : (
            <span className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-300 cursor-not-allowed">
              Next <ChevronRight className="h-4 w-4" />
            </span>
          )}
        </div>
      </div>
    </>
  );
}

export default function RecallsPage({ searchParams }: { searchParams: SearchParams }) {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <PublicNav />

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 sm:px-6 py-8">
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <h1 className="text-2xl font-black text-gray-900">Food Recalls</h1>
          </div>
          <p className="text-sm text-gray-500">
            Synced from FDA and USDA FSIS. Updated nightly.{' '}
            <a
              href="https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts"
              target="_blank"
              rel="noopener noreferrer"
              className="text-red-600 hover:underline"
            >
              Official FDA source ↗
            </a>
          </p>
        </div>

        {/* Class I warning */}
        <div className="mb-6 rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-700">
          <strong>Class I recalls</strong> are the most serious — they involve products that
          could cause serious adverse health consequences or death. Discard or return these
          products immediately.
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          <Suspense>
            <SearchInput
              placeholder="Search recalls, brands, firms…"
              param="search"
              className="flex-1"
            />
            <FilterSelect
              param="source"
              placeholder="All sources"
              options={[
                { value: 'fda', label: 'FDA' },
                { value: 'usda_fsis', label: 'USDA FSIS' },
              ]}
              className="sm:w-36"
            />
            <FilterSelect
              param="state"
              placeholder="All states"
              options={US_STATES.map((s) => ({ value: s, label: s }))}
              className="sm:w-32"
            />
            <FilterSelect
              param="status"
              placeholder="Active"
              options={[
                { value: 'active', label: 'Active' },
                { value: 'ongoing', label: 'Ongoing' },
                { value: 'completed', label: 'Completed' },
                { value: 'all', label: 'All statuses' },
              ]}
              className="sm:w-36"
            />
          </Suspense>
        </div>

        {/* Results */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Suspense
            fallback={Array.from({ length: 6 }).map((_, i) => (
              <RecallCardSkeleton key={i} />
            ))}
          >
            <RecallResults searchParams={searchParams} />
          </Suspense>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}
