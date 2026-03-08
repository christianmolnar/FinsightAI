# Phase 4-6: Autonomous Trading System - Implementation Tracker
**Goal:** Live autonomous trading by Monday March 10, 2026 at 9:30 AM ET  
**Timeline:** March 7-9, 2026 (Weekend Build)  
**Approach:** Option A (Production Ready) - Always Shippable  
**Total Estimated:** 18 hours

---

## 🎯 Success Criteria

**Monday Morning 9:30 AM:**
- ✅ Scanner runs automatically every 15 minutes during market hours
- ✅ Finds 5-10 opportunities per day (technical breakouts)
- ✅ Creates proposals in Transaction Queue with AI reasoning
- ✅ Position monitor checks every 5 minutes for exit signals
- ✅ High-confidence trades (>85%) auto-execute
- ✅ Risk controls prevent runaway losses
- ✅ Circuit breakers pause trading on consecutive losses
- ✅ All activity logged and visible in UI

---

## 📋 Implementation Phases

### **Phase 4A: Market Scanner Service** (Friday Night)
**Goal:** Scanner finds technical breakouts and creates proposals  
**Status:** 🔲 Not Started  
**Estimated:** 4 hours  
**Actual:** - hours

#### Tasks
- [ ] **4A.1: Create market_scanner.py** (2 hours)
  - [ ] Define scan universe (S&P 100 or watchlist)
  - [ ] Strategy: Technical breakouts (price > 50-day high)
  - [ ] Filters: Volume > 1M, spread < 0.5%, price > $10
  - [ ] Return candidate list with scores
  - [ ] **Test:** Run manually, verify 3-5 candidates found
  - [ ] **Commit:** "feat: Add market scanner service with breakout strategy"

- [ ] **4A.2: Create opportunity_analyzer.py** (1 hour)
  - [ ] For each candidate: Run stock research
  - [ ] Dual AI analysis (OpenAI + Claude)
  - [ ] Calculate confidence score
  - [ ] If confidence > 75% → Return opportunity
  - [ ] **Test:** Analyze 3 candidates, verify AI reasoning
  - [ ] **Commit:** "feat: Add opportunity analyzer with dual AI"

- [ ] **4A.3: Create scanner API endpoint** (30 min)
  - [ ] `POST /api/scanner/run` - Manual trigger
  - [ ] Call market_scanner → opportunity_analyzer
  - [ ] Create pending transactions for opportunities
  - [ ] Return summary (candidates, opportunities, proposals)
  - [ ] **Test:** Postman call → Verify proposals in queue
  - [ ] **Commit:** "feat: Add scanner API endpoint"

- [ ] **4A.4: Add "Scan Now" button to UI** (30 min)
  - [ ] Button in Dashboard or Research tab
  - [ ] Loading spinner during scan
  - [ ] Display results: "Found X opportunities, created Y proposals"
  - [ ] Link to Transaction Queue
  - [ ] **Test:** Click button → See proposals
  - [ ] **Commit:** "feat: Add Scan Now button to UI"

**Checkpoint 4A Complete:**
- ✅ Can manually trigger scanner
- ✅ Scanner finds 3-5 candidates
- ✅ Proposals appear in Transaction Queue
- ✅ Each proposal has AI reasoning
- ✅ All tests passing
- ✅ Code committed to git

---

### **Phase 4B: Background Scheduler** (Saturday Morning)
**Goal:** Scanner runs automatically every 15 minutes during market hours  
**Status:** 🔲 Not Started  
**Estimated:** 2 hours  
**Actual:** - hours

#### Tasks
- [ ] **4B.1: Create scan_opportunities.py job** (1 hour)
  - [ ] Background job in `backend/jobs/`
  - [ ] Cron: */15 9-16 * * 1-5 (every 15 min, market hours)
  - [ ] Call scanner service
  - [ ] Log results to database
  - [ ] Error handling and retry logic
  - [ ] **Test:** Run manually, verify execution
  - [ ] **Commit:** "feat: Add background scanner job"

- [ ] **4B.2: Configure Railway cron** (30 min)
  - [ ] Update Railway configuration
  - [ ] Set cron schedule
  - [ ] Verify timezone (ET)
  - [ ] **Test:** Check Railway logs for execution
  - [ ] **Commit:** "chore: Configure Railway cron for scanner"

