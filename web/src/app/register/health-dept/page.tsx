'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import {
  Building2, MapPin, Settings2, Mail,
  ChevronRight, ChevronLeft, CheckCircle2, Loader2, AlertCircle,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─── Types ───────────────────────────────────────────────────────────────────

interface FormData {
  name: string;
  fips_code: string;
  state: string;
  jurisdiction_type: string;
  website: string;
  contact_email: string;
  score_system: string;
  schema_map_raw: string; // JSON text edited by user
  webhook_url: string;
}

type FieldErrors = Partial<Record<keyof FormData | '_form', string>>;

// ─── Constants ────────────────────────────────────────────────────────────────

const US_STATES = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
  'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
  'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
  'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
  'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC',
];

const JURISDICTION_TYPES = [
  { value: 'COUNTY', label: 'County' },
  { value: 'CITY',   label: 'City / Municipality' },
  { value: 'STATE',  label: 'State Agency' },
  { value: 'TRIBAL', label: 'Tribal Nation' },
];

const SCORE_SYSTEMS = [
  { value: 'SCORE_0_100',    label: 'Numeric 0–100',            example: '"score": 88' },
  { value: 'GRADE_A_F',      label: 'Letter grade A–F',         example: '"grade": "A"' },
  { value: 'PASS_FAIL',      label: 'Pass / Fail',              example: '"score": "pass"' },
  { value: 'LETTER_NUMERIC', label: 'Letter + Numeric (hybrid)', example: '"score": "85" or "B"' },
];

const STEP_LABELS = ['Jurisdiction', 'Data Format', 'Contact & Review'];

const INPUT = `
  w-full px-4 py-2.5 rounded-xl border border-gray-200 bg-white text-gray-900
  placeholder-gray-400 text-sm focus:outline-none focus:ring-2
  focus:ring-emerald-500/30 focus:border-emerald-500 transition-all
`.replace(/\s+/g, ' ').trim();

const LABEL = 'block text-xs font-semibold text-gray-600 mb-1';

// ─── Field error helper ───────────────────────────────────────────────────────

function FieldError({ msg }: { msg?: string }) {
  if (!msg) return null;
  return (
    <p className="mt-1 text-xs text-red-500 flex items-center gap-1">
      <AlertCircle size={12} />{msg}
    </p>
  );
}

// ─── Step 1: Jurisdiction info ────────────────────────────────────────────────

