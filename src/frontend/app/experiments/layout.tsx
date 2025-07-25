import ExperimentsHeader from '@/app/components/header';

export default function ExperimentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
        <ExperimentsHeader />
        <main className="flex-grow p-4">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                {children}
            </div>
        </main>
    </div>
  );
}
