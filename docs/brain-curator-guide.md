# 🧠 Brain Curator Guide

**For Stephen (and other team members)**

The Brain Curator is an intelligent knowledge management system that lets you add information to PhonoLogic's central knowledge base naturally—while preventing accidental overwrites of correct information.

---

## How It Works

### The Problem It Solves
When you're moving fast and dump thoughts/updates, you might:
- Accidentally overwrite correct info with outdated info
- Add something that contradicts existing knowledge
- Duplicate information that already exists

### The Solution
The Brain Curator **checks your input against existing knowledge** and:
1. ✅ **Accepts** if no conflicts found
2. ⚠️ **Pushes back** if it detects a conflict
3. 🤔 **Asks for clarification** if unsure

---

## Using the Brain Curator

### Option 1: Ops Portal UI (Recommended)

1. Go to [ops.phonologic.cloud](https://ops.phonologic.cloud)
2. Navigate to **AI Hub** tab
3. Find the **🧠 Brain Curator** section
4. Type naturally in the chat box

**Examples:**
```
"What's our current pricing?"
→ Returns: Parent Plan is $20/mo annual, $25/mo monthly

"Update: our pricing is now $15/month"
→ Response: "Hey Stephen, conflict! Brain says $20/mo. Update or keep?"

"Do we have rate limiting set up?"
→ Returns: "Yes! Rate limiting: 60/min default, 20/min writes, 10/min auth"

"We need to add rate limiting"
→ Response: "Actually, we already have rate limiting configured..."
```

### Option 2: Direct API

```bash
# Query mode - just ask questions
curl -X POST https://ops.phonologic.cloud/api/orchestrator/brain/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is our launch timeline?", "mode": "query"}'

# Contribute mode - add new information
curl -X POST https://ops.phonologic.cloud/api/orchestrator/brain/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Update: we now have 50 beta testers", "mode": "contribute"}'

# Auto mode - let system detect intent
curl -X POST https://ops.phonologic.cloud/api/orchestrator/brain/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is our beta launch still Jan 28?", "mode": "auto"}'
```

---

## Conflict Resolution

When the Brain Curator detects a conflict, you'll see options:

| Action | What It Does |
|--------|--------------|
| **Update Brain** | Replace existing info with your new info |
| **Keep Existing** | Discard your input, keep what's in the brain |
| **Add as Note** | Add your input as a note without overwriting |
| **Clarify** | Provide more context so the system understands better |

### Example Conflict Flow

```
You: "Our pricing is $15/month now"

Brain Curator: "🧠 Hey Stephen, hold up! I found some potential conflicts:

1. Contradiction detected in `pricing.parent_plan`
   - You said: $15...
   - Brain says: Annual: $20/month, Monthly: $25/month
   - Confidence: 80%

What would you like to do?
[Update Brain] [Keep Existing] [Add as Note]"
```

---

## What Gets Checked

The Brain Curator checks for conflicts in:

| Category | Examples |
|----------|----------|
| **Pricing** | Dollar amounts, plan names, tiers |
| **Timeline** | Launch dates, beta dates, milestones |
| **Features** | Claims about what exists or doesn't exist |
| **Team** | Roles, who does what |
| **General** | Semantic similarity to existing content |

---

## Tips for Stephen

1. **Just dump thoughts** - The system will parse your intent
2. **Be specific** - "Update: pricing is now $X" vs just "$X"
3. **Questions are safe** - Asking never overwrites anything
4. **Trust the pushback** - If the system says something conflicts, double-check
5. **Use "Update:" prefix** - Makes it clear you're adding, not asking

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/orchestrator/brain/chat` | POST | Natural language chat interface |
| `/api/orchestrator/brain/contribute` | POST | Direct contribution with conflict detection |
| `/api/orchestrator/brain/resolve` | POST | Resolve a pending contribution |
| `/api/orchestrator/brain/pending` | GET | View pending contributions |
| `/api/orchestrator/brain/query` | POST | Query existing knowledge |

---

## Future Enhancements

- [ ] **Slack Integration** - Chat with brain via Slack DM
- [ ] **Email Integration** - Forward emails to brain for ingestion
- [ ] **Document Upload** - Upload PDFs/docs for automatic parsing
- [ ] **Approval Workflow** - Route sensitive changes for Joey's review
- [ ] **Audit Log** - Track all brain changes with timestamps

---

*Last updated: January 18, 2026*
