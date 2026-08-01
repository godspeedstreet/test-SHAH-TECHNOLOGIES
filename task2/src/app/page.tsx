import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-gray-50 font-sans dark:bg-gray-900 min-h-screen">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-gray-800 sm:items-start rounded-xl shadow-lg mx-8 mt-16">
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
          <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-gray-900 dark:text-gray-100">
            Outreach Platform — Companies
          </h1>
          <p className="max-w-md text-lg leading-8 text-gray-600 dark:text-gray-400">
            Просмотр компаний из PostgreSQL с поиском и фильтрацией
          </p>
        </div>
        <div className="flex flex-col gap-4 text-base font-medium sm:flex-row mt-8">
          <Link
            href="/companies"
            className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-blue-600 px-5 text-white transition-colors hover:bg-blue-700 md:w-[200px]"
          >
            Открыть /companies
          </Link>
        </div>
      </main>
    </div>
  );
}