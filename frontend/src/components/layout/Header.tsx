export default function Header({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="border-b border-zinc-200 bg-white px-8 py-6">
      <h2 className="text-2xl font-semibold text-zinc-900">{title}</h2>
      {subtitle && (
        <p className="text-sm text-zinc-500 mt-1">{subtitle}</p>
      )}
    </div>
  );
}
