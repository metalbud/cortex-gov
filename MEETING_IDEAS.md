# MEETING_IDEAS.md - Agent Team Improvement Suggestions

## Purpose
This file captures ideas, decisions, and action items from CEO meetings and agent team strategy sessions. Similar to PROJECT_IDEAS.md but focused on:
- Agent capability improvements
- Team workflow optimizations
- Strategic pivots and new initiatives
- Process improvements from meetings

## Governance Workflow
All ideas follow: `TODO -> IN_PROGRESS -> VERIFY -> DONE`

---

## Meeting: Emergency CEO Session - Competitive Analysis & Site Improvements
**Date:** 2026-02-21
**Type:** Emergency CEO Meeting
**Trigger:** Need competitive analysis and site improvement recommendations

### Attendees
- CEO (Kyle)
- Main Agent (The Dude)

### Agenda
1. ✅ Competitive landscape review
2. ✅ Site improvement recommendations
3. ✅ Priority action items

### Meeting Summary

**Competitive Analysis Complete:**
- Analyzed 15+ competitors across 3 markets (poll tools, QR generators, indie app platforms)
- Identified 5 quick wins (< 1 day each) and 4 strategic initiatives (1-4 weeks)
- Created full competitor landscape report: `cortex-gov/artifacts/competitive-analysis/competitor-landscape-2026-02-21.md`

**Key Findings:**
- Firebook: Missing real-time results (table stakes feature)
- qrDude: Missing analytics/tracking (key differentiator)
- DLC: Unique positioning as "indie app launchpad with monetization"

**Decisions Made:**
- ✅ Prioritize QW01 (Real-Time Results) and QW02 (Comparison Page) for this week
- ✅ Start content marketing engine (2 blog posts/week)
- ✅ Build freemium monetization layer in next 2 weeks

### Ideas & Decisions

#### [IN_PROGRESS] CA001: Competitive Analysis Framework
**Priority:** P1
**Owner:** main-agent
**Status:** Initial analysis complete, automation pending
**Description:** Build automated competitive analysis system that:
- ✅ Scans top 5-10 competitor sites in our niche (DONE - 2026-02-21)
- [ ] Compares features, UX, content strategy, monetization
- [ ] Generates weekly improvement recommendations
- [ ] Tracks competitor changes over time

**Acceptance Criteria:**
- [x] Competitor list defined and documented
- [ ] Automated scanning script created
- [x] Comparison report template generated (competitor-landscape-2026-02-21.md)
- [ ] Weekly cadence established

**Verification Evidence:**
- File paths:
  - cortex-gov/artifacts/competitive-analysis/competitor-landscape-2026-02-21.md ✅
  - cortex-gov/artifacts/competitive-analysis/weekly-report-template.md (TODO)
  - cortex-gov/tools/competitive-analysis/scan-competitors.mjs (TODO)

---

#### [IN_PROGRESS] CA002: Site Improvement Backlog
**Priority:** P1
**Owner:** main-agent
**Status:** Backlog created with 9 items prioritized
**Description:** Create prioritized backlog of site improvements based on:
- [x] Competitive gaps identified (DONE - 2026-02-21)
- [ ] User feedback and analytics
- [ ] Technical debt assessment
- [x] Monetization opportunities (DONE - freemium strategy defined)

**Acceptance Criteria:**
- [x] Improvement backlog documented (9 items in competitor-landscape-2026-02-21.md)
- [x] Each item scored by impact/effort
- [x] Top 3 priorities identified for immediate action (QW01, QW02, QW05)
- [x] Timeline estimated for top 10 items

**Verification Evidence:**
- File paths:
  - cortex-gov/artifacts/competitive-analysis/competitor-landscape-2026-02-21.md ✅
  - cortex-gov/artifacts/site-improvements/backlog.md (TODO - extract from analysis)
  - cortex-gov/artifacts/site-improvements/priority-matrix.md (TODO)

---

#### [IN_PROGRESS] CA003: Meeting Cadence & Documentation
**Priority:** P2
**Owner:** main-agent
**Status:** MEETING_IDEAS.md created, cadence pending
**Description:** Establish regular CEO meeting cadence with proper documentation:
- [ ] Weekly strategy sync (30 min)
- [ ] Monthly deep-dive (60 min)
- [ ] Quarterly planning (2 hours)
- [x] All meetings documented in MEETING_IDEAS.md (DONE - this file)

**Acceptance Criteria:**
- [ ] Meeting schedule defined
- [ ] Agenda templates created
- [x] Documentation process established (MEETING_IDEAS.md format)
- [ ] Action item tracking implemented

**Verification Evidence:**
- File paths:
  - cortex-gov/MEETING_IDEAS.md ✅
  - cortex-gov/docs/meeting-cadence.md (TODO)
  - cortex-gov/docs/meeting-agenda-templates.md (TODO)

---

#### [IN_PROGRESS] CA004: Quick Win Implementation Sprint
**Priority:** P0
**Owner:** main-agent
**Status:** Started 2026-02-22, QW01 in progress
**Description:** Implement top 3 quick wins this week:
- QW01: Add real-time results to Firebook (4-6 hours)
- QW02: Create comparison landing page (2-3 hours)
- QW05: Write 2 SEO blog posts (4-6 hours each)

**Acceptance Criteria:**
- [ ] QW01: Real-time poll results working
- [ ] QW02: Comparison page published at /apps/firebook/vs-competitors
- [ ] QW05: 2 blog posts published and shared on Facebook

**Timeline:** Complete by 2026-02-28

**Verification Evidence:**
- Firebook page with live results
- Comparison page URL
- Blog post URLs + Facebook engagement metrics

---

#### [TODO] CA005: Freemium Monetization Strategy
**Priority:** P1
**Owner:** main-agent + CEO approval needed
**Status:** Pending pricing decision
**Description:** Build freemium tier for Firebook and qrDude:
- Free: Basic features (current functionality)
- Pro ($5-9/mo): Analytics, custom branding, unlimited usage

**Acceptance Criteria:**
- [ ] CEO approves pricing tier ($5, $7, or $9/mo?)
- [ ] Stripe integration setup
- [ ] Pricing page created
- [ ] Feature gating implemented

**Timeline:** 2 weeks from approval

**Verification Evidence:**
- Pricing page URL
- Stripe dashboard showing test transactions
- Pro feature documentation

---

## Operating Notes

### How to Use This File
1. **Before meetings:** Add agenda items as TODO entries
2. **During meetings:** Capture decisions, update status to IN_PROGRESS
3. **After meetings:** Assign owners, set priorities, define acceptance criteria
4. **Between meetings:** Track progress, move items through governance flow

### Priority Levels
- **P0:** Critical - blocks other work, needs immediate attention
- **P1:** High - important strategic initiatives
- **P2:** Medium - valuable but can wait
- **P3:** Low - nice to have, backlog items

### Status Flow
```
TODO → IN_PROGRESS → VERIFY → DONE
```

### Linking to PROJECT_IDEAS.md
- Meeting ideas that become concrete projects should be copied to PROJECT_IDEAS.md
- Use consistent ID naming (CA### for meeting ideas, I### for projects, H### for legacy)
- Cross-reference when an idea spawns a project

---

## Archive

### Past Meetings

#### 2026-02-21: Emergency CEO Session
**Outcome:** Hired competitive analysis agent, created MEETING_IDEAS.md framework
**Follow-ups:** CA001, CA002, CA003 (all TODO)
