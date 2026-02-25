import { getRequestConfig } from 'next-intl/server';
import { headers } from 'next/headers';

// Supported locales — must match Django LANGUAGES
export const locales = ['en', 'es', 'zh-hans', 'vi', 'ko', 'tl'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'en';

/**
 * Resolve the locale for each request.
 *
 * Strategy (in priority order):
 *  1. `Accept-Language` header from the browser
 *  2. Default locale ('en')
 *
 * We do NOT use locale-prefixed URLs (/en/, /es/) — the public health
 * mission requires clean, shareable URLs for QR codes and social sharing.
 * Language detection is transparent to the user.
 */
export default getRequestConfig(async () => {
  const acceptLanguage = headers().get('accept-language') ?? '';
  const locale = resolveLocale(acceptLanguage);

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
    timeZone: 'America/New_York',   // default TZ for date formatting
    now: new Date(),
  };
});


function resolveLocale(acceptLanguage: string): Locale {
  if (!acceptLanguage) return defaultLocale;

  // Parse "en-US,en;q=0.9,es;q=0.8" → ['en', 'es']
  const preferred = acceptLanguage
    .split(',')
    .map((entry) => {
      const [lang] = entry.trim().split(';');
      return lang.trim().toLowerCase().split('-')[0];  // "en-US" → "en"
    });

  for (const lang of preferred) {
    const match = locales.find((l) => l === lang || l.startsWith(lang));
    if (match) return match;
  }

  return defaultLocale;
}
