import { Badge } from './badge'
import { cn } from '@/lib/utils'

type Status = 'DRAFT' | 'REQUESTED' | 'ACCEPTED' | 'IN_CONVO' | 'ARCHIVED'

const statusConfig: Record<Status, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline'; className?: string }> = {
  DRAFT: { label: 'Draft', variant: 'outline', className: 'border-gray-500 text-gray-400' },
  REQUESTED: { label: 'Requested', variant: 'secondary', className: 'bg-blue-900/20 text-blue-400 border-blue-400/30' },
  ACCEPTED: { label: 'Accepted', variant: 'secondary', className: 'bg-green-900/20 text-green-400 border-green-400/30' },
  IN_CONVO: { label: 'In Conversation', variant: 'secondary', className: 'bg-purple-900/20 text-purple-400 border-purple-400/30' },
  ARCHIVED: { label: 'Archived', variant: 'outline', className: 'border-gray-600 text-gray-500' },
}

interface StatusPillProps {
  status: Status
  className?: string
}

export function StatusPill({ status, className }: StatusPillProps) {
  const config = statusConfig[status]

  return (
    <Badge
      variant={config.variant}
      className={cn(config.className, className)}
    >
      {config.label}
    </Badge>
  )
}