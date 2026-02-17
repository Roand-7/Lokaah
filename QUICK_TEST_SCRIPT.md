# 🎯 Quick Test Script - Copy & Paste
**Fast testing sequence - copy each question and paste into your chat**

---

## SECTION 1: BASIC ROUTING (5 tests - 2 minutes)

```
hello
```
**Expected:** 🧠 VEDA greets you warmly

```
thank you
```
**Expected:** 🧠 VEDA responds, session CONTINUES (not closes!)

```
explain pythagoras theorem
```
**Expected:** 🧠 VEDA teaches with real-world examples

```
/test
```
**Expected:** 🔮 ORACLE gives practice question

```
bye
```
**Expected:** 🧠 VEDA says goodbye, session ends

---

## SECTION 2: AGENT ROUTING (7 tests - 3 minutes)

```
hello
```
→ 🧠 VEDA

```
give me a practice question on trigonometry
```
→ 🔮 ORACLE

```
give me a hard question
```
→ ⚡ SPARK

```
when is my exam?
```
→ 🗺️ ATLAS

```
i'm so stressed about this exam
```
→ 💚 PULSE

```
who are you?
```
→ 🧠 VEDA

```
good morning
```
→ 🧠 VEDA (continues conversation)

---

## SECTION 3: CONTEXT MEMORY (4 tests - 3 minutes)

```
explain quadratic equations
```
→ 🧠 VEDA explains

```
can you give me an example?
```
→ 🧠 VEDA gives example of QUADRATIC EQUATIONS (remembers context!)

```
show me another one
```
→ 🧠 VEDA gives another quadratic example (still remembers!)

```
thank you
```
→ 🧠 VEDA responds, session stays open

---

## SECTION 4: CONVERSATION FLOW (6 tests - 3 minutes)

```
hi
```
→ 🧠 VEDA

```
explain sin cos tan
```
→ 🧠 VEDA

```
give me a practice question
```
→ 🔮 ORACLE

```
thanks
```
→ 🧠 VEDA (NO session close!)

```
what else can you help with?
```
→ 🧠 VEDA

```
goodbye
```
→ 🧠 VEDA closes session

---

## SECTION 5: SLASH COMMANDS (6 tests - 2 minutes)

```
/veda
```
→ 🧠 VEDA responds

```
/test
```
→ 🔮 ORACLE gives question

```
/spark
```
→ ⚡ SPARK gives hard question

```
/plan
```
→ 🗺️ ATLAS shows schedule

```
/chill
```
→ 💚 PULSE calming message

```
/bye
```
→ 🧠 VEDA goodbye

---

## SECTION 6: EDGE CASES (4 tests - 2 minutes)

```
asdfghjkl
```
→ 🧠 VEDA asks for clarification (no error!)

```
what is $$\frac{1}{2}$$
```
→ Math renders correctly

```
bhai, help karo na
```
→ 🧠 VEDA responds in Hinglish

```
namaste
```
→ 🧠 VEDA responds (doesn't close session!)

---

## ✅ PASS/FAIL CHECKLIST

**Critical Tests (Must Pass):**
- [ ] "hello" → VEDA greets
- [ ] "thank you" → Session continues (NOT closes!)
- [ ] "/test" → ORACLE gives question
- [ ] Context memory works (example follows topic)
- [ ] "bye" → Session ends properly

**Important Tests (Should Pass):**
- [ ] "give me a hard question" → SPARK responds
- [ ] "i'm stressed" → PULSE responds
- [ ] "when is my exam" → ATLAS responds
- [ ] "good morning" → VEDA continues (no close)
- [ ] Math notation renders correctly

**Nice to Have:**
- [ ] Hinglish detection works
- [ ] Multiple agent switches in one session
- [ ] No debug data visible
- [ ] Responses are natural (not templated)

---

## 🚨 RED FLAGS - Stop Testing if You See:

❌ "Great effort today! I've closed this session" after "thank you"
❌ "source: pattern" or "question_id: PAT_123" visible
❌ Stack traces or error 500
❌ "route_confidence: 0.923" visible
❌ "[3 marks | source: pattern]" format
❌ "Challenge accepted. High-focus mode ON." template

---

## ✅ WHAT GOOD LOOKS LIKE:

✅ Natural conversation flow
✅ Context maintained across messages  
✅ "Thank you" continues session
✅ Agent switches happen smoothly
✅ No technical jargon visible
✅ Responses feel like a real tutor

---

## 📊 TEST RESULTS TEMPLATE

Copy this to track your results:

```
=== LOKAAH TEST RESULTS ===
Date: 2026-02-16
Tester: [Your Name]

BASIC ROUTING:
✅ Hello → VEDA
✅ Thank You → VEDA (continues) 
✅ Explain → VEDA teaches
✅ /test → ORACLE
✅ Bye → Closes properly

AGENT ROUTING:
✅ Practice → ORACLE
✅ Hard question → SPARK
✅ Exam date → ATLAS
✅ Stressed → PULSE

CONTEXT MEMORY:
✅ Follow-up questions work
✅ "Give example" remembers topic

CRITICAL FIXES:
✅ "thank you" DOESN'T close session (FIXED!)
✅ No premature "session closed" messages

OVERALL: [X/20] tests passed

READY FOR PRODUCTION: [YES / NO / NEEDS WORK]

NOTES:
- [Any issues found]
- [Things working great]
```

---

## 🎬 DEMO SCRIPT (For Showcasing)

Perfect sequence to demonstrate the platform:

1. **Hello** → Warm VEDA greeting
2. **Explain quadratic equations** → VEDA teaches concept
3. **Give me an example** → VEDA provides example (context!)
4. **Give me a practice question** → ORACLE appears
5. **[Answer something]** → Gets feedback
6. **Thank you** → VEDA acknowledges, continues
7. **I'm stressed** → PULSE takes over with support
8. **When is my exam?** → ATLAS shows plan
9. **Give me a hard challenge** → SPARK brings intensity
10. **Good morning** → Back to VEDA naturally
11. **Goodbye** → Clean session close

**Demo Time:** ~5 minutes  
**Shows:** All 5 agents, context memory, natural flow, fixed "thank you" bug

---

**Total Testing Time:** ~15 minutes for complete validation
**Quick Test:** ~5 minutes for smoke test (Section 1 only)

Good luck! 🚀
