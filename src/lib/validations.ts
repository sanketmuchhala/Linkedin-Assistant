import { z } from 'zod'

export const connectionRecordSchema = z.object({
  fullName: z.string().min(1, 'Name is required'),
  role: z.string().optional(),
  company: z.string().optional(),
  linkedinUrl: z.string().url('Must be a valid URL'),
  source: z.enum(['event', 'post', 'referral', 'news', 'cold']),
  whyConnect: z.string().min(1, 'Why connect is required'),
  sharedTopics: z.array(z.string()).default([]),
  evidence: z.array(z.string()).default([]),
  tone: z.enum(['friendly', 'professional', 'enthusiastic', 'warm', 'curious']).optional(),
  doNotDo: z.array(z.string()).default([]),
  goal: z.enum(['informational_chat', 'collab', 'intro', 'share_portfolio', 'job_referral', 'hiring']).optional(),
  cta: z.string().optional(),
  tags: z.array(z.string()).default([]),
  status: z.enum(['DRAFT', 'REQUESTED', 'ACCEPTED', 'IN_CONVO', 'ARCHIVED']).default('DRAFT'),
  nextActionDate: z.date().optional(),
  nextActionLabel: z.string().optional(),
})

export const updateConnectionRecordSchema = connectionRecordSchema.partial().extend({
  id: z.string(),
})

export const generateRequestSchema = z.object({
  recordId: z.string().optional(),
  record: connectionRecordSchema.optional(),
}).refine(
  (data) => data.recordId || data.record,
  'Either recordId or record must be provided'
)

export const generationOutputSchema = z.object({
  connection_note: z.object({
    text: z.string().max(300, 'Connection note must be ≤300 characters'),
    char_count: z.number(),
  }),
  accept_message: z.object({
    text: z.string().max(600, 'Accept message must be ≤600 characters'),
    char_count: z.number(),
  }),
})

export type ConnectionRecordInput = z.infer<typeof connectionRecordSchema>
export type UpdateConnectionRecordInput = z.infer<typeof updateConnectionRecordSchema>
export type GenerateRequestInput = z.infer<typeof generateRequestSchema>
export type GenerationOutput = z.infer<typeof generationOutputSchema>