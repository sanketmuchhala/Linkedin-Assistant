import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { LLMAdapter } from '@/lib/llm'
import { generateRequestSchema, generationOutputSchema } from '@/lib/validations'
import { parseJsonArray, stringifyArray } from '@/lib/utils'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const validatedRequest = generateRequestSchema.parse(body)

    let record

    if (validatedRequest.recordId) {
      // Get existing record
      const existingRecord = await prisma.connectionRecord.findUnique({
        where: { id: validatedRequest.recordId },
      })

      if (!existingRecord) {
        return NextResponse.json(
          { error: 'Record not found' },
          { status: 404 }
        )
      }

      record = existingRecord
    } else if (validatedRequest.record) {
      // Use provided record data (convert arrays to strings for LLM processing)
      record = {
        ...validatedRequest.record,
        role: validatedRequest.record.role || null,
        company: validatedRequest.record.company || null,
        tone: validatedRequest.record.tone || null,
        goal: validatedRequest.record.goal || null,
        cta: validatedRequest.record.cta || null,
        sharedTopics: stringifyArray(validatedRequest.record.sharedTopics || []),
        evidence: stringifyArray(validatedRequest.record.evidence || []),
        doNotDo: stringifyArray(validatedRequest.record.doNotDo || []),
        tags: stringifyArray(validatedRequest.record.tags || []),
        id: 'temp', // temporary ID for processing
        createdAt: new Date(),
        updatedAt: new Date(),
        connectionNote: null,
        acceptanceDM: null,
        nextActionDate: validatedRequest.record.nextActionDate || null,
        nextActionLabel: validatedRequest.record.nextActionLabel || null,
      }
    }

    if (!record) {
      return NextResponse.json(
        { error: 'No record data provided' },
        { status: 400 }
      )
    }

    // Initialize LLM adapter
    const llmAdapter = new LLMAdapter()

    // Generate content
    const generated = await llmAdapter.generateContent(record)

    // Validate the generated content
    const validatedOutput = generationOutputSchema.parse(generated)

    // If we have a real record ID, update it with the generated content
    if (validatedRequest.recordId) {
      const updatedRecord = await prisma.connectionRecord.update({
        where: { id: validatedRequest.recordId },
        data: {
          connectionNote: validatedOutput.connection_note.text,
          acceptanceDM: validatedOutput.accept_message.text,
        },
      })

      // Parse JSON strings back to arrays for response
      const parsedRecord = {
        ...updatedRecord,
        sharedTopics: parseJsonArray(updatedRecord.sharedTopics),
        evidence: parseJsonArray(updatedRecord.evidence),
        doNotDo: parseJsonArray(updatedRecord.doNotDo),
        tags: parseJsonArray(updatedRecord.tags),
      }

      return NextResponse.json({
        record: parsedRecord,
        generated: validatedOutput,
      })
    } else {
      // Just return the generated content without saving
      return NextResponse.json({
        generated: validatedOutput,
      })
    }

  } catch (error) {
    console.error('Error generating content:', error)

    if (error instanceof Error) {
      // Handle specific LLM errors
      if (error.message.includes('API key')) {
        return NextResponse.json(
          { error: 'LLM API configuration error. Please check your API keys in settings.' },
          { status: 500 }
        )
      }

      if (error.message.includes('Failed to parse')) {
        return NextResponse.json(
          { error: 'Generated content format error. Please try again.' },
          { status: 500 }
        )
      }
    }

    return NextResponse.json(
      { error: 'Failed to generate content' },
      { status: 500 }
    )
  }
}