import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { getLocale, getMessages } from 'next-intl/server';
import './globals.css';

const plusJakarta = Plus_Jakarta_Sans({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: '[PROJECT_NAME] — Food Safety Intelligence',
    template: '%s — [PROJECT_NAME]',
  },
  description: 'Open-source food safety intelligence platform. Restaurant grades, recall alerts, and outbreak advisories.',
};

// Inline script — registers the service worker after the page loads.
// Using a raw string keeps this out of the React hydration cycle and
// avoids a 'use client' directive on the root layout.
const SW_SCRIPT = `
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function (err) {
      console.warn('[SW] Registration failed:', err);
    });
  });
}
`;

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale   = await getLocale();
  const messages = await getMessages();

  return (
    <html lang={locale} suppressHydrationWarning>
      <body className={plusJakarta.className}>
        <NextIntlClientProvider locale={locale} messages={messages}>
          {children}
        </NextIntlClientProvider>
        {/* Service worker registration — enables offline caching for restaurant grade pages */}
        <script dangerouslySetInnerHTML={{ __html: SW_SCRIPT }} />
      </body>
    </html>
  );
}
