import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ChevronLeft, AlertTriangle, Package, MapPin, Building2, Calendar } from 'lucide-react';
import { PublicNav } from '@/components/public/nav';
import { PublicFooter } from '@/components/public/footer';
import { getRecall } from '@/lib/public-api';
import { cn } from '@/lib/utils';

interface Props { params: { id: string } }

export async function generateMetadata({ params }: Props) {
  try {
    const recall = await getRecall(params.id);
    return {
      title: `${recall.title.slice(0, 60)} — HealthGuard`,
      description: `${recall.recalling_firm}: ${recall.reason.slice(0, 120)}`,
    };
  } catch {
    return { title: 'Recall — HealthGuard' };
  }
}

const classConfig: Record<string, { label: string; desc: string; bg: string; text: string; border: string }> = {
  I:  { label: 'Class I', desc: 'Serious adverse health consequences or death', bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
  II: { label: 'Class II', desc: 'May cause temporary adverse health consequences', bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
  III:{ label: 'Class III', desc: 'Unlikely to cause adverse health consequences', bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  '': { label: 'Unclassified', desc: '', bg: 'bg-gray-50', text: 'text-gray-500', border: 'border-gray-200' },
};

const sourceLabel: Record<string, string> = {
  fda: 'FDA', usda_fsis: 'USDA FSIS', cdc: 'CDC', manual: 'Manual',
};

export default async function RecallDetailPage({ params }: Props) {
  let recall;
  try { recall = await getRecall(params.id); }
  catch { notFound(); }

  const cls = classConfig[recall.classification] ?? classConfig[''];

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <PublicNav />

      <main className="mx-auto w-full max-w-4xl flex-1 px-4 sm:px-6 py-8">
        <Link href="/recalls" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-red-700 transition-colors mb-6">
          <ChevronLeft className="h-4 w-4" /> Back to recalls
        </Link>

        {/* Class banner */}
        {recall.classification && (
          <div className={cn('rounded-xl border p-4 mb-5 flex items-start gap-3', cls.bg, cls.border)}>
            <AlertTriangle className={cn('h-5 w-5 mt-0.5 shrink-0', cls.text)} />
            <div>
              <p className={cn('font-semibold text-sm', cls.text)}>{cls.label} Recall</p>
              {cls.desc && <p className={cn('text-xs mt-0.5', cls.text)}>{cls.desc}</p>}
            </div>
          </div>
        )}

        {/* Header */}
        <div className="rounded-2xl border bg-white shadow-sm p-6 mb-6">
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-semibold text-gray-600">
              {sourceLabel[recall.source] ?? recall.source}
            </span>
            {recall.hazard_type && (
              <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-700">
                {recall.hazard_type}
              </span>
            )}
            <span className={cn(
              'rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize',
              recall.status === 'active' ? 'bg-red-50 text-red-700' :
              recall.status === 'completed' ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-50 text-gray-600',
            )}>
              {recall.status}
            </span>
          </div>

          <h1 className="text-xl font-black text-gray-900 leading-snug mb-4">{recall.title}</h1>

          <div className="grid sm:grid-cols-2 gap-4 text-sm text-gray-600">
            <div className="flex items-start gap-2">
              <Building2 className="h-4 w-4 text-gray-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-xs text-gray-400 mb-0.5">Recalling firm</p>
                <p className="font-medium">{recall.recalling_firm}</p>
                {recall.firm_state && <p className="text-xs text-gray-400">{recall.firm_state}</p>}
              </div>
            </div>
            {recall.recall_initiation_date && (
              <div className="flex items-start gap-2">
                <Calendar className="h-4 w-4 text-gray-400 mt-0.5 shrink-0" />
                <div>
                  <p className="text-xs text-gray-400 mb-0.5">Recall initiated</p>
                  <p className="font-medium">{new Date(recall.recall_initiation_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                </div>
              </div>
            )}
            {recall.affected_states.length > 0 && (
              <div className="flex items-start gap-2 sm:col-span-2">
                <MapPin className="h-4 w-4 text-gray-400 mt-0.5 shrink-0" />
                <div>
                  <p className="text-xs text-gray-400 mb-1">Affected states</p>
                  <div className="flex flex-wrap gap-1">
                    {recall.affected_states.map((s) => (
                      <span key={s} className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">{s}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Reason */}
        <div className="rounded-2xl border bg-white shadow-sm p-6 mb-6">
          <h2 className="font-bold text-gray-900 mb-3">Reason for Recall</h2>
          <p className="text-sm text-gray-600 leading-relaxed">{recall.reason}</p>
        </div>

        {/* Products */}
        {recall.products && recall.products.length > 0 && (
          <div className="rounded-2xl border bg-white shadow-sm p-6 mb-6">
            <h2 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Package className="h-4 w-4 text-gray-400" />
              Affected Products ({recall.products.length})
            </h2>
            <div className="space-y-4">
              {recall.products.map((product) => (
                <div key={product.id} className="rounded-xl border border-gray-100 p-4">
                  <p className="font-medium text-sm text-gray-900">
                    {product.brand_name ? `${product.brand_name} — ` : ''}{product.product_description}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-3 text-xs text-gray-500">
                    {product.lot_numbers.length > 0 && (
                      <span><strong>Lot numbers:</strong> {product.lot_numbers.join(', ')}</span>
                    )}
                    {product.best_by_dates.length > 0 && (
                      <span><strong>Best by:</strong> {product.best_by_dates.join(', ')}</span>
                    )}
                    {product.upc_codes.length > 0 && (
                      <span><strong>UPC:</strong> {product.upc_codes.join(', ')}</span>
                    )}
                    {product.package_sizes.length > 0 && (
                      <span><strong>Sizes:</strong> {product.package_sizes.join(', ')}</span>
                    )}
                  </div>
                  {product.code_info && (
                    <p className="mt-2 text-xs text-gray-400 leading-relaxed">{product.code_info}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <p className="text-center text-xs text-gray-400 mt-4">
          External ID: {recall.external_id} · Source: {sourceLabel[recall.source] ?? recall.source}
        </p>
      </main>

      <PublicFooter />
    </div>
  );
}
