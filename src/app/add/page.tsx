'use client'

import * as React from 'react'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TagInput } from '@/components/ui/tag-input'
import { CharCounter } from '@/components/ui/char-counter'
import { CopyButton } from '@/components/ui/copy-button'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

const sourceOptions = [
  { value: 'event', label: 'Event' },
  { value: 'post', label: 'Post' },
  { value: 'referral', label: 'Referral' },
  { value: 'news', label: 'News' },
  { value: 'cold', label: 'Cold Outreach' },
]

const toneOptions = [
  { value: 'friendly', label: 'Friendly' },
  { value: 'professional', label: 'Professional' },
  { value: 'enthusiastic', label: 'Enthusiastic' },
  { value: 'warm', label: 'Warm' },
  { value: 'curious', label: 'Curious' },
]

const goalOptions = [
  { value: 'informational_chat', label: 'Informational Chat' },
  { value: 'collab', label: 'Collaboration' },
  { value: 'intro', label: 'Introduction' },
  { value: 'share_portfolio', label: 'Share Portfolio' },
  { value: 'job_referral', label: 'Job Referral' },
  { value: 'hiring', label: 'Hiring' },
]

interface FormData {
  fullName: string
  role: string
  company: string
  linkedinUrl: string
  source: string
  whyConnect: string
  sharedTopics: string[]
  evidence: string[]
  tone: string
  doNotDo: string[]
  goal: string
  cta: string
  tags: string[]
}

interface GeneratedContent {
  connection_note: { text: string; char_count: number }
  accept_message: { text: string; char_count: number }
}

export default function AddLead() {
  const router = useRouter()
  const [formData, setFormData] = React.useState<FormData>({
    fullName: '',
    role: '',
    company: '',
    linkedinUrl: '',
    source: 'event',
    whyConnect: '',
    sharedTopics: [],
    evidence: [],
    tone: 'professional',
    doNotDo: [],
    goal: 'informational_chat',
    cta: '',
    tags: [],
  })

  const [generated, setGenerated] = React.useState<GeneratedContent | null>(null)
  const [isGenerating, setIsGenerating] = React.useState(false)
  const [isSaving, setIsSaving] = React.useState(false)
  const [error, setError] = React.useState<string>('')

  const handleInputChange = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (generated) setGenerated(null) // Clear generated content when form changes
  }

  const generateContent = async () => {
    if (!formData.fullName.trim() || !formData.linkedinUrl.trim() || !formData.whyConnect.trim()) {
      setError('Please fill in the required fields: Name, LinkedIn URL, and Why Connect')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ record: formData }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to generate content')
      }

      const data = await response.json()
      setGenerated(data.generated)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate content')
    } finally {
      setIsGenerating(false)
    }
  }

  const saveRecord = async () => {
    if (!formData.fullName.trim()) {
      setError('Name is required')
      return
    }

    setIsSaving(true)
    setError('')

    try {
      const recordData = {
        ...formData,
        connectionNote: generated?.connection_note.text || null,
        acceptanceDM: generated?.accept_message.text || null,
      }

      const response = await fetch('/api/records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(recordData),
      })

      if (!response.ok) {
        throw new Error('Failed to save record')
      }

      const savedRecord = await response.json()
      router.push(`/record/${savedRecord.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save record')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-black">
      <header className="border-b border-border bg-card/5">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold">Add New Lead</h1>
              <p className="text-muted-foreground">Create a new LinkedIn connection record</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Form */}
          <Card>
            <CardHeader>
              <CardTitle>Connection Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <div className="p-3 rounded bg-destructive/20 border border-destructive/30 text-destructive text-sm">
                  {error}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Full Name *</label>
                  <Input
                    value={formData.fullName}
                    onChange={(e) => handleInputChange('fullName', e.target.value)}
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Role</label>
                  <Input
                    value={formData.role}
                    onChange={(e) => handleInputChange('role', e.target.value)}
                    placeholder="Software Engineer"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Company</label>
                  <Input
                    value={formData.company}
                    onChange={(e) => handleInputChange('company', e.target.value)}
                    placeholder="Tech Corp"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">LinkedIn URL *</label>
                  <Input
                    value={formData.linkedinUrl}
                    onChange={(e) => handleInputChange('linkedinUrl', e.target.value)}
                    placeholder="https://linkedin.com/in/johndoe"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Source</label>
                  <select
                    value={formData.source}
                    onChange={(e) => handleInputChange('source', e.target.value)}
                    className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    {sourceOptions.map(option => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Tone</label>
                  <select
                    value={formData.tone}
                    onChange={(e) => handleInputChange('tone', e.target.value)}
                    className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    {toneOptions.map(option => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Goal</label>
                <select
                  value={formData.goal}
                  onChange={(e) => handleInputChange('goal', e.target.value)}
                  className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {goalOptions.map(option => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Why Connect *</label>
                <Textarea
                  value={formData.whyConnect}
                  onChange={(e) => handleInputChange('whyConnect', e.target.value)}
                  placeholder="Explain why you want to connect with this person..."
                  className="min-h-[100px]"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Call to Action</label>
                <Input
                  value={formData.cta}
                  onChange={(e) => handleInputChange('cta', e.target.value)}
                  placeholder="Would love to chat about..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Shared Topics</label>
                <TagInput
                  tags={formData.sharedTopics}
                  onTagsChange={(tags) => handleInputChange('sharedTopics', tags)}
                  placeholder="AI, startups, react..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Evidence/Context</label>
                <TagInput
                  tags={formData.evidence}
                  onTagsChange={(tags) => handleInputChange('evidence', tags)}
                  placeholder="Spoke at same event, mutual connections..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Don&apos;t Do</label>
                <TagInput
                  tags={formData.doNotDo}
                  onTagsChange={(tags) => handleInputChange('doNotDo', tags)}
                  placeholder="Don&apos;t mention sales, don&apos;t be pushy..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Tags</label>
                <TagInput
                  tags={formData.tags}
                  onTagsChange={(tags) => handleInputChange('tags', tags)}
                  placeholder="high-priority, local, etc..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  onClick={generateContent}
                  disabled={isGenerating}
                  className="flex-1"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    'Generate Messages'
                  )}
                </Button>
                <Button
                  onClick={saveRecord}
                  disabled={isSaving}
                  variant="outline"
                >
                  {isSaving ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    'Save Draft'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Generated Content */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Connection Note
                  {generated && (
                    <CopyButton text={generated.connection_note.text} />
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {generated ? (
                  <div>
                    <div className="bg-secondary/20 p-4 rounded-lg mb-2">
                      <p className="text-sm">{generated.connection_note.text}</p>
                    </div>
                    <CharCounter
                      current={generated.connection_note.char_count}
                      max={300}
                    />
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">
                    Click &quot;Generate Messages&quot; to create your personalized connection note
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Acceptance Follow-up Message
                  {generated && (
                    <CopyButton text={generated.accept_message.text} />
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {generated ? (
                  <div>
                    <div className="bg-secondary/20 p-4 rounded-lg mb-2">
                      <p className="text-sm">{generated.accept_message.text}</p>
                    </div>
                    <CharCounter
                      current={generated.accept_message.char_count}
                      max={600}
                    />
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">
                    This message will be generated to send after they accept your connection
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