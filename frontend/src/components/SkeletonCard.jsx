export default function SkeletonCard() {
  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5 animate-pulse">
      {/* Header */}
      <div className="flex justify-between items-start mb-5">
        <div className="space-y-2">
          <div className="h-5 w-14 bg-slate-700 rounded" />
          <div className="h-3 w-32 bg-slate-700/70 rounded" />
        </div>
        <div className="space-y-2 text-right">
          <div className="h-6 w-24 bg-slate-700 rounded ml-auto" />
          <div className="h-3 w-16 bg-slate-700/70 rounded ml-auto" />
        </div>
      </div>

      {/* Valuation gauge skeleton */}
      <div className="mb-5 space-y-2">
        <div className="flex justify-between">
          <div className="h-2 w-20 bg-slate-700/60 rounded" />
          <div className="h-2 w-16 bg-slate-700 rounded" />
          <div className="h-2 w-20 bg-slate-700/60 rounded" />
        </div>
        <div className="h-2 w-full bg-slate-700 rounded-full" />
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-3 gap-3 pt-4 border-t border-slate-700/50">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="text-center space-y-1">
            <div className="h-2 w-10 bg-slate-700/60 rounded mx-auto" />
            <div className="h-4 w-14 bg-slate-700 rounded mx-auto" />
          </div>
        ))}
      </div>

      {/* Returns row */}
      <div className="grid grid-cols-3 gap-3 pt-3 mt-3 border-t border-slate-700/50">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="text-center space-y-1">
            <div className="h-2 w-6 bg-slate-700/60 rounded mx-auto" />
            <div className="h-3 w-12 bg-slate-700 rounded mx-auto" />
          </div>
        ))}
      </div>
    </div>
  )
}
