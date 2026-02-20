# PROJECT_IDEAS.md

## Context
Dude Logic Labs is the parent brand/site. Firebook is one product at `firebook.app`.
The Dude Logic Labs site should act as the showcase/blog hub that links to products (including Firebook) and supports web app experiences to increase adoption.


## Governance Workflow
All work follows: `TODO -> IN_PROGRESS -> VERIFY -> DONE`

---

## I012: Port and Deploy Existing Apps into Dude Logic Labs Ecosystem
Epic: Platform Integration
Status: IN_PROGRESS
Priority: P1
Owner: agent

Governance Flow:
- TODO → IN_PROGRESS (started 2026-02-19)

Work:
- [x] Inventory current apps/services and define migration order (Firebook, qrDude, then idea-backed app)
- [ ] Create per-app porting checklist (routing, auth, analytics, branding, links)
- [ ] Integrate app entries into DLC Apps Directory with metadata and status
- [ ] Deploy each app behind correct domain/subdomain/path strategy
- [ ] Validate cross-linking, UTM tracking, and fallback/rollback plans
- [ ] Document runbooks for ongoing app onboarding into DLC ecosystem

Owner Direction (2026-02-19):
- Top 3 app priority order: 1) Firebook, 2) qrDude, 3) best candidate from ideas backlog.
- Preferred routing strategy: path-based routing first (higher autonomy, lower owner overhead).

Acceptance Criteria:
- [ ] App inventory and migration priority list published
- [ ] At least first batch of apps deployed and linked from DLC
- [ ] Routing + analytics validated for each migrated app
- [ ] Operational runbook created for future app ports

Verification Evidence:
- File paths:
  - dudelogiclabs/docs/app-porting-inventory.md
  - dudelogiclabs/docs/app-porting-checklists.md
  - dudelogiclabs/docs/app-deployment-matrix.md
  - dudelogiclabs/docs/app-onboarding-runbook.md

---

## I015: Shopify Channel Integration for Monetization + Conversion
Epic: Commerce Expansion
Status: TODO
Priority: P1
Owner: agent

Work:
- [ ] Define Shopify integration strategy with DLC pages (product highlights, bundles, seasonal drops)
- [ ] Map DLC content/app pages to Shopify conversion paths
- [ ] Add Shopify-linked CTA modules on high-intent pages
- [ ] Define product curation rules for app-relevant merch/tools
- [ ] Instrument Shopify referral tracking (UTM + conversion proxy events)
- [ ] Propose bonus plays (abandoned cart capture hooks, bundles, limited-time promo placements)

Acceptance Criteria:
- [ ] Shopify integration plan documented
- [ ] At least one reusable Shopify CTA/module pattern implemented
- [ ] Referral tracking spec documented and validated
- [ ] Weekly scorecard includes Shopify channel KPI section

Verification Evidence:
- File paths:
  - dudelogiclabs/docs/shopify-integration-strategy.md
  - dudelogiclabs/docs/shopify-placement-map.md
  - dudelogiclabs/docs/shopify-tracking-spec.md
  - dudelogiclabs/docs/shopify-kpi-spec.md

---

## Operating Note for Cron/Heartbeat Agents
During scheduled checks, agents should:
1. Pick highest-priority TODO task not blocked.
2. Move status through governance stages with evidence.
3. Report blockers with concrete next action.
4. If no priority work exists, run app incubation workflow (I007).
5. Avoid creating duplicate tasks unless explicitly requested.
