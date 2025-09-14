'use client'

import * as React from 'react'
import { ArrowLeft, ExternalLink, Loader2, Edit3 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { StatusPill } from '@/components/ui/status-pill'
import { Badge } from '@/components/ui/badge'
import { CopyButton } from '@/components/ui/copy-button'
import { CharCounter } from '@/components/ui/char-counter'
import { formatDateTime } from '@/lib/utils'
import Link from 'next/link'

interface ConnectionRecord {
  id: string
  fullName: string
  role?: string
  company?: string
  linkedinUrl: string
  source: string
  whyConnect: string
  sharedTopics: string[]
  evidence: string[]
  tone?: string
  doNotDo: string[]
  goal?: string
  cta?: string
  tags: string[]
  status: 'DRAFT' | 'REQUESTED' | 'ACCEPTED' | 'IN_CONVO' | 'ARCHIVED'
  connectionNote?: string
  acceptanceDM?: string
  nextActionDate?: string
  nextActionLabel?: string
  createdAt: string
  updatedAt: string
}

const statusOptions = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'REQUESTED', label: 'Requested' },
  { value: 'ACCEPTED', label: 'Accepted' },
  { value: 'IN_CONVO', label: 'In Conversation' },
  { value: 'ARCHIVED', label: 'Archived' },
]

export default function RecordDetail({ params }: { params: { id: string } }) {
  const [record, setRecord] = React.useState<ConnectionRecord | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [isGenerating, setIsGenerating] = React.useState(false)
  const [error, setError] = React.useState('')

  React.useEffect(() => {
    fetchRecord()
  }, [params.id]) // eslint-disable-line react-hooks/exhaustive-deps

  const fetchRecord = async () => {
    try {
      const response = await fetch(`/api/records/${params.id}`)
      if (response.ok) {
        const data = await response.json()
        setRecord(data)
      } else {
        setError('Record not found')
      }
    } catch (err) {
      setError('Failed to load record')
    } finally {
      setLoading(false)
    }
  }

  const updateStatus = async (newStatus: string) => {
    if (!record) return

    try {
      const response = await fetch(`/api/records/${record.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      })

      if (response.ok) {
        const updatedRecord = await response.json()
        setRecord(updatedRecord)
      }
    } catch (err) {
      setError('Failed to update status')
    }
  }

  const regenerateContent = async () => {
    if (!record) return

    setIsGenerating(true)
    setError('')

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recordId: record.id }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to generate content')
      }

      const data = await response.json()
      setRecord(data.record)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to regenerate content')
    } finally {
      setIsGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading record...</p>
        </div>
      </div>
    )
  }

  if (!record) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl mb-4">Record not found</p>
          <Link href="/">
            <Button>Back to Dashboard</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black">
      <header className="border-b border-border bg-card/5">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="h-4 w-4" />
                </Button>
              </Link>
              <div>
                <h1 className="text-2xl font-bold">{record.fullName}</h1>
                <p className="text-muted-foreground">
                  {record.role} {record.role && record.company && 'at'} {record.company}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <StatusPill status={record.status} />
              <Button variant="outline" size="icon">
                <Edit3 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {error && (
        <div className="container mx-auto px-4 py-4">
          <div className="p-3 rounded bg-destructive/20 border border-destructive/30 text-destructive text-sm">
            {error}
          </div>
        </div>
      )}

      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Context Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Context & Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">LinkedIn Profile</label>
                  <div className="flex items-center gap-2">
                    <a
                      href={record.linkedinUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:underline text-sm truncate flex-1"
                    >
                      {record.linkedinUrl}
                    </a>
                    <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                      <a href={record.linkedinUrl} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Source</label>
                    <Badge variant="outline">{record.source}</Badge>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Goal</label>
                    <Badge variant="outline">{record.goal || 'informational_chat'}</Badge>
                  </div>
                </div>

                {record.tone && (
                  <div>
                    <label className="block text-sm font-medium mb-1">Tone</label>
                    <Badge variant="outline">{record.tone}</Badge>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium mb-1">Why Connect</label>
                  <p className="text-sm bg-secondary/20 p-3 rounded">{record.whyConnect}</p>
                </div>

                {record.cta && (
                  <div>
                    <label className="block text-sm font-medium mb-1">Call to Action</label>
                    <p className="text-sm bg-secondary/20 p-3 rounded">{record.cta}</p>
                  </div>
                )}

                {record.sharedTopics.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Shared Topics</label>
                    <div className="flex flex-wrap gap-1">
                      {record.sharedTopics.map((topic) => (
                        <Badge key={topic} variant="secondary" className="text-xs">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {record.evidence.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Evidence/Context</label>
                    <div className="flex flex-wrap gap-1">
                      {record.evidence.map((item) => (
                        <Badge key={item} variant="secondary" className="text-xs">
                          {item}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {record.doNotDo.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Don&apos;t Do</label>
                    <div className="flex flex-wrap gap-1">
                      {record.doNotDo.map((item) => (
                        <Badge key={item} variant="destructive" className="text-xs">
                          {item}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {record.tags.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Tags</label>
                    <div className="flex flex-wrap gap-1">
                      {record.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t">
                  <p className="text-xs text-muted-foreground">
                    Created: {formatDateTime(record.createdAt)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Updated: {formatDateTime(record.updatedAt)}
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Status Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <label className="block text-sm font-medium">Update Status</label>
                  <div className="flex flex-wrap gap-2">
                    {statusOptions.map((option) => (
                      <Button
                        key={option.value}
                        variant={record.status === option.value ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => updateStatus(option.value)}
                      >
                        {option.label}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Generated Content Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Connection Note
                  <div className="flex gap-2">
                    {record.connectionNote && (
                      <CopyButton text={record.connectionNote} />
                    )}
                    <Button
                      onClick={regenerateContent}
                      disabled={isGenerating}
                      size="sm"
                      variant="outline"
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                          Regenerating...
                        </>
                      ) : (
                        'Regenerate'
                      )}
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {record.connectionNote ? (
                  <div>
                    <div className="bg-secondary/20 p-4 rounded-lg mb-3">
                      <p className="text-sm">{record.connectionNote}</p>
                    </div>
                    <CharCounter
                      current={record.connectionNote.length}
                      max={300}
                    />
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground text-sm mb-4">
                      No connection note generated yet
                    </p>
                    <Button onClick={regenerateContent} disabled={isGenerating}>
                      {isGenerating ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        'Generate Messages'
                      )}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Acceptance Follow-up Message
                  {record.acceptanceDM && (
                    <CopyButton text={record.acceptanceDM} />
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {record.acceptanceDM ? (
                  <div>
                    <div className="bg-secondary/20 p-4 rounded-lg mb-3">
                      <p className="text-sm">{record.acceptanceDM}</p>
                    </div>
                    <CharCounter
                      current={record.acceptanceDM.length}
                      max={600}
                    />
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm text-center py-8">
                    No acceptance message generated yet
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}