function StepJurisdiction({
  data, errors, onChange,
}: { data: FormData; errors: FieldErrors; onChange: (k: keyof FormData, v: string) => void }) {
  return (
    <div className="space-y-4">
      <div>
        <label className={LABEL}>Department / agency name *</label>
        <input
          className={INPUT}
          placeholder="Maricopa County Health Department"
          value={data.name}
          onChange={e => onChange('name', e.target.value)}
        />
        <FieldError msg={errors.name} />
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-2">
          <label className={LABEL}>FIPS code *</label>
          <input
            className={INPUT}
            placeholder="04013"
            value={data.fips_code}
            maxLength={5}
            onChange={e => onChange('fips_code', e.target.value.replace(/\D/g, ''))}
          />
          <p className="mt-1 text-xs text-gray-400">5-digit county FIPS (e.g. 04013 for Maricopa, AZ)</p>
          <FieldError msg={errors.fips_code} />
        </div>
        <div>
          <label className={LABEL}>State *</label>
          <select
            className={INPUT}
            value={data.state}
            onChange={e => onChange('state', e.target.value)}
          >
            <option value="">—</option>
            {US_STATES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <FieldError msg={errors.state} />
        </div>
      </div>

      <div>
        <label className={LABEL}>Jurisdiction type *</label>
        <div className="grid grid-cols-2 gap-2">
          {JURISDICTION_TYPES.map(({ value, label }) => (
            <label
              key={value}
              className={`flex items-center gap-2 p-3 rounded-xl border cursor-pointer text-sm transition-colors ${
                data.jurisdiction_type === value
                  ? 'border-emerald-500 bg-emerald-50 text-emerald-800'
                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
              }`}
            >
              <input
                type="radio"
                name="jurisdiction_type"
                value={value}
                checked={data.jurisdiction_type === value}
                onChange={e => onChange('jurisdiction_type', e.target.value)}
                className="accent-emerald-600"
              />
              {label}
            </label>
          ))}
        </div>
        <FieldError msg={errors.jurisdiction_type} />
      </div>

      <div>
        <label className={LABEL}>Official website</label>
        <input
          className={INPUT}
          type="url"
          placeholder="https://health.maricopa.gov"
          value={data.website}
          onChange={e => onChange('website', e.target.value)}
        />
      </div>
    </div>
  );
}

// ─── Step 2: Data format ──────────────────────────────────────────────────────

function StepDataFormat({
  data, errors, onChange,
}: { data: FormData; errors: FieldErrors; onChange: (k: keyof FormData, v: string) => void }) {
  return (
    <div className="space-y-5">
      <div>
        <label className={LABEL}>Score / grade system *</label>
        <p className="text-xs text-gray-400 mb-2">
          How does your department record inspection outcomes?
        </p>
        <div className="space-y-2">
          {SCORE_SYSTEMS.map(({ value, label, example }) => (
            <label
              key={value}
              className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-colors ${
                data.score_system === value
                  ? 'border-emerald-500 bg-emerald-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="radio"
                name="score_system"
                value={value}
                checked={data.score_system === value}
                onChange={e => onChange('score_system', e.target.value)}
                className="mt-0.5 accent-emerald-600"
              />
              <div>
                <span className="text-sm font-medium text-gray-900">{label}</span>
                <span className="ml-2 text-xs text-gray-400 font-mono">{example}</span>
              </div>
            </label>
          ))}
        </div>
        <FieldError msg={errors.score_system} />
      </div>

      <div>
        <label className={LABEL}>Field name mapping (optional)</label>
        <p className="text-xs text-gray-400 mb-1">
          If your export uses different field names, map them here. JSON object —
          left side is your name, right side is the platform's canonical name.
        </p>
        <textarea
          className={`${INPUT} resize-none h-28 font-mono text-xs`}
          placeholder={'{\n  "facility_name": "restaurant_name",\n  "inspection_date": "inspected_at"\n}'}
          value={data.schema_map_raw}
          onChange={e => onChange('schema_map_raw', e.target.value)}
        />
        <FieldError msg={errors.schema_map_raw} />
        <p className="mt-1 text-xs text-gray-400">
          Leave blank if your field names already match the{' '}
          <Link href="/api/docs/" target="_blank" className="text-emerald-600 hover:underline">
            API schema
          </Link>.
        </p>
      </div>

      <div>
        <label className={LABEL}>Webhook callback URL (optional)</label>
        <input
          className={INPUT}
          type="url"
          placeholder="https://your-system.gov/webhooks/foodsafety"
          value={data.webhook_url}
          onChange={e => onChange('webhook_url', e.target.value)}
        />
        <p className="mt-1 text-xs text-gray-400">
          We'll POST a signed JSON summary to this URL after each batch completes.
        </p>
      </div>
    </div>
  );
}

// ─── Step 3: Contact & Review ─────────────────────────────────────────────────

function StepContactReview({
  data, errors, onChange,
}: { data: FormData; errors: FieldErrors; onChange: (k: keyof FormData, v: string) => void }) {
  const ssys = SCORE_SYSTEMS.find(s => s.value === data.score_system)?.label ?? data.score_system;
  const Row = ({ label, value }: { label: string; value: string }) =>
    value ? (
      <div className="flex gap-3 py-2 border-b border-gray-100 last:border-0">
        <span className="w-40 shrink-0 text-xs text-gray-500">{label}</span>
        <span className="text-sm text-gray-900 break-all">{value}</span>
      </div>
    ) : null;

  return (
    <div className="space-y-5">
      <div>
        <label className={LABEL}>Contact email *</label>
        <div className="relative">
          <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            className={`${INPUT} pl-9`}
            type="email"
            placeholder="jsmith@cookcountyil.gov"
            value={data.contact_email}
            onChange={e => onChange('contact_email', e.target.value)}
          />
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Your API key will be sent here once approved. Use an official government address.
        </p>
        <FieldError msg={errors.contact_email} />
      </div>

      <div>
        <p className="text-xs font-semibold text-gray-600 mb-2">Review your submission</p>
        <div className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-1">
          <Row label="Department" value={data.name} />
          <Row label="FIPS code" value={data.fips_code} />
          <Row label="State" value={data.state} />
          <Row label="Type" value={JURISDICTION_TYPES.find(j => j.value === data.jurisdiction_type)?.label ?? data.jurisdiction_type} />
          <Row label="Score system" value={ssys} />
          <Row label="Contact email" value={data.contact_email} />
          {data.webhook_url && <Row label="Webhook" value={data.webhook_url} />}
        </div>
      </div>

      <p className="text-xs text-gray-400">
        By submitting you agree to our{' '}
        <Link href="/terms" className="text-emerald-600 hover:underline">Terms of Service</Link>
        {' '}and{' '}
        <Link href="/privacy" className="text-emerald-600 hover:underline">Privacy Policy</Link>.
      </p>
    </div>
  );
}

// ─── Main wizard ──────────────────────────────────────────────────────────────

export default function HealthDeptRegisterPage() {
  const [step, setStep] = useState(0);
  const [data, setData] = useState<FormData>({
    name: '',
    fips_code: '',
    state: '',
    jurisdiction_type: 'COUNTY',
    website: '',
    contact_email: '',
    score_system: 'SCORE_0_100',
    schema_map_raw: '',
    webhook_url: '',
  });
  const [errors, setErrors] = useState<FieldErrors>({});
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState<{ id: number; fips_code: string } | null>(null);

  function onChange(key: keyof FormData, value: string) {
    setData(d => ({ ...d, [key]: value }));
    setErrors(e => ({ ...e, [key]: undefined }));
  }

  function validateStep(s: number): FieldErrors {
    const errs: FieldErrors = {};
    if (s === 0) {
      if (!data.name.trim())            errs.name = 'Required.';
      if (!/^\d{2,5}$/.test(data.fips_code)) errs.fips_code = 'Must be 2–5 digits.';
      if (!data.state)                  errs.state = 'Required.';
      if (!data.jurisdiction_type)      errs.jurisdiction_type = 'Required.';
    }
    if (s === 1) {
      if (data.schema_map_raw.trim()) {
        try { JSON.parse(data.schema_map_raw); }
        catch { errs.schema_map_raw = 'Invalid JSON.'; }
      }
    }
    if (s === 2) {
      if (!data.contact_email.trim())   errs.contact_email = 'Required.';
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.contact_email))
                                         errs.contact_email = 'Must be a valid email.';
    }
    return errs;
  }

  function handleNext() {
    const errs = validateStep(step);
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }
    setErrors({});
    setStep(s => s + 1);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const errs = validateStep(2);
    if (Object.keys(errs).length > 0) { setErrors(errs); return; }

    setLoading(true);
    setErrors({});

    let schema_map: Record<string, string> = {};
    if (data.schema_map_raw.trim()) {
      try { schema_map = JSON.parse(data.schema_map_raw); }
      catch { setErrors({ schema_map_raw: 'Invalid JSON.' }); setLoading(false); return; }
    }

    try {
      const res = await fetch(`${API_URL}/api/v1/submissions/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name:              data.name,
          fips_code:         data.fips_code,
          state:             data.state,
          contact_email:     data.contact_email,
          jurisdiction_type: data.jurisdiction_type,
          website:           data.website || undefined,
          score_system:      data.score_system,
          schema_map,
          webhook_url:       data.webhook_url || undefined,
        }),
      });

      const json = await res.json();

      if (!res.ok) {
        const serverErrors = json as FieldErrors;
        setErrors(serverErrors);
        // jump to the step containing the first error
        if (serverErrors.name || serverErrors.fips_code || serverErrors.state || serverErrors.jurisdiction_type)
          setStep(0);
        else if (serverErrors.score_system || serverErrors.schema_map_raw || serverErrors.webhook_url)
          setStep(1);
      } else {
        setSubmitted({ id: json.id, fips_code: json.fips_code });
      }
    } catch {
      setErrors({ _form: 'Network error — please check your connection and try again.' });
    } finally {
      setLoading(false);
    }
  }

  // ── Success screen ──────────────────────────────────────────────────────────
  if (submitted) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-gray-200 p-10 text-center">
          <CheckCircle2 size={48} className="mx-auto text-emerald-500 mb-4" />
          <h1 className="text-xl font-bold text-gray-900 mb-2">Registration submitted</h1>
          <p className="text-sm text-gray-500 mb-2">
            Request <span className="font-mono text-xs bg-gray-100 px-1 rounded">#{submitted.id}</span> is
            pending TSC review. Once approved, an API key will be sent to{' '}
            <strong>{data.contact_email}</strong>.
          </p>
          <p className="text-xs text-gray-400 mb-6">
            In the meantime, review the{' '}
            <Link href="/api/docs/" className="text-emerald-600 hover:underline">
              API documentation
            </Link>
            {' '}and prepare your inspection export pipeline.
          </p>
          <Link
            href="/"
            className="inline-block px-6 py-2.5 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors"
          >
            Back to home
          </Link>
        </div>
      </main>
    );
  }

  // ── Wizard ──────────────────────────────────────────────────────────────────
  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="max-w-lg w-full">

        {/* Header */}
        <div className="mb-6 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-emerald-100 mb-4">
            <Building2 size={24} className="text-emerald-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Submit Inspection Data</h1>
          <p className="mt-1 text-sm text-gray-500">
            Register your jurisdiction to push inspection records directly to the platform
          </p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-6">
          {STEP_LABELS.map((label, i) => (
            <div key={label} className="flex items-center gap-2">
              <div className={`
                flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold transition-colors
                ${i === step ? 'bg-emerald-600 text-white' : i < step ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-400'}
              `}>
                {i < step ? '✓' : i + 1}
              </div>
              <span className={`text-xs font-medium hidden sm:block ${i === step ? 'text-gray-900' : 'text-gray-400'}`}>
                {label}
              </span>
              {i < STEP_LABELS.length - 1 && (
                <div className="w-6 h-px bg-gray-200 mx-1" />
              )}
            </div>
          ))}
        </div>

        {/* Card */}
        <form
          onSubmit={step === 2 ? handleSubmit : e => { e.preventDefault(); handleNext(); }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
        >
          {errors._form && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 flex items-start gap-2">
              <AlertCircle size={14} className="text-red-500 mt-0.5 shrink-0" />
              <p className="text-xs text-red-600">{errors._form}</p>
            </div>
          )}

          {step === 0 && <StepJurisdiction data={data} errors={errors} onChange={onChange} />}
          {step === 1 && <StepDataFormat   data={data} errors={errors} onChange={onChange} />}
          {step === 2 && <StepContactReview data={data} errors={errors} onChange={onChange} />}

          {/* Navigation */}
          <div className="mt-6 flex items-center justify-between">
            {step > 0 ? (
              <button
                type="button"
                onClick={() => setStep(s => s - 1)}
                className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                <ChevronLeft size={16} /> Back
              </button>
            ) : (
              <Link href="/" className="text-sm text-gray-400 hover:text-gray-600 transition-colors">
                Cancel
              </Link>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            >
              {loading && <Loader2 size={14} className="animate-spin" />}
              {step < 2 ? (
                <>Next <ChevronRight size={16} /></>
              ) : loading ? 'Submitting…' : 'Submit registration'}
            </button>
          </div>
        </form>

        <p className="mt-4 text-center text-xs text-gray-400">
          Already have an API key?{' '}
          <Link href="/api/docs/" className="text-emerald-600 hover:underline">
            View the submission API docs
          </Link>
        </p>
      </div>
    </main>
  );
}
