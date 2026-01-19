/**
 * Brain Chat endpoint - Answers questions using company knowledge
 * Returns natural language responses, not raw JSON
 */

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { question, message, category, mode } = req.body;
  const queryText = question || message; // Accept both 'question' and 'message'
  
  if (!queryText?.trim()) {
    return res.status(400).json({ error: 'Question is required' });
  }

  // Try the orchestrator's intelligent brain/chat endpoint
  let orchestratorUrl = process.env.ORCHESTRATOR_URL;
  console.log('[BRAIN CHAT] ORCHESTRATOR_URL:', orchestratorUrl);
  
  if (orchestratorUrl) {
    if (!orchestratorUrl.startsWith('http')) {
      orchestratorUrl = `https://${orchestratorUrl}`;
    }
    orchestratorUrl = orchestratorUrl.replace(/\/$/, '');
    
    try {
      const endpoint = `${orchestratorUrl}/api/orchestrator/brain/chat`;
      console.log('[BRAIN CHAT] Calling:', endpoint);
      
      // Forward X-User-Email header for authentication
      const headers = { 'Content-Type': 'application/json' };
      if (req.headers['x-user-email']) {
        headers['X-User-Email'] = req.headers['x-user-email'];
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify({ 
          message: queryText, 
          mode: mode || 'query'
        }),
      });
      
      console.log('[BRAIN CHAT] Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('[BRAIN CHAT] Got AI response');
        return res.json({
          response: data.response,
          mode: data.mode,
          conflicts: data.conflicts || [],
          contribution_id: data.contribution_id
        });
      } else {
        const errorText = await response.text();
        console.log('[BRAIN CHAT] Orchestrator error:', response.status, errorText.substring(0, 200));
      }
    } catch (error) {
      console.log('[BRAIN CHAT] Orchestrator unavailable:', error.message);
    }
  } else {
    console.log('[BRAIN CHAT] No ORCHESTRATOR_URL configured, using fallback');
  }

  // Fallback: Use built-in knowledge if orchestrator unavailable
  const fallbackAnswer = getBuiltInAnswer(queryText);
  if (fallbackAnswer) {
    return res.json({
      response: fallbackAnswer.answer,
      sources: fallbackAnswer.sources || ['built-in knowledge'],
      confidence: fallbackAnswer.confidence || 0.8
    });
  }

  return res.json({
    response: "I don't have enough information to answer that question. The orchestrator may be starting up - please try again in a moment.",
    sources: [],
    confidence: 0
  });
}

/**
 * Synthesize a natural language answer from brain search results
 */
function synthesizeAnswer(question, results) {
  const questionLower = question.toLowerCase();
  
  // Pricing questions
  if (questionLower.includes('cost') || questionLower.includes('price') || questionLower.includes('pricing')) {
    return formatPricingAnswer(results);
  }
  
  // Team questions
  if (questionLower.includes('team') || questionLower.includes('who') || questionLower.includes('founder')) {
    return formatTeamAnswer(results);
  }
  
  // Product questions
  if (questionLower.includes('product') || questionLower.includes('what do') || questionLower.includes('feature')) {
    return formatProductAnswer(results);
  }
  
  // Company questions
  if (questionLower.includes('company') || questionLower.includes('about') || questionLower.includes('mission')) {
    return formatCompanyAnswer(results);
  }
  
  // Timeline / GTM / roadmap questions
  if (questionLower.includes('launch') || questionLower.includes('timeline') || questionLower.includes('roadmap') || 
      questionLower.includes('when') || questionLower.includes('market') || questionLower.includes('timing') ||
      questionLower.includes('gtm') || questionLower.includes('strategy') || questionLower.includes('milestone')) {
    return formatTimelineAnswer(results);
  }
  
  // Generic summary
  return formatGenericAnswer(question, results);
}

