import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '@/styles/globals.css'
import { cn } from '@/lib/utils'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'LinkedIn Connection Assistant',
  description: 'Manage your LinkedIn connections with personalized notes and follow-ups',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={cn(inter.className, 'min-h-screen bg-black text-white')}>
        {children}
      </body>
    </html>
  )
}