- [ ] **4B.3: Add Agent Status widget** (30 min)
  - [ ] Show "Last Scan: X min ago"
  - [ ] Show "Opportunities Today: X"
  - [ ] Show "Proposals Created: X"
  - [ ] Auto-refresh every 60 seconds
  - [ ] **Test:** Widget updates in real-time
  - [ ] **Commit:** "feat: Add Agent Status widget to Dashboard"

**Checkpoint 4B Complete:**
- ✅ Scanner runs every 15 minutes automatically
- ✅ Only runs during market hours (9:30-4:00 ET)
- ✅ Logs visible in Railway
- ✅ Status widget shows activity
- ✅ All tests passing
- ✅ Code committed to git

---

### **Phase 5A: Position Monitor** (Saturday Afternoon)
**Goal:** Monitor open positions, create exit signals  
**Status:** 🔲 Not Started  
**Estimated:** 4 hours  
**Actual:** - hours

#### Tasks
- [ ] **5A.1: Create position_evaluator.py** (2 hours)
  - [ ] For each open position:
    - [ ] Check stop loss: price < entry * 0.95
    - [ ] Check profit target: price > entry * 1.10
    - [ ] Check max hold: days > 14
  - [ ] Calculate position health (Healthy, Warning, Alert)
  - [ ] Return evaluation with reasoning
  - [ ] **Test:** Mock positions, verify exit signals
  - [ ] **Commit:** "feat: Add position evaluator service"

- [ ] **5A.2: Create exit signal generator** (1 hour)
  - [ ] Generate SELL proposals on triggers
  - [ ] Calculate P&L, tax implications
  - [ ] Add AI reasoning for exit
  - [ ] Priority: IMMEDIATE (stop loss), HIGH (profit target)
  - [ ] **Test:** Simulate stop loss → Verify SELL proposal
  - [ ] **Commit:** "feat: Add exit signal generator"

- [ ] **5A.3: Create monitor_positions.py job** (30 min)
  - [ ] Background job in `backend/jobs/`
  - [ ] Cron: */5 9-16 * * 1-5 (every 5 min, market hours)
  - [ ] Call position_evaluator
  - [ ] Create exit proposals when needed
  - [ ] **Test:** Run manually with test position
  - [ ] **Commit:** "feat: Add position monitor background job"

- [ ] **5A.4: Add position status to Portfolio UI** (30 min)
  - [ ] Status badge: ✅ Healthy, ⚠️ Warning, 🔴 Alert
  - [ ] Show stop loss and target prices
  - [ ] Days held counter
  - [ ] Link to pending exit proposals
  - [ ] **Test:** Display shows correct statuses
  - [ ] **Commit:** "feat: Add position status to Portfolio"

**Checkpoint 5A Complete:**
- ✅ Monitor runs every 5 minutes automatically
- ✅ Detects stop loss breaches
- ✅ Detects profit target hits
- ✅ Creates SELL proposals in queue
- ✅ Portfolio shows position health
- ✅ All tests passing
- ✅ Code committed to git

---

### **Phase 6A: Auto-Execute Logic** (Sunday Morning)
**Goal:** High-confidence proposals execute automatically  
**Status:** 🔲 Not Started  
**Estimated:** 3 hours  
**Actual:** - hours

#### Tasks
- [ ] **6A.1: Create auto_executor.py service** (1.5 hours)
  - [ ] Rules engine:
    - [ ] Scanner proposals: confidence > 85% → auto-execute
    - [ ] Stop loss signals: → auto-execute immediately
    - [ ] Profit targets: → auto-execute after 1-hour delay
  - [ ] Check risk limits before execution
  - [ ] Execute trade via Alpaca
  - [ ] Mark transaction as "AUTO_EXECUTED"
  - [ ] **Test:** Mock high-confidence proposal → Verify execution
  - [ ] **Commit:** "feat: Add auto-executor service"

- [ ] **6A.2: Create auto_execute.py job** (1 hour)
  - [ ] Background job in `backend/jobs/`
  - [ ] Cron: */1 9-16 * * 1-5 (every 1 min, market hours)
  - [ ] Check pending transactions with auto_execute=true
  - [ ] Call auto_executor service
  - [ ] Log execution results
  - [ ] **Test:** Run manually with test proposals
  - [ ] **Commit:** "feat: Add auto-execute background job"

