'use client'

import * as React from 'react'
import { X } from 'lucide-react'
import { Badge } from './badge'
import { Input } from './input'
import { cn } from '@/lib/utils'

interface TagInputProps {
  tags: string[]
  onTagsChange: (tags: string[]) => void
  placeholder?: string
  className?: string
}

export function TagInput({ tags, onTagsChange, placeholder = 'Add tags...', className }: TagInputProps) {
  const [inputValue, setInputValue] = React.useState('')

  const addTag = (tag: string) => {
    const trimmedTag = tag.trim()
    if (trimmedTag && !tags.includes(trimmedTag)) {
      onTagsChange([...tags, trimmedTag])
    }
    setInputValue('')
  }

  const removeTag = (tagToRemove: string) => {
    onTagsChange(tags.filter(tag => tag !== tagToRemove))
  }

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addTag(inputValue)
    } else if (e.key === 'Backspace' && inputValue === '' && tags.length > 0) {
      removeTag(tags[tags.length - 1])
    }
  }

  return (
    <div className={cn('space-y-2', className)}>
      <Input
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleInputKeyDown}
        placeholder={placeholder}
      />
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="gap-1">
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="ml-1 hover:bg-secondary-foreground/20 rounded-full p-0.5"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}
    </div>
  )
}