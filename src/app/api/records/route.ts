import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { connectionRecordSchema } from '@/lib/validations'
import { parseJsonArray, stringifyArray } from '@/lib/utils'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const status = searchParams.get('status')
    const tags = searchParams.get('tags')
    const search = searchParams.get('search')
    const source = searchParams.get('source')
    const goal = searchParams.get('goal')

    const where: any = {}

    if (status) {
      where.status = status
    }

    if (tags) {
      const tagList = tags.split(',')
      where.tags = {
        contains: tagList[0] // Simple contains search for now
      }
    }

    if (search) {
      where.OR = [
        { fullName: { contains: search, mode: 'insensitive' } },
        { company: { contains: search, mode: 'insensitive' } },
        { whyConnect: { contains: search, mode: 'insensitive' } },
      ]
    }

    if (source) {
      where.source = source
    }

    if (goal) {
      where.goal = goal
    }

    const records = await prisma.connectionRecord.findMany({
      where,
      orderBy: { createdAt: 'desc' },
    })

    // Parse JSON strings back to arrays for response
    const parsedRecords = records.map(record => ({
      ...record,
      sharedTopics: parseJsonArray(record.sharedTopics),
      evidence: parseJsonArray(record.evidence),
      doNotDo: parseJsonArray(record.doNotDo),
      tags: parseJsonArray(record.tags),
    }))

    return NextResponse.json(parsedRecords)
  } catch (error) {
    console.error('Error fetching records:', error)
    return NextResponse.json(
      { error: 'Failed to fetch records' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const validatedData = connectionRecordSchema.parse(body)

    const record = await prisma.connectionRecord.create({
      data: {
        ...validatedData,
        sharedTopics: stringifyArray(validatedData.sharedTopics),
        evidence: stringifyArray(validatedData.evidence),
        doNotDo: stringifyArray(validatedData.doNotDo),
        tags: stringifyArray(validatedData.tags),
      },
    })

    // Parse JSON strings back to arrays for response
    const parsedRecord = {
      ...record,
      sharedTopics: parseJsonArray(record.sharedTopics),
      evidence: parseJsonArray(record.evidence),
      doNotDo: parseJsonArray(record.doNotDo),
      tags: parseJsonArray(record.tags),
    }

    return NextResponse.json(parsedRecord, { status: 201 })
  } catch (error) {
    console.error('Error creating record:', error)
    return NextResponse.json(
      { error: 'Failed to create record' },
      { status: 500 }
    )
  }
}