function formatPricingAnswer(results) {
  // Look for pricing info in results
  for (const result of results) {
    if (result.results?.[0]?.pricing_model) {
      const product = result.results[0];
      return `**PhonoLogic Pricing:**

We use a **freemium model** with these tiers:

• **Free Tier** - Limited generations, watermarked exports, on-screen validator
• **Parent Plan** - $20/month (billed annually) or $25/month - Full exports, 300 stories/month, no watermarks
• **Teacher Pro** - Coming soon - Folders, IEP formats, unlimited stories
• **School/District** - Coming soon - Custom pricing for institutions

The Parent Plan is designed for families who want to support their child's reading practice at home.`;
    }
  }
  
  return `Our pricing uses a **freemium model**:

• **Free** - Try the product with limited features
• **Parent Plan** - $20/month (annual) or $25/month for full access
• **Teacher & School plans** - Coming soon

For specific pricing details, check the Pricing page in the wiki or ask Stephen.`;
}

function formatTeamAnswer(results) {
  const teamMembers = [];
  
  for (const result of results) {
    if (result.source === 'team' && result.results?.[0]?.name) {
      teamMembers.push(result.results[0]);
    }
  }
  
  if (teamMembers.length > 0) {
    let answer = `**PhonoLogic Team:**\n\n`;
    for (const member of teamMembers) {
      answer += `• **${member.name}** - ${member.role}\n  ${member.bio?.substring(0, 150)}...\n\n`;
    }
    return answer;
  }
  
  return `**Our Team:**

• **Stephen Robins** - CEO & Founder - Former Brewmaster turned entrepreneur, MBA from IE Business School
• **Joey Drury** - CTO - Former Associate Director at Cardinal Path, digital analytics expert
• **Marysia Robins** - Student Success Teacher - Orton-Gillingham trained literacy specialist`;
}

function formatProductAnswer(results) {
  for (const result of results) {
    if (result.source === 'products' && result.results?.[0]) {
      const product = result.results[0];
      return `**${product.name}**

${product.tagline}

${product.description}

**Key Features:**
${product.key_features?.slice(0, 4).map(f => `• ${f}`).join('\n')}

**Value Proposition:**
${product.value_propositions?.slice(0, 2).map(v => `• ${v}`).join('\n')}`;
    }
  }
  
  return `**PhonoLogic Decodable Story Generator**

An AI-powered tool that creates individualized, decodable reading texts aligned to each student's phonics scope.

**Key Features:**
• AI-generated stories matching phonics skills
• Personalized to student interests
• Decodability validation before teacher sees content
• Science of Reading aligned`;
}

function formatCompanyAnswer(results) {
  return `**PhonoLogic**

*Where literacy meets possibility*

**Mission:** Finding a text that fits your learner should not be the hard part of learning how to read. We create reading practice that fits any learner in minutes.

**Founded:** July 2025 in Toronto, Canada

**Stage:** Private Beta (launching January 28, 2026)

**Recognition:**
• Finalist Runner-Up at IE Venture Lab Competition (Dec 2025)
• Incubated at TMU Social Ventures Zone
• Featured Startup at Vancouver Web Summit (May 2026)`;
}

function formatTimelineAnswer(results) {
  return `**PhonoLogic Go-to-Market Timeline:**

**Launch Phases:**
• **Jan 28, 2026** - Private Beta Launch (50 testers)
• **Mar 1, 2026** - Public Beta (500 users)
• **May 15, 2026** - Public Launch at Vancouver Web Summit
• **Sept 2026** - District Ready (K-8 coverage)

**Current Status:** Private Beta, raising $250K pre-seed SAFE

**GTM Strategy:**
• B2B2C model: Sell to schools/districts, teachers use with students
• Initial focus: Literacy specialists, reading interventionists, SLPs
• Land with teachers, expand to school-wide licenses
• Pilot partnerships prove value before district deals

**Traction:**
• Pilot with Montcrest School, Toronto (12 educators, 20 students)
• Finalist Runner-Up at IE Venture Lab Competition
• Incubated at TMU Social Ventures Zone`;
}

