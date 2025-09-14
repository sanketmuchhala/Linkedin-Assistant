import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('Seeding database...')

  const sampleRecords = [
    {
      fullName: 'Sarah Chen',
      role: 'Senior Product Manager',
      company: 'TechFlow Inc',
      linkedinUrl: 'https://linkedin.com/in/sarahchen',
      source: 'event',
      whyConnect: 'Met at the AI Summit 2024. Sarah gave an insightful presentation on product-led growth in AI tools. We discussed the challenges of user onboarding for technical products, and she mentioned being interested in developer experience optimization.',
      sharedTopics: JSON.stringify(['AI', 'Product Management', 'Developer Experience', 'UX']),
      evidence: JSON.stringify(['Spoke at same AI Summit', 'Both interested in DevEx', 'Exchanged contact cards']),
      tone: 'professional',
      doNotDo: JSON.stringify(['Don\'t mention sales immediately']),
      goal: 'informational_chat',
      cta: 'Would love to continue our conversation about product-led growth strategies',
      tags: JSON.stringify(['high-priority', 'ai-summit', 'product']),
      status: 'DRAFT',
      connectionNote: 'Hi Sarah! Great meeting you at the AI Summit yesterday. Your talk on product-led growth really resonated with me, especially your insights on developer onboarding. Would love to continue our discussion about optimizing the developer experience. Hope to connect!',
      acceptanceDM: 'Thanks for connecting, Sarah! I\'ve been thinking more about our conversation on developer experience optimization. I\'d love to learn more about how TechFlow approaches user onboarding for technical products. Would you be open to a brief chat sometime this week? I can share some insights from my experience as well.'
    },
    {
      fullName: 'Marcus Rodriguez',
      role: 'Engineering Manager',
      company: 'DataCorp',
      linkedinUrl: 'https://linkedin.com/in/marcusrodriguez',
      source: 'referral',
      whyConnect: 'Referred by Jessica Kim, who mentioned Marcus is leading a team working on distributed systems architecture. I\'m exploring similar challenges in my current project and would value his perspective on scaling microservices.',
      sharedTopics: JSON.stringify(['Microservices', 'Distributed Systems', 'Engineering Leadership']),
      evidence: JSON.stringify(['Referred by Jessica Kim', 'Both working on distributed systems', 'Similar engineering challenges']),
      tone: 'friendly',
      doNotDo: JSON.stringify(['Don\'t be overly technical in first message']),
      goal: 'collab',
      cta: 'Interested in exchanging insights on distributed systems challenges',
      tags: JSON.stringify(['referral', 'engineering', 'collaboration']),
      status: 'REQUESTED',
      connectionNote: 'Hi Marcus! Jessica Kim suggested I reach out to you. I understand you\'re doing great work with distributed systems at DataCorp. I\'m facing similar challenges with scaling microservices and would love to exchange insights. Looking forward to connecting!',
      acceptanceDM: 'Thanks for accepting my connection request, Marcus! Jessica spoke highly of your work on distributed systems architecture. I\'m currently working on scaling our microservices infrastructure and running into some interesting challenges around service mesh implementation. Would you be interested in a brief chat to exchange experiences? I\'d be happy to share what we\'ve learned as well.'
    },
    {
      fullName: 'Emily Watson',
      role: 'UX Research Lead',
      company: 'InnovateLabs',
      linkedinUrl: 'https://linkedin.com/in/emilywatson',
      source: 'post',
      whyConnect: 'Emily recently shared a fascinating post about conducting user research for B2B SaaS products. Her approach to combining quantitative and qualitative methods really caught my attention, especially her insights on user interview techniques.',
      sharedTopics: JSON.stringify(['UX Research', 'B2B SaaS', 'User Interviews', 'Design Thinking']),
      evidence: JSON.stringify(['Engaged with her LinkedIn post', 'Commented on user research methodology', 'Both in B2B SaaS space']),
      tone: 'enthusiastic',
      doNotDo: JSON.stringify(['Don\'t ask for too much time initially']),
      goal: 'share_portfolio',
      cta: 'Would love to share my recent UX case study and get your thoughts',
      tags: JSON.stringify(['ux-research', 'b2b-saas', 'design']),
      status: 'ACCEPTED',
      connectionNote: 'Hi Emily! Loved your recent post about user research methodologies for B2B SaaS. Your insights on combining qual and quant research really resonated with me. I recently completed a similar study and would love to get your perspective. Excited to connect!',
      acceptanceDM: 'Hi Emily! Thanks for connecting. I\'ve been following your content on UX research and really admire your systematic approach to user interviews. I recently completed a case study on improving onboarding for a B2B platform and would love to share it with you for feedback. Your insights on research methodology have already influenced my approach. Would you be interested in a quick 15-minute chat?'
    },
    {
      fullName: 'David Park',
      role: 'Startup Founder',
      company: 'GrowthHack Solutions',
      linkedinUrl: 'https://linkedin.com/in/davidpark',
      source: 'news',
      whyConnect: 'Read about David\'s recent Series A funding in TechCrunch. His company\'s approach to growth marketing automation is impressive, and I\'m particularly interested in their customer acquisition strategies for B2B startups.',
      sharedTopics: JSON.stringify(['Startups', 'Growth Marketing', 'B2B Sales', 'Funding']),
      evidence: JSON.stringify(['Read TechCrunch article about his Series A', 'Both in startup ecosystem', 'Similar target market']),
      tone: 'warm',
      doNotDo: JSON.stringify(['Don\'t congratulate on funding without adding value']),
      goal: 'job_referral',
      cta: 'Interested in learning about growth opportunities',
      tags: JSON.stringify(['startup', 'growth', 'funding', 'opportunity']),
      status: 'IN_CONVO',
      connectionNote: 'Hi David! Read about GrowthHack Solutions\' Series A in TechCrunch - congratulations! Your approach to growth marketing automation is fascinating. I\'ve been working on similar challenges in customer acquisition and would love to learn from your experience. Hope to connect!',
      acceptanceDM: 'David, thanks for connecting! I\'ve been really impressed with what you\'re building at GrowthHack Solutions. Your customer acquisition strategies align well with some challenges I\'ve been working on. I\'d love to learn more about how you approach growth marketing automation. Also curious about your team expansion plans - I have experience in both marketing and product growth. Would you be open to a conversation?'
    },
    {
      fullName: 'Lisa Thompson',
      role: 'VP of Engineering',
      company: 'CloudSync Technologies',
      linkedinUrl: 'https://linkedin.com/in/lisathompson',
      source: 'cold',
      whyConnect: 'Lisa has an impressive background in scaling engineering teams at cloud infrastructure companies. Her experience at both early-stage and growth-stage companies would be valuable as I\'m looking to transition into engineering leadership roles.',
      sharedTopics: JSON.stringify(['Engineering Leadership', 'Cloud Infrastructure', 'Team Scaling', 'Career Growth']),
      evidence: JSON.stringify(['Similar career trajectory', 'Both in cloud/infra space', 'Leadership experience']),
      tone: 'curious',
      doNotDo: JSON.stringify(['Don\'t ask for job directly', 'Don\'t make it all about me']),
      goal: 'intro',
      cta: 'Would appreciate insights on engineering leadership transition',
      tags: JSON.stringify(['leadership', 'career', 'cloud', 'cold-outreach']),
      status: 'ARCHIVED',
      connectionNote: 'Hi Lisa! I\'ve been following your career journey from startup engineer to VP of Engineering at CloudSync. Your experience scaling engineering teams really resonates with my own career goals. Would love to connect and learn from your leadership insights!',
      acceptanceDM: 'Lisa, thank you for connecting! I really admire your path from individual contributor to VP of Engineering. I\'m currently an engineering manager looking to grow into senior leadership roles, and your experience scaling teams at CloudSync is exactly the kind of journey I\'d love to learn from. Would you be open to a brief conversation about your transition into engineering leadership? I\'d be happy to buy you coffee (virtual or in-person) and learn about your experiences.'
    }
  ]

  console.log('Creating sample records...')

  for (const record of sampleRecords) {
    await prisma.connectionRecord.create({
      data: record,
    })
    console.log(`Created record for ${record.fullName}`)
  }

  console.log('Seeding completed successfully!')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })