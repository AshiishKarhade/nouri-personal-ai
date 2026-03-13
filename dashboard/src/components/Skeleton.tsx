import type { CSSProperties } from 'react'

interface SkeletonProps {
  className?: string
  width?: string | number
  height?: string | number
  style?: CSSProperties
}

export function Skeleton({ className = '', width, height, style }: SkeletonProps) {
  return (
    <div
      className={`rounded-xl ${className}`}
      style={{
        width,
        height,
        background: '#262626',
        animation: 'pulse-skeleton 1.5s ease-in-out infinite',
        borderRadius: 12,
        ...style,
      }}
    />
  )
}

export function SkeletonRow({ count = 1, className = '' }: { count?: number; className?: string }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className={`h-4 ${className}`} />
      ))}
    </>
  )
}

export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div
      className={`rounded-xl p-4 ${className}`}
      style={{ background: '#141414', border: '1px solid #262626' }}
    >
      <Skeleton className="h-4 w-1/2 mb-3" />
      <Skeleton className="h-8 w-3/4 mb-2" />
      <Skeleton className="h-3 w-1/3" />
    </div>
  )
}