- [ ] **6A.3: Add Agent Configuration UI** (30 min)
  - [ ] Settings page:
    - [ ] Enable/disable auto-execute toggle
    - [ ] Confidence threshold slider (75-95%)
    - [ ] Max position size input
    - [ ] Max concurrent positions input
  - [ ] Save to database
  - [ ] **Test:** Change settings → Verify respected
  - [ ] **Commit:** "feat: Add Agent Configuration UI"

**Checkpoint 6A Complete:**
- ✅ High-confidence trades execute automatically
- ✅ Stop losses execute immediately
- ✅ User can enable/disable auto-execute
- ✅ User can set confidence threshold
- ✅ All tests passing
- ✅ Code committed to git

---

### **Phase 6B: Risk Controls** (Sunday Afternoon)
**Goal:** Prevent runaway losses and enforce limits  
**Status:** 🔲 Not Started  
**Estimated:** 3 hours  
**Actual:** - hours

#### Tasks
- [ ] **6B.1: Create risk_manager.py** (1 hour)
  - [ ] Risk limits:
    - [ ] Max portfolio exposure: 80%
    - [ ] Max position size: 10% of portfolio
    - [ ] Max concurrent positions: 10
    - [ ] Max daily trades: 20
    - [ ] Max daily loss: 2% of portfolio
  - [ ] Validate before execution
  - [ ] **Test:** Exceed limits → Verify blocked
  - [ ] **Commit:** "feat: Add risk manager with limits"

- [ ] **6B.2: Create circuit_breaker.py** (1 hour)
  - [ ] Circuit breakers:
    - [ ] 3 consecutive losses → Pause 1 hour
    - [ ] Daily loss > 2% → Stop all new trades
    - [ ] Portfolio < 90% start → Require manual approval
  - [ ] Store breaker state in database
  - [ ] **Test:** Trigger breakers → Verify pause
  - [ ] **Commit:** "feat: Add circuit breakers"

- [ ] **6B.3: Add Risk Dashboard widget** (1 hour)
  - [ ] Display current limits vs usage
  - [ ] Show circuit breaker status
  - [ ] Warning indicators when near limits
  - [ ] Manual reset buttons for breakers
  - [ ] **Test:** Display shows accurate data
  - [ ] **Commit:** "feat: Add Risk Dashboard widget"

**Checkpoint 6B Complete:**
- ✅ System respects all risk limits
- ✅ Circuit breakers prevent runaway losses
- ✅ Dashboard shows risk status
- ✅ User can override with manual approval
- ✅ All tests passing
- ✅ Code committed to git

---

### **Phase 6C: Alerts & Monitoring** (Sunday Evening)
**Goal:** User notified of important events  
**Status:** 🔲 Not Started  
**Estimated:** 2 hours  
**Actual:** - hours

#### Tasks
- [ ] **6C.1: Create alert_service.py** (1 hour)
  - [ ] Alert types:
    - [ ] Circuit breaker triggered
    - [ ] Daily loss limit reached
    - [ ] Large position (>5% portfolio)
    - [ ] Trade executed (optional)
  - [ ] Email notifications (optional)
  - [ ] In-app notifications
  - [ ] **Test:** Trigger alerts → Verify delivery
  - [ ] **Commit:** "feat: Add alert service"

- [ ] **6C.2: Add Activity Log widget** (1 hour)
  - [ ] Show recent scanner activity
  - [ ] Show recent executions
  - [ ] Show alerts/warnings
  - [ ] Filter by type/date
  - [ ] **Test:** Display shows recent activity
  - [ ] **Commit:** "feat: Add Activity Log widget"

**Checkpoint 6C Complete:**
- ✅ User receives alerts on important events
- ✅ Activity log shows full history
- ✅ All tests passing
- ✅ Code committed to git

---

### **Phase 7: End-to-End Testing** (Sunday Evening)
**Goal:** System proven ready for Monday  
**Status:** 🔲 Not Started  
**Estimated:** 2 hours  
**Actual:** - hours

#### Tasks
- [ ] **7.1: Full system test on paper account** (1 hour)
  - [ ] Enable scanner on paper account
  - [ ] Let run for 1-2 hours
  - [ ] Verify proposals created
  - [ ] Verify auto-execution works
  - [ ] Verify position monitoring works
  - [ ] Verify risk limits enforced
  - [ ] **Test:** Full autonomous loop working
  - [ ] **Commit:** "test: Full system validated on paper"

