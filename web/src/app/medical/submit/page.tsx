"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { submitCase, type CaseSubmission } from "@/lib/medical-api";

const SYMPTOM_OPTIONS = [
  "diarrhea", "vomiting", "nausea", "abdominal cramps", "fever",
  "bloody stool", "headache", "fatigue", "muscle aches", "chills",
  "jaundice", "dehydration",
];

const EXPOSURE_TYPES = [
  { value: "restaurant", label: "Restaurant / Food service" },
  { value: "grocery",    label: "Grocery / Retail food" },
  { value: "home",       label: "Home-prepared food" },
  { value: "catered",    label: "Catered event" },
  { value: "water",      label: "Water source" },
  { value: "animal",     label: "Animal contact" },
  { value: "person",     label: "Person-to-person" },
  { value: "unknown",    label: "Unknown" },
];

interface ExposureForm {
  exposure_type: string;
  exposure_date: string;
  establishment_type: string;
  food_items: string;   // comma-separated raw input
  notes: string;
}

function ConsentBanner() {
  return (
    <div className="bg-teal-900/20 border border-teal-700/30 rounded-xl p-4">
      <div className="flex gap-3">
        <svg className="w-5 h-5 text-teal-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
        </svg>
        <div>
          <p className="text-sm font-medium text-teal-300">Anonymization guarantee</p>
          <p className="text-xs text-teal-400/80 mt-0.5 leading-relaxed">
            The Patient ID field is hashed before transmission. Age is stored as a range band
            (e.g. "30–39"). Location is truncated to a 5-character geohash (~5 km) and ZIP
            prefix only. No name, date of birth, address, or contact information is ever stored.
          </p>
        </div>
      </div>
    </div>
  );
}

