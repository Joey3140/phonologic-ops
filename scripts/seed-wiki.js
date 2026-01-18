/**
 * Wiki Seed Script - Pre-populates the wiki with company information
 * 
 * Run with: UPSTASH_REDIS_REST_URL=xxx UPSTASH_REDIS_REST_TOKEN=xxx node scripts/seed-wiki.js
 */

const { Redis } = require('@upstash/redis');

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN
});

const WIKI_KEY = 'phonologic:wiki';

const wikiPages = [
  {
    id: 'wiki_company_overview',
    title: 'Company Overview',
    category: 'onboarding',
    content: `**PhonoLogic** is an AI-powered speech therapy platform designed to help children develop proper speech and language skills through engaging, gamified exercises.

**Mission:** To make speech therapy accessible, affordable, and effective for every child who needs it.

**Founded:** 2024
**Headquarters:** Canada
**Domain:** phonologic.ca / phonologic.cloud

**Core Product:**
- AI-powered speech assessment and feedback
- Gamified therapy exercises for children
- Progress tracking for parents and therapists
- Cloud-based platform accessible from any device

**Target Users:**
- Children aged 3-12 with speech difficulties
- Parents seeking speech therapy resources
- Speech-Language Pathologists (SLPs)
- Schools and educational institutions

**Key Differentiators:**
- Real-time AI speech analysis
- Engaging game-based learning
- Affordable compared to traditional therapy
- Accessible from home, reducing barriers to treatment`
  },
  {
    id: 'wiki_tech_stack',
    title: 'Technology Stack',
    category: 'decisions',
    content: `**Frontend:**
- React / Next.js for web applications
- Modern CSS with Tailwind
- Responsive design for mobile and tablet

**Backend:**
- Node.js serverless functions
- Vercel for hosting and deployments
- Upstash Redis for data storage and caching

**AI/ML:**
- Speech recognition and analysis
- Natural language processing
- Real-time audio processing

**Infrastructure:**
- Vercel (phonologic.cloud hosting)
- Upstash Redis (database)
- Google Cloud Platform (AI services)
- Hover (domain management)

**Development Tools:**
- GitHub for version control
- Windsurf IDE with Cascade AI
- ClickUp for project management

**Domains:**
- phonologic.ca - Primary domain
- phonologic.cloud - Application hosting
- ops.phonologic.cloud - Operations portal`
  },
  {
    id: 'wiki_team_structure',
    title: 'Team Structure',
    category: 'onboarding',
    content: `**Leadership:**
- Joey Drury - Founder/CEO

**Departments:**
- Product & Engineering
- Marketing & Growth
- Operations
- Sales & Partnerships

**Communication:**
- Google Workspace for email and docs
- Team meetings via Google Meet
- Project tracking in ClickUp

**Decision Making:**
- Major decisions documented in Wiki (Decisions category)
- Weekly team syncs for alignment
- Async communication for day-to-day updates`
  },
  {
    id: 'wiki_tools_access',
    title: 'Tools & Access Guide',
    category: 'onboarding',
    content: `**Getting Started:**
All team members get access to the following tools with their @phonologic.ca Google account:

**Core Tools (automatic access):**
- Google Workspace (email, calendar, drive, docs)
- Operations Portal (ops.phonologic.cloud)
- ClickUp (project management)

**Development Tools (request access):**
- GitHub organization
- Vercel team
- Upstash console

**Design & Marketing:**
- Pitch.com (presentations)
- Looker Studio (analytics)

**How to Request Access:**
1. Contact your manager or admin
2. Specify which tool you need
3. Explain the business reason
4. Access typically granted within 24 hours

**Security Notes:**
- Always use your @phonologic.ca account
- Enable 2FA on all accounts
- Never share credentials
- Report suspicious activity immediately`
  },
  {
    id: 'wiki_google_accelerator',
    title: 'Google for Startups Accelerator',
    category: 'decisions',
    content: `**Program:** Google for Startups Accelerator

**Status:** Accepted / Participating

**What it Provides:**
- Access to Google Cloud credits
- Mentorship from Google experts
- AI/ML technical guidance
- Networking with other startups
- Visibility and credibility

**Key Deliverables:**
- Pitch deck (see Pitch.com section in portal)
- Product demos
- Progress reports

**Timeline:**
- Application submitted
- Acceptance received
- Program participation ongoing

**Resources:**
- Pitch deck available in Pitch.com section
- Program materials in Google Drive > Operations`
  },
  {
    id: 'wiki_communication_norms',
    title: 'Communication Guidelines',
    category: 'policies',
    content: `**Email:**
- Use for external communication and formal internal matters
- Response expected within 24 hours on business days
- Use clear subject lines

**Meetings:**
- Default to 25 or 50 minute meetings (not 30/60)
- Always have an agenda
- Document decisions and action items
- Prefer async when possible

**Documentation:**
- Major decisions go in Wiki
- Project updates in ClickUp
- Meeting notes in Google Docs
- Announcements via Operations Portal

**Response Times:**
- Urgent: Same day
- Normal: Within 24 hours
- Low priority: Within 48 hours

**Best Practices:**
- Be concise and clear
- Use bullet points for readability
- Include context and next steps
- Tag relevant people directly`
  },
  {
    id: 'wiki_expense_policy',
    title: 'Expense Policy',
    category: 'policies',
    content: `**General Guidelines:**
- All expenses must have a clear business purpose
- Receipts required for all expenses
- Submit expenses within 30 days

**Pre-Approved Expenses:**
- Software subscriptions under $50/month
- Books and learning materials
- Domain renewals

**Requires Approval:**
- Software over $50/month
- Hardware purchases
- Travel expenses
- Conference attendance

**How to Submit:**
1. Keep all receipts
2. Document business purpose
3. Submit via expense system
4. Await approval

**Reimbursement:**
- Processed bi-weekly
- Direct deposit to bank account`
  }
];

async function seedWiki() {
  console.log('Seeding wiki with company information...\n');

  for (const page of wikiPages) {
    const pageData = {
      title: page.title,
      content: page.content,
      category: page.category,
      author: 'System',
      authorEmail: 'system@phonologic.ca',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    try {
      await redis.hset(WIKI_KEY, { [page.id]: JSON.stringify(pageData) });
      console.log(`✓ Created: ${page.title} (${page.category})`);
    } catch (error) {
      console.error(`✗ Failed: ${page.title} - ${error.message}`);
    }
  }

  console.log('\nWiki seeding complete!');
  console.log(`Total pages: ${wikiPages.length}`);
}

seedWiki().catch(console.error);
