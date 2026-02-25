import { Suspense } from 'react';
import { PublicNav } from '@/components/public/nav';
import { PublicFooter } from '@/components/public/footer';
import { SearchInput, FilterSelect } from '@/components/public/search-input';
import { RestaurantCard, RestaurantCardSkeleton } from '@/components/public/restaurant-card';
import { searchRestaurants } from '@/lib/public-api';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import Link from 'next/link';

export const metadata = {
  title: 'Find Restaurants — [PROJECT_NAME]',
  description: 'Search restaurant inspection grades and violation history.',
};

const US_STATES = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN',
  'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV',
  'NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
  'TX','UT','VT','VA','WA','WV','WI','WY','DC',
];

const PAGE_SIZE = 20;

interface SearchParams {
  q?: string;
  state?: string;
  grade?: string;
  offset?: string;
}

async function RestaurantResults({ searchParams }: { searchParams: SearchParams }) {
  const offset = parseInt(searchParams.offset ?? '0', 10);

  let data;
  try {
    data = await searchRestaurants({
      q: searchParams.q,
      state: searchParams.state,
      grade: searchParams.grade,
      page_size: PAGE_SIZE,
      offset,
    });
  } catch {
    return (
      <p className="col-span-full text-center text-sm text-gray-400 py-12">
        Could not load results. Make sure the API is running.
      </p>
    );
  }

  if (data.results.length === 0) {
    return (
      <div className="col-span-full py-16 text-center">
        <p className="text-gray-500 font-medium">No restaurants found.</p>
        <p className="text-sm text-gray-400 mt-1">Try broadening your search.</p>
      </div>
    );
  }

  return (
    <>
      {data.results.map((r) => (
        <RestaurantCard key={r.id} restaurant={r} />
      ))}
      {/* Pagination */}
      <PaginationRow total={data.total} offset={offset} searchParams={searchParams} />
    </>
  );
}

function PaginationRow({
  total,
  offset,
  searchParams,
}: {
  total: number;
  offset: number;
  searchParams: SearchParams;
}) {
  const prevOffset = Math.max(0, offset - PAGE_SIZE);
  const nextOffset = offset + PAGE_SIZE;
  const hasPrev = offset > 0;
  const hasNext = nextOffset < total;

  const buildHref = (o: number) => {
    const params = new URLSearchParams();
    if (searchParams.q) params.set('q', searchParams.q);
    if (searchParams.state) params.set('state', searchParams.state);
    if (searchParams.grade) params.set('grade', searchParams.grade);
    if (o > 0) params.set('offset', String(o));
    const s = params.toString();
    return `/search${s ? `?${s}` : ''}`;
  };

  return (
    <div className="col-span-full flex items-center justify-between border-t border-gray-100 pt-4 mt-2">
      <p className="text-xs text-gray-400">
        {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
      </p>
      <div className="flex gap-2">
        {hasPrev ? (
          <Link
            href={buildHref(prevOffset)}
            className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-600 hover:border-emerald-300 hover:text-emerald-700 transition-colors"
          >
            <ChevronLeft className="h-4 w-4" /> Prev
          </Link>
        ) : (
          <span className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-300 cursor-not-allowed">
            <ChevronLeft className="h-4 w-4" /> Prev
          </span>
        )}
        {hasNext ? (
          <Link
            href={buildHref(nextOffset)}
            className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-600 hover:border-emerald-300 hover:text-emerald-700 transition-colors"
          >
            Next <ChevronRight className="h-4 w-4" />
          </Link>
        ) : (
          <span className="inline-flex items-center gap-1 rounded-lg border px-3 py-1.5 text-sm font-medium text-gray-300 cursor-not-allowed">
            Next <ChevronRight className="h-4 w-4" />
          </span>
        )}
      </div>
    </div>
  );
}

export default function SearchPage({ searchParams }: { searchParams: SearchParams }) {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <PublicNav />

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 sm:px-6 py-8">
        <h1 className="text-2xl font-black text-gray-900 mb-6">Find Restaurants</h1>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          <Suspense>
            <SearchInput
              placeholder="Restaurant name, city, or ZIP…"
              className="flex-1"
            />
            <FilterSelect
              param="state"
              placeholder="All states"
              options={US_STATES.map((s) => ({ value: s, label: s }))}
              className="sm:w-32"
            />
            <FilterSelect
              param="grade"
              placeholder="Any grade"
              options={[
                { value: 'A', label: 'Grade A' },
                { value: 'B', label: 'Grade B' },
                { value: 'C', label: 'Grade C' },
                { value: 'P', label: 'Pending' },
                { value: 'X', label: 'Closed' },
              ]}
              className="sm:w-36"
            />
          </Suspense>
        </div>

        {/* Grade legend */}
        <div className="mb-6 flex flex-wrap gap-3 text-xs text-gray-500">
          {[
            { grade: 'A', label: 'Excellent (90–100)', color: 'bg-emerald-400' },
            { grade: 'B', label: 'Good (80–89)', color: 'bg-yellow-400' },
            { grade: 'C', label: 'Needs improvement (70–79)', color: 'bg-orange-400' },
            { grade: 'X', label: 'Closed', color: 'bg-red-400' },
          ].map(({ grade, label, color }) => (
            <span key={grade} className="flex items-center gap-1.5">
              <span className={`inline-block h-2.5 w-2.5 rounded-full ${color}`} />
              <strong className="font-semibold">{grade}</strong> — {label}
            </span>
          ))}
        </div>

        {/* Results */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Suspense
            fallback={Array.from({ length: 6 }).map((_, i) => (
              <RestaurantCardSkeleton key={i} />
            ))}
          >
            <RestaurantResults searchParams={searchParams} />
          </Suspense>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
}
