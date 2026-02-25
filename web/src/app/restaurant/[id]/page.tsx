import { notFound } from 'next/navigation';
import Link from 'next/link';
import { MapPin, Calendar, ChevronLeft, Wifi, WifiOff, ExternalLink } from 'lucide-react';
import { PublicNav } from '@/components/public/nav';
import { PublicFooter } from '@/components/public/footer';
import { GradeBadge, GradeLabel } from '@/components/public/grade-badge';
import { InspectionTimeline } from '@/components/public/inspection-timeline';
import { getRestaurant, getRestaurantInspections } from '@/lib/public-api';

interface Props {
  params: { id: string };
}

export async function generateMetadata({ params }: Props) {
  try {
    const restaurant = await getRestaurant(params.id);
    return {
      title: `${restaurant.name} — [PROJECT_NAME]`,
      description: `Inspection grade and history for ${restaurant.name} in ${restaurant.city}, ${restaurant.state}.`,
    };
  } catch {
    return { title: 'Restaurant — [PROJECT_NAME]' };
  }
}

export default async function RestaurantPage({ params }: Props) {
  let restaurant;
  let inspections;

  try {
    [restaurant, inspections] = await Promise.all([
      getRestaurant(params.id),
      getRestaurantInspections(params.id, 20),
    ]);
  } catch {
    notFound();
  }

  const isActive = restaurant.status === 'ACTIVE';
  const latestInspection = inspections[0] ?? null;

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <PublicNav />

      <main className="mx-auto w-full max-w-4xl flex-1 px-4 sm:px-6 py-8">
        {/* Back */}
        <Link
          href="/search"
          className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-emerald-700 transition-colors mb-6"
        >
          <ChevronLeft className="h-4 w-4" /> Back to search
        </Link>

        {/* Header card */}
        <div className="rounded-2xl border bg-white shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <h1 className="text-2xl font-black text-gray-900 truncate">
                  {restaurant.name}
                </h1>
                {!isActive && (
                  <span className="rounded-full bg-red-50 px-2.5 py-0.5 text-xs font-semibold text-red-600">
                    {restaurant.status === 'CLOSED' ? 'Closed' : 'Suspended'}
                  </span>
                )}
              </div>

              {restaurant.cuisine_type && (
                <p className="text-sm text-gray-400 mb-2">{restaurant.cuisine_type}</p>
              )}

              <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1.5">
                  <MapPin className="h-4 w-4 shrink-0" />
                  {restaurant.address}, {restaurant.city}, {restaurant.state} {restaurant.zip_code}
                </span>
                {restaurant.last_inspection_date && (
                  <span className="flex items-center gap-1.5">
                    <Calendar className="h-4 w-4 shrink-0" />
                    Inspected {new Date(restaurant.last_inspection_date).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>

            {/* Current grade */}
            <div className="shrink-0 flex flex-col items-center gap-1">
              <GradeBadge grade={restaurant.current_grade} size="xl" />
              {restaurant.current_grade && (
                <span className="text-xs font-medium text-gray-500">
                  <GradeLabel grade={restaurant.current_grade} />
                </span>
              )}
              {restaurant.last_inspection_score !== null && (
                <span className="text-sm font-bold text-gray-700">
                  {restaurant.last_inspection_score} / 100
                </span>
              )}
            </div>
          </div>

          {/* Compliance score bar */}
          {restaurant.compliance_score > 0 && (
            <div className="mt-5">
              <div className="mb-1 flex justify-between text-xs text-gray-400">
                <span>Compliance score</span>
                <span className="font-medium text-gray-700">{Math.round(Number(restaurant.compliance_score))}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="h-full rounded-full bg-emerald-400 transition-all"
                  style={{ width: `${restaurant.compliance_score}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Stats row */}
        {latestInspection && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            {[
              {
                label: 'Latest grade',
                value: latestInspection.grade || '—',
              },
              {
                label: 'Latest score',
                value: latestInspection.score != null ? `${latestInspection.score}/100` : '—',
              },
              {
                label: 'Critical violations',
                value: latestInspection.critical_violations,
                danger: latestInspection.critical_violations > 0,
              },
              {
                label: 'Total violations',
                value: latestInspection.total_violations,
              },
            ].map(({ label, value, danger }) => (
              <div key={label} className="rounded-xl border bg-white p-4 shadow-sm text-center">
                <p className="text-xs text-gray-400 mb-0.5">{label}</p>
                <p className={`text-xl font-black ${danger ? 'text-red-600' : 'text-gray-900'}`}>
                  {String(value)}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Inspection history */}
        <div className="rounded-2xl border bg-white shadow-sm p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-5">
            Inspection History
            {inspections.length > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-400">
                {inspections.length} record{inspections.length !== 1 ? 's' : ''}
              </span>
            )}
          </h2>
          <InspectionTimeline inspections={inspections} />
        </div>

        {/* Data attribution */}
        <p className="mt-4 text-center text-xs text-gray-400">
          Inspection data sourced from public health department records.
          Accuracy depends on source data freshness.{' '}
          {restaurant.health_department_id && (
            <span>Health Dept ID: {restaurant.health_department_id}</span>
          )}
        </p>
      </main>

      <PublicFooter />
    </div>
  );
}
