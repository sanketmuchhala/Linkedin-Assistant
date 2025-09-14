'use client'

import * as React from 'react'
import { Plus, Search, Settings, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusPill } from '@/components/ui/status-pill'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'
import Link from 'next/link'

interface ConnectionRecord {
  id: string
  fullName: string
  role?: string
  company?: string
  source: string
  whyConnect: string
  tags: string[]
  status: 'DRAFT' | 'REQUESTED' | 'ACCEPTED' | 'IN_CONVO' | 'ARCHIVED'
  connectionNote?: string
  nextActionDate?: string
  nextActionLabel?: string
  createdAt: string
}

const statusColumns: { status: string; label: string }[] = [
  { status: 'DRAFT', label: 'Draft' },
  { status: 'REQUESTED', label: 'Requested' },
  { status: 'ACCEPTED', label: 'Accepted' },
  { status: 'IN_CONVO', label: 'In Conversation' },
  { status: 'ARCHIVED', label: 'Archived' },
]

function ConnectionCard({ record }: { record: ConnectionRecord }) {
  const truncateText = (text: string, maxLength: number) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  }

  return (
    <Card className="mb-3 hover:bg-card/80 transition-colors cursor-pointer">
      <Link href={`/record/${record.id}`}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-base font-semibold">
                {record.fullName}
              </CardTitle>
              {(record.role || record.company) && (
                <p className="text-sm text-muted-foreground">
                  {record.role} {record.role && record.company && 'at'} {record.company}
                </p>
              )}
            </div>
            <StatusPill status={record.status} />
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <p className="text-sm text-muted-foreground mb-3">
            {truncateText(record.whyConnect, 100)}
          </p>

          {record.connectionNote && (
            <div className="mb-3">
              <p className="text-xs text-muted-foreground mb-1">Connection Note ({record.connectionNote.length}/300)</p>
              <p className="text-xs bg-secondary/20 p-2 rounded">
                {truncateText(record.connectionNote, 80)}
              </p>
            </div>
          )}

          {record.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {record.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {record.tags.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{record.tags.length - 3} more
                </Badge>
              )}
            </div>
          )}

          {record.nextActionDate && (
            <div className="text-xs text-yellow-400">
              {record.nextActionLabel || 'Follow up'}: {formatDate(record.nextActionDate)}
            </div>
          )}
        </CardContent>
      </Link>
    </Card>
  )
}

function EmptyColumn({ status }: { status: string }) {
  return (
    <div className="text-center py-8 text-muted-foreground">
      <p className="text-sm">No {status.toLowerCase()} connections yet</p>
    </div>
  )
}

export default function Dashboard() {
  const [records, setRecords] = React.useState<ConnectionRecord[]>([])
  const [search, setSearch] = React.useState('')
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    fetchRecords()
  }, [search]) // eslint-disable-line react-hooks/exhaustive-deps

  const fetchRecords = async () => {
    try {
      const params = new URLSearchParams()
      if (search) params.append('search', search)

      const response = await fetch(`/api/records?${params}`)
      if (response.ok) {
        const data = await response.json()
        setRecords(data)
      }
    } catch (error) {
      console.error('Error fetching records:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRecordsByStatus = (status: string) => {
    return records.filter(record => record.status === status)
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="border-b border-border bg-card/5">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">LinkedIn Connection Assistant</h1>
              <p className="text-muted-foreground">Manage your connection pipeline</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search connections..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9 w-64"
                />
              </div>
              <Button variant="outline" size="icon">
                <Filter className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Settings className="h-4 w-4" />
              </Button>
              <Link href="/add">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Lead
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Kanban Board */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-5 gap-6">
          {statusColumns.map(({ status, label }) => {
            const statusRecords = getRecordsByStatus(status)

            return (
              <div key={status} className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="font-semibold text-lg">{label}</h2>
                  <Badge variant="outline" className="ml-2">
                    {statusRecords.length}
                  </Badge>
                </div>

                <div className="min-h-[400px] space-y-3">
                  {loading ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <p className="text-sm">Loading...</p>
                    </div>
                  ) : statusRecords.length > 0 ? (
                    statusRecords.map((record) => (
                      <ConnectionCard key={record.id} record={record} />
                    ))
                  ) : (
                    <EmptyColumn status={status} />
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </main>
    </div>
  )
}