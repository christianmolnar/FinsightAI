# Agent Memory - Document Organization & Timeline Estimation

**Last Updated:** December 23, 2025  
**Context:** FInsightAI AI Trading Agent Development

---

## 📚 Document Organization Rules

### Folder Structure (ALWAYS FOLLOW)
```
docs/
  architecture/      ← System design, component diagrams, technical architecture
  specifications/    ← UX specs, API specs, feature specifications
  planning/          ← Implementation plans, roadmaps, project tracking
  status/            ← Status updates, session summaries (WITH DATES!)
  guides/            ← How-to guides, quick starts, tutorials
  reference/         ← Reference materials, API docs
```

### Naming Conventions

**❌ BAD (Generic, no context):**
- `DESIGN-SESSION-SUMMARY.md`
- `QUICK-START.md`
- `ARCHITECTURE.md`

**✅ GOOD (Specific, with context):**
- `status/2024-12-23-DESIGN-SESSION.md` (includes date!)
- `guides/PHASE-1-QUICK-START.md` (includes phase context)
- `architecture/AI-AGENT-ARCHITECTURE.md` (describes what it is)

### Key Principles

1. **Date Everything:** Status docs, session summaries need dates (YYYY-MM-DD format)
2. **Be Specific:** Names should describe what the document contains
3. **Follow Structure:** Use existing folders, don't create docs in root
4. **Context Matters:** User should know when/why a document was created
5. **No Redundancy:** Check if similar doc exists before creating new one

---

## ⏰ Time Estimation Rules

### The 84× Acceleration Factor

**Human Hours → Real-Time Hours:**
- Formula: `Real Hours = Human Hours ÷ 84`
- Example: 336 human hours = 4 real-time hours

### BUT: Calendar Time ≠ Real-Time Hours!

**Critical Mistake to Avoid:**
- ❌ "35 real-time hours = 6 weeks"
- ❌ Confusing work hours with calendar weeks

**Correct Calculation:**
```
35 real-time hours = How many calendar days?

It depends on work schedule:
- 8 hours/day: 35 ÷ 8 = 4.4 days (less than 1 week)
- 4 hours/day: 35 ÷ 4 = 8.75 days (1.5 weeks)
- 2 hours/day: 35 ÷ 2 = 17.5 days (2.5 weeks)
- 1 hour/day: 35 ÷ 1 = 35 days (5 weeks)
```

### Always Provide Multiple Timelines

**Template:**
```markdown
**Estimated Human Dev Hours:** 336 hours  
**Actual Dev Time with AI (84× acceleration):** 4 real-time hours (336 ÷ 84)

**Calendar Time (depends on schedule):**
- Working 8 hours/day: ~0.5 days
- Working 4 hours/day: ~1 day
- Working 2 hours/day: ~2 days
- Working 1 hour/day: ~4 days
```

---

## 🎯 Phase Naming Conventions

**❌ BAD (Implies calendar time):**
- "Phase 1 (Week 1)"
- "Phase 2 (Week 2)"

**✅ GOOD (Work time based):**
- "Phase 1 (Day 1: 4 hours)"
- "Phase 2 (Day 2: 3 hours)"

**Or even better (no time assumption):**
- "Phase 1: AI Research Engine (4h)"
- "Phase 2: Sell Validation (3h)"

---

## 🏗️ UI Integration Principles

### When Enhancing Existing UI

**ALWAYS Clarify:**
1. What stays the same ✅
2. What we're adding 🆕
3. What we're enhancing 🔧
4. What we're removing (if anything) ❌

**Template:**
```markdown
## UI Integration Strategy

### What Stays The Same ✅
- Existing Dashboard layout
- Portfolio tab
- Navigation structure
- Tailwind theme

### What We're Adding 🆕
- Research tab (new)
- Queue tab (new)

### What We're Enhancing 🔧
- Dashboard: Add "Pending Actions" widget
- Portfolio: Add AI status indicators
```

**Key Principle:** Default to ENHANCING, not REPLACING. The user loves their current design!

---

## 🧠 Position Monitoring - Complete Feature Set

### When designing position monitoring, ALWAYS include:

1. **SELL signals** (exit position)
   - Stop loss hit
   - Profit target achieved
   - Bad news detected

2. **BUY_MORE signals** (scale into position)
   - Price dips to better entry
   - Fundamentals improving
   - Add to winners
   - Average down smartly

3. **HOLD signals** (no action needed)
   - Position on track
   - No concerns

4. **WATCH signals** (monitor closely)
   - Approaching decision point
   - Needs attention soon

**User Feedback:**
> "I do assume that the engine will also evaluate on positions we already own, whether it's worth holding and buying more, not just buying and selling what we buy."

**Translation:** Position monitoring is NOT just about exits. It's about full position management: HOLD / BUY_MORE / SELL.

---

## 📝 Lessons Learned (December 23, 2025)

### 1. Timeline Communication
- **Error:** Said "6 weeks" when it was really 35 hours of work
- **Fix:** Always provide multiple timelines based on work schedule
- **Root Cause:** Confused real-time hours with calendar time

### 2. Document Organization
- **Error:** Created docs in root with generic names
- **Fix:** Use existing folder structure with dates and specificity
- **Root Cause:** Didn't check existing structure before creating docs

### 3. UI Enhancement vs. Replacement
- **Error:** Didn't clarify we're enhancing, not replacing existing UI
- **Fix:** Always show what stays vs. what's new
- **Root Cause:** Assumed user would know we're building on top

### 4. Position Monitoring Scope
- **Error:** Only designed for exits (SELL), forgot BUY_MORE
- **Fix:** Full position management: HOLD / BUY_MORE / SELL / WATCH
- **Root Cause:** Incomplete understanding of feature requirements

---

## ✅ Action Items for Future Sessions

**Before creating documents:**
- [ ] Check existing folder structure
- [ ] Use specific names with dates (for status docs)
- [ ] Place in appropriate folder (not root)

**Before estimating timelines:**
- [ ] Convert human hours → real-time hours (÷84)
- [ ] Calculate calendar time for multiple schedules (8h, 4h, 2h, 1h/day)
- [ ] Use "Day X" not "Week X" for phases

**Before designing features:**
- [ ] Ask: Are we enhancing or replacing?
- [ ] Clarify what stays vs. what's new
- [ ] Consider full feature scope (e.g., BUY_MORE for positions)

**When user points out errors:**
- [ ] Thank them for catching it
- [ ] Fix immediately
- [ ] Update CNS/memory so it doesn't happen again
- [ ] Learn the underlying principle, not just the specific fix

---

**Status:** Active learning in progress  
**Next Review:** After Phase 1 implementation  
**Goal:** Consistent, accurate documentation and time estimation
