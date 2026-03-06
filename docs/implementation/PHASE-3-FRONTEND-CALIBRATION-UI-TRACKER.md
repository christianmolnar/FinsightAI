# Phase 3: Frontend Calibration UI - Implementation Tracker

**Started:** March 5, 2026, 9:15 PM  
**Status:** 🔄 IN PROGRESS  
**Estimated Time:** 2-3 hours  
**Goal:** Build frontend interface for viewing and applying calibration recommendations

---

## 📋 Task Checklist

### **Task 3.1: Remove AI Optimize Button & Add Calibrate Button** (30 minutes)
- [ ] Find and remove "AI Optimize" button from backtest results
- [ ] Add "Calibrate from Backtest" button
- [ ] Wire button to trigger calibration API call
- [ ] Show loading state during analysis
- **Files to modify:**
  - Backtest results component (need to locate)

### **Task 3.2: Create CalibrationModal Component** (60 minutes)
- [ ] Create modal component structure
- [ ] Display backtest summary (trades, win rate, return, Sharpe)
- [ ] List recommendations with parameter, current, recommended values
- [ ] Show AI reasoning for each recommendation
- [ ] Display confidence scores
- [ ] Add Apply/Reject buttons per recommendation
- [ ] Add "Apply All" and "Reject All" buttons
- **Files to create:**
  - `/frontend/components/CalibrationModal.tsx` or similar

### **Task 3.3: Wire Backend API Endpoints** (30 minutes)
- [ ] Create `/api/calibration/backtest` endpoint
- [ ] Accept backtest metrics + current config
- [ ] Call CalibrationEngine.generate_recommendations()
- [ ] Return recommendations array
- [ ] Handle errors gracefully
- **Files to create:**
  - Backend API endpoint (FastAPI route)

### **Task 3.4: Apply Recommendations to Config** (30 minutes)
- [ ] Update Strategic Config state when user clicks "Apply"
- [ ] Show before/after comparison
- [ ] Mark recommendations as applied in database
- [ ] Trigger config save
- [ ] Show success feedback
- **Files to modify:**
  - Strategic Config component/state management

### **Task 3.5: Testing & Polish** (30 minutes)
- [ ] Test full user flow: backtest → calibrate → apply → re-run
- [ ] Verify config updates correctly
- [ ] Check database records recommendations
- [ ] Add loading states and error handling
- [ ] Polish UI/UX

---

## 🎯 Acceptance Criteria

**Phase 3 is complete when:**
1. ✅ "AI Optimize" button removed from UI
2. ✅ "Calibrate from Backtest" button appears after backtest completes
3. ✅ Clicking button triggers calibration analysis
4. ✅ CalibrationModal displays:
   - Backtest summary metrics
   - 1-5 recommendations with reasoning
   - Apply/Reject actions per recommendation
5. ✅ Applying recommendations updates Strategic Config
6. ✅ Applied recommendations saved to database
7. ✅ User can re-run backtest with new config

---

## 📊 Progress Tracking

| Task | Status | Time Spent | Notes |
|------|--------|------------|-------|
| 3.1: Remove AI Optimize, Add Calibrate Button | ⏳ Pending | 0h | Need to locate backtest UI |
| 3.2: Create CalibrationModal | ⏳ Pending | 0h | Main UI component |
| 3.3: Wire Backend API | ⏳ Pending | 0h | FastAPI endpoint |
| 3.4: Apply Recommendations | ⏳ Pending | 0h | Config state updates |
| 3.5: Testing & Polish | ⏳ Pending | 0h | End-to-end validation |
| **TOTAL** | **0%** | **0h / 2-3h** | Ready to start |

---

## 📝 Update Log

**March 5, 2026, 9:15 PM:**
- Phase 3 started
- Tracker document created
- Phase 2 complete, backend ready
- Ready to begin Task 3.1

---

## 📚 Related Documents

- **Master Plan:** `/docs/implementation/BACKTEST-CALIBRATION-SYSTEM.md`
- **Phase 2 Complete:** `/docs/implementation/PHASE-2-COMPLETE.md`
- **Backend API:** CalibrationEngine in `/backend/services/calibration_engine.py`
- **Next Phase:** Phase 4 - Performance Dashboard

---

**Ready to start Task 3.1: Locate backtest UI and add Calibrate button**
