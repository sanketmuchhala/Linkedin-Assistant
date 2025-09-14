'use client'

import * as React from 'react'
import { Copy, Check } from 'lucide-react'
import { Button } from './button'
import { cn } from '@/lib/utils'

interface CopyButtonProps {
  text: string
  className?: string
  size?: 'sm' | 'default' | 'lg'
  variant?: 'ghost' | 'outline' | 'default'
}

export function CopyButton({ text, className, size = 'sm', variant = 'ghost' }: CopyButtonProps) {
  const [copied, setCopied] = React.useState(false)

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  return (
    <Button
      onClick={copyToClipboard}
      size={size}
      variant={variant}
      className={cn('h-8 w-8 p-0', className)}
    >
      {copied ? (
        <Check className="h-4 w-4 text-green-500" />
      ) : (
        <Copy className="h-4 w-4" />
      )}
    </Button>
  )
}