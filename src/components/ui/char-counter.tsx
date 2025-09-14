import { cn } from '@/lib/utils'

interface CharCounterProps {
  current: number
  max: number
  className?: string
}

export function CharCounter({ current, max, className }: CharCounterProps) {
  const percentage = (current / max) * 100
  const isNearLimit = percentage > 90
  const isOverLimit = current > max

  return (
    <div className={cn('text-xs', className)}>
      <span
        className={cn(
          'font-mono',
          isOverLimit
            ? 'text-destructive'
            : isNearLimit
            ? 'text-yellow-500'
            : 'text-muted-foreground'
        )}
      >
        {current}/{max}
      </span>
      {isOverLimit && (
        <span className="ml-2 text-destructive">Exceeds limit by {current - max}</span>
      )}
    </div>
  )
}