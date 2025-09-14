import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { updateConnectionRecordSchema } from '@/lib/validations'
import { parseJsonArray, stringifyArray } from '@/lib/utils'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const record = await prisma.connectionRecord.findUnique({
      where: { id: params.id },
    })

    if (!record) {
      return NextResponse.json(
        { error: 'Record not found' },
        { status: 404 }
      )
    }

    // Parse JSON strings back to arrays for response
    const parsedRecord = {
      ...record,
      sharedTopics: parseJsonArray(record.sharedTopics),
      evidence: parseJsonArray(record.evidence),
      doNotDo: parseJsonArray(record.doNotDo),
      tags: parseJsonArray(record.tags),
    }

    return NextResponse.json(parsedRecord)
  } catch (error) {
    console.error('Error fetching record:', error)
    return NextResponse.json(
      { error: 'Failed to fetch record' },
      { status: 500 }
    )
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()

    const validatedData = updateConnectionRecordSchema.parse({
      ...body,
      id: params.id,
    })

    const updateData: any = { ...validatedData }
    delete updateData.id

    // Convert arrays to JSON strings for storage
    if (updateData.sharedTopics) {
      updateData.sharedTopics = stringifyArray(updateData.sharedTopics)
    }
    if (updateData.evidence) {
      updateData.evidence = stringifyArray(updateData.evidence)
    }
    if (updateData.doNotDo) {
      updateData.doNotDo = stringifyArray(updateData.doNotDo)
    }
    if (updateData.tags) {
      updateData.tags = stringifyArray(updateData.tags)
    }

    const record = await prisma.connectionRecord.update({
      where: { id: params.id },
      data: updateData,
    })

    // Parse JSON strings back to arrays for response
    const parsedRecord = {
      ...record,
      sharedTopics: parseJsonArray(record.sharedTopics),
      evidence: parseJsonArray(record.evidence),
      doNotDo: parseJsonArray(record.doNotDo),
      tags: parseJsonArray(record.tags),
    }

    return NextResponse.json(parsedRecord)
  } catch (error) {
    console.error('Error updating record:', error)
    return NextResponse.json(
      { error: 'Failed to update record' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await prisma.connectionRecord.delete({
      where: { id: params.id },
    })

    return NextResponse.json({ message: 'Record deleted successfully' })
  } catch (error) {
    console.error('Error deleting record:', error)
    return NextResponse.json(
      { error: 'Failed to delete record' },
      { status: 500 }
    )
  }
}