export default function SubmitCasePage() {
  const router = useRouter();

  const [form, setForm] = useState({
    patient_id: "",
    age: "",
    sex: "" as "" | "M" | "F" | "O",
    lat: "",
    lon: "",
    zip_code: "",
    onset_date: "",
    symptoms: [] as string[],
    pathogen: "",
    illness_status: "suspected" as CaseSubmission["illness_status"],
    outcome: "unknown",
    hospitalized: false,
    notes: "",
  });

  const [exposures, setExposures] = useState<ExposureForm[]>([]);
  const [showAddExposure, setShowAddExposure] = useState(false);
  const [newExp, setNewExp] = useState<ExposureForm>({
    exposure_type: "restaurant",
    exposure_date: "",
    establishment_type: "",
    food_items: "",
    notes: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  function toggleSymptom(s: string) {
    setForm(f => ({
      ...f,
      symptoms: f.symptoms.includes(s)
        ? f.symptoms.filter(x => x !== s)
        : [...f.symptoms, s],
    }));
  }

  function addExposure() {
    setExposures(e => [...e, newExp]);
    setNewExp({
      exposure_type: "restaurant",
      exposure_date: "",
      establishment_type: "",
      food_items: "",
      notes: "",
    });
    setShowAddExposure(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!form.patient_id.trim()) {
      setError("Patient ID is required for anonymization.");
      return;
    }
    if (form.symptoms.length === 0) {
      setError("Please select at least one symptom.");
      return;
    }

    setSubmitting(true);
    try {
      const payload: CaseSubmission = {
        patient_id:     form.patient_id.trim(),
        age:            parseInt(form.age, 10),
        sex:            form.sex || undefined,
        lat:            parseFloat(form.lat),
        lon:            parseFloat(form.lon),
        zip_code:       form.zip_code.trim(),
        onset_date:     form.onset_date,
        symptoms:       form.symptoms,
        pathogen:       form.pathogen.trim() || undefined,
        illness_status: form.illness_status,
        outcome:        form.outcome,
        hospitalized:   form.hospitalized,
        notes:          form.notes.trim() || undefined,
        exposures: exposures.map(exp => ({
          exposure_type:      exp.exposure_type,
          exposure_date:      exp.exposure_date || undefined,
          establishment_type: exp.establishment_type.trim() || undefined,
          food_items:         exp.food_items
            ? exp.food_items.split(",").map(s => s.trim()).filter(Boolean)
            : [],
          notes:              exp.notes.trim() || undefined,
        })),
      };

      await submitCase(payload);
      setSuccess(true);
      setTimeout(() => router.push("/medical"), 2000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Submission failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <div className="max-w-lg mx-auto mt-20 text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-teal-500/10 border border-teal-500/20 flex items-center justify-center mx-auto">
          <svg className="w-8 h-8 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-white">Case Submitted</h2>
        <p className="text-slate-400 text-sm">
          The anonymized case has been recorded. Redirecting to dashboard…
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white">Submit Clinical Case</h1>
        <p className="text-sm text-slate-400 mt-0.5">
          All patient data is anonymized before storage.
        </p>
      </div>

      <ConsentBanner />

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Core patient info */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-white">Patient (anonymized at submission)</h2>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                Patient / Chart ID <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                value={form.patient_id}
                onChange={e => setForm(f => ({ ...f, patient_id: e.target.value }))}
                placeholder="e.g. MRN-00123 or chart #"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
                required
              />
              <p className="text-xs text-slate-600 mt-1">Never stored — hashed client-side.</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                Age <span className="text-red-400">*</span>
              </label>
              <input
                type="number"
                min={0}
                max={120}
                value={form.age}
                onChange={e => setForm(f => ({ ...f, age: e.target.value }))}
                placeholder="e.g. 34"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
                required
              />
              <p className="text-xs text-slate-600 mt-1">Stored as age band (30–39).</p>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Sex</label>
              <select
                value={form.sex}
                onChange={e => setForm(f => ({ ...f, sex: e.target.value as typeof form.sex }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-teal-500"
              >
                <option value="">Not specified</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="O">Other / Unknown</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                Illness Status <span className="text-red-400">*</span>
              </label>
              <select
                value={form.illness_status}
                onChange={e => setForm(f => ({ ...f, illness_status: e.target.value as CaseSubmission["illness_status"] }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-teal-500"
              >
                <option value="suspected">Suspected</option>
                <option value="confirmed">Confirmed</option>
                <option value="ruled_out">Ruled out</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="hospitalized"
              checked={form.hospitalized}
              onChange={e => setForm(f => ({ ...f, hospitalized: e.target.checked }))}
              className="rounded border-slate-600 bg-slate-800 text-teal-500"
            />
            <label htmlFor="hospitalized" className="text-sm text-slate-300">Patient was hospitalized</label>
          </div>
        </div>

        {/* Location */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-white">Location (coarsened on save)</h2>
          <div className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                Latitude <span className="text-red-400">*</span>
              </label>
              <input
                type="number"
                step="any"
                value={form.lat}
                onChange={e => setForm(f => ({ ...f, lat: e.target.value }))}
                placeholder="37.7749"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                Longitude <span className="text-red-400">*</span>
              </label>
              <input
                type="number"
                step="any"
                value={form.lon}
                onChange={e => setForm(f => ({ ...f, lon: e.target.value }))}
                placeholder="-122.4194"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                ZIP Code <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                maxLength={10}
                value={form.zip_code}
                onChange={e => setForm(f => ({ ...f, zip_code: e.target.value }))}
                placeholder="94103"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
                required
              />
            </div>
          </div>
        </div>

        {/* Illness details */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-white">Illness Details</h2>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">
                Onset Date <span className="text-red-400">*</span>
              </label>
              <input
                type="date"
                value={form.onset_date}
                onChange={e => setForm(f => ({ ...f, onset_date: e.target.value }))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-teal-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Suspected Pathogen</label>
              <input
                type="text"
                value={form.pathogen}
                onChange={e => setForm(f => ({ ...f, pathogen: e.target.value }))}
                placeholder="e.g. Salmonella, Norovirus"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-2">
              Symptoms <span className="text-red-400">*</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {SYMPTOM_OPTIONS.map(s => (
                <button
                  key={s}
                  type="button"
                  onClick={() => toggleSymptom(s)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    form.symptoms.includes(s)
                      ? "bg-teal-500/20 border-teal-500/40 text-teal-300"
                      : "bg-slate-800 border-slate-700 text-slate-400 hover:text-white hover:border-slate-600"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Notes</label>
            <textarea
              rows={2}
              value={form.notes}
              onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              placeholder="Additional clinical notes (no patient identifiers)"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500 resize-none"
            />
          </div>
        </div>

        {/* Exposures */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Reported Exposures</h2>
            <button
              type="button"
              onClick={() => setShowAddExposure(v => !v)}
              className="text-xs text-teal-400 hover:underline"
            >
              + Add exposure
            </button>
          </div>

          {exposures.length > 0 && (
            <ul className="space-y-2">
              {exposures.map((exp, i) => (
                <li key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
                  <div>
                    <p className="text-sm text-white capitalize">{exp.exposure_type.replace("_", " ")}</p>
                    {exp.exposure_date && <p className="text-xs text-slate-500">{exp.exposure_date}</p>}
                  </div>
                  <button
                    type="button"
                    onClick={() => setExposures(e => e.filter((_, j) => j !== i))}
                    className="text-slate-600 hover:text-red-400 text-xs"
                  >
                    remove
                  </button>
                </li>
              ))}
            </ul>
          )}

          {showAddExposure && (
            <div className="border border-slate-700 rounded-xl p-4 space-y-3 bg-slate-800/30">
              <div className="grid sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Type</label>
                  <select
                    value={newExp.exposure_type}
                    onChange={e => setNewExp(n => ({ ...n, exposure_type: e.target.value }))}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-teal-500"
                  >
                    {EXPOSURE_TYPES.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Date</label>
                  <input
                    type="date"
                    value={newExp.exposure_date}
                    onChange={e => setNewExp(n => ({ ...n, exposure_date: e.target.value }))}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-teal-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Food items (comma-separated)</label>
                <input
                  type="text"
                  value={newExp.food_items}
                  onChange={e => setNewExp(n => ({ ...n, food_items: e.target.value }))}
                  placeholder="chicken, lettuce, eggs"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={addExposure}
                  className="px-4 py-1.5 bg-teal-500/20 border border-teal-500/30 text-teal-300 rounded-lg text-xs font-medium hover:bg-teal-500/30"
                >
                  Add
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddExposure(false)}
                  className="px-4 py-1.5 text-slate-400 text-xs hover:text-white"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-900/20 border border-red-700/30 rounded-xl px-4 py-3">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 bg-teal-500 hover:bg-teal-400 disabled:opacity-50 text-black font-semibold py-2.5 rounded-xl text-sm transition-colors"
          >
            {submitting ? "Submitting…" : "Submit Case"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-2.5 rounded-xl text-sm text-slate-400 hover:text-white border border-slate-700 hover:border-slate-600 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
