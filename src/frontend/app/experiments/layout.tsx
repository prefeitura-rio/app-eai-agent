import ExperimentsHeader from '@/app/components/header';

export default function ExperimentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
        <ExperimentsHeader />
        <main className="">
            <div className="">
                {children}
            </div>
        </main>
    </div>
  );
}