- [ ] **7.2: Go-Live Checklist** (30 min)
  - [ ] Scanner enabled ✅
  - [ ] Position monitor enabled ✅
  - [ ] Auto-execute enabled (85% threshold) ✅
  - [ ] Risk limits configured ✅
  - [ ] Circuit breakers active ✅
  - [ ] Alert system tested ✅
  - [ ] Paper account proven ✅
  - [ ] **Live account DISABLED** until Monday decision ✅

- [ ] **7.3: Documentation** (30 min)
  - [ ] Update WHOLE-SITE-IMPLEMENTATION-PLAN.md
  - [ ] Create go-live instructions
  - [ ] Document monitoring procedures
  - [ ] Create rollback plan
  - [ ] **Commit:** "docs: Add autonomous trading documentation"

**Checkpoint 7 Complete:**
- ✅ System runs autonomously on paper account
- ✅ All phases working together
- ✅ Documentation complete
- ✅ Ready for Monday morning
- ✅ Final commit and git tag

---

## 📊 Progress Tracking

| Phase | Description | Est. | Actual | Status | Commits |
|-------|-------------|------|--------|--------|---------|
| 4A | Market Scanner Service | 4h | -h | 🔲 Not Started | 0 |
| 4B | Background Scheduler | 2h | -h | 🔲 Not Started | 0 |
| 5A | Position Monitor | 4h | -h | 🔲 Not Started | 0 |
| 6A | Auto-Execute Logic | 3h | -h | 🔲 Not Started | 0 |
| 6B | Risk Controls | 3h | -h | 🔲 Not Started | 0 |
| 6C | Alerts & Monitoring | 2h | -h | 🔲 Not Started | 0 |
| 7 | End-to-End Testing | 2h | -h | 🔲 Not Started | 0 |
| **TOTAL** | | **20h** | **0h** | **0% complete** | **0** |

---

## 🎯 Always Shippable Principle

**After Each Task:**
1. ✅ Write the code
2. ✅ Test manually (verify it works)
3. ✅ Run any automated tests
4. ✅ Commit with descriptive message
5. ✅ Update this tracker
6. ✅ Update WHOLE-SITE-IMPLEMENTATION-PLAN.md

**Never commit broken code.** Every commit should be deployable.

---

## 🚀 Monday Morning Procedure

### Pre-Market (9:00 AM ET)
1. Check Railway logs - scanner running?
2. Check paper account - any weekend activity?
3. Review pending proposals in queue
4. Verify market hours badge ready

### Market Open (9:30 AM ET)
1. Scanner starts automatic scanning
2. First scan results within 15 minutes
3. Watch for first auto-execute (if high confidence found)
4. Monitor position health

### First Hour Check-In (10:30 AM)
1. Review scanner performance: How many opportunities?
2. Review executions: Any auto-executed trades?
3. Check position monitor: All positions tracked?
4. Verify no circuit breakers triggered

### End of Day (4:00 PM ET)
1. Review full day activity
2. Check P&L on executed trades
3. Review any alerts/warnings
4. Plan improvements for Tuesday

---

## 📝 Notes & Learnings

**Design Decisions:**
- Using S&P 100 for scan universe (manageable size, high liquidity)
- Technical breakouts only for v1 (proven strategy, simple to implement)
- 85% confidence threshold for auto-execute (conservative start)
- 5-minute position monitoring (frequent enough, not excessive)

**Risk Management Philosophy:**
- Multiple layers: Hard limits + Circuit breakers + Manual override
- Conservative defaults: 10% max position, 80% max exposure
- Fail-safe: System pauses rather than continues on errors

**Testing Strategy:**
- Test each component individually
- Test full integration before go-live
- Paper trading validation required
- Live trading requires manual enable

---

## 🔗 Related Documents

- **Master Plan:** `/docs/implementation/WHOLE-SITE-IMPLEMENTATION-PLAN.md`
- **Weekend Plan:** `/docs/status/2026-03-07-V1.0-RELEASE-STATUS.md`
- **V1.0 Analysis:** `/docs/BACKTEST-STRATEGY-ANALYSIS-2026-03-07.md`
- **Release Notes:** `/docs/RELEASE-NOTES.md`

---

**Current Phase:** 🔲 Phase 4A - Market Scanner Service  
**Next Task:** Create `backend/services/market_scanner.py`  
**Time:** Friday evening, March 7, 2026  
**Let's build!** 🚀