function formatGenericAnswer(question, results) {
  if (results.length === 0) {
    return "I couldn't find specific information about that. Try asking about our product, team, pricing, mission, or roadmap.";
  }
  
  // Try to extract key info from results
  const firstResult = results[0]?.results?.[0];
  if (firstResult) {
    if (firstResult.name && firstResult.description) {
      return `**${firstResult.name}**\n\n${firstResult.description}`;
    }
    if (firstResult.quote) {
      return `"${firstResult.quote}"\n— ${firstResult.attribution}`;
    }
  }
  
  return "I found some related information but I'm not sure how to summarize it for your specific question. Could you rephrase or be more specific?";
}

/**
 * Built-in answers for common questions when orchestrator is unavailable
 */
function getBuiltInAnswer(question) {
  const q = question.toLowerCase();
  
  // Product cost / pricing
  if (q.includes('cost') || q.includes('price') || q.includes('pricing') || q.includes('how much')) {
    return {
      answer: `**PhonoLogic Pricing:**

• **Free Tier** - Limited generations, watermarked exports, try before you buy
• **Parent Plan** - **$20/month** (billed annually) or $25/month
  - Full exports without watermarks
  - 300 stories/month soft limit
  - Purchase additional stories as needed
• **Teacher Pro** - Coming soon
• **School/District** - Coming soon - custom pricing

The Parent Plan is designed for families supporting their child's reading practice at home.`,
      sources: ['pricing info'],
      confidence: 0.95
    };
  }
  
  // Mission / about
  if (q.includes('mission') || q.includes('what do you do') || q.includes('about')) {
    return {
      answer: `**PhonoLogic's Mission:**

*"Finding a text that fits your learner should not be the hard part of learning how to read."*

We create **AI-powered decodable texts** that match each student's phonics scope and personal interests. Teachers pick a phonics focus, topic, and length — and PhonoLogic generates a fully decodable, engaging story in seconds.

**The Problem We Solve:** Half of students don't read at grade level. Teachers spend 5-6 hours weekly hunting for appropriate texts. Generic AI tools violate structured literacy rules.

**Our Solution:** Scope-aligned stories validated before they reach students.`,
      sources: ['company info'],
      confidence: 0.95
    };
  }
  
  // Team / who
  if (q.includes('team') || q.includes('who work') || q.includes('founder')) {
    return {
      answer: `**PhonoLogic Team:**

• **Stephen Robins** - CEO & Founder
  Former award-winning Brewmaster, MBA from IE Business School. Founded PhonoLogic to help his wife spend less time finding materials and more time teaching.

• **Joey Drury** - CTO
  Former Associate Director at Cardinal Path. Digital analytics expert building the technical foundation.

• **Marysia Robins** - Student Success Teacher
  Orton-Gillingham trained literacy specialist with 7+ years in special education. Ensures everything we build actually works in classrooms.`,
      sources: ['team directory'],
      confidence: 0.95
    };
  }
  
  // Timeline / launch / roadmap / GTM
  if (q.includes('launch') || q.includes('timeline') || q.includes('roadmap') || q.includes('when') ||
      q.includes('market') || q.includes('timing') || q.includes('gtm') || q.includes('strategy') || q.includes('milestone')) {
    return {
      answer: `**PhonoLogic Launch Timeline:**

• **Jan 28, 2026** - Private Beta Launch (50 testers)
• **Mar 1, 2026** - Public Beta (500 users)
• **May 15, 2026** - Public Launch at Vancouver Web Summit
• **Sept 2026** - District Ready (K-8 coverage)

**Current Status:** Private Beta, raising $250K pre-seed SAFE

**Traction:**
• Pilot with Montcrest School, Toronto (12 educators, 20 students)
• Finalist Runner-Up at IE Venture Lab Competition
• Incubated at TMU Social Ventures Zone`,
      sources: ['roadmap', 'milestones'],
      confidence: 0.9
    };
  }
  
  return null;
}
