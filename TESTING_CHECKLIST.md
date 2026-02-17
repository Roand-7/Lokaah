# 🧪 LOKAAH Platform Testing Checklist
**Complete Test Suite for User Experience Validation**

---

## 📋 How to Use This Checklist

1. Open your web app: http://localhost:5500 (or your frontend URL)
2. Start a new session (refresh the page)
3. Go through each test scenario below
4. Check if the response matches expectations
5. Mark ✅ if correct, ❌ if needs fixing

---

## 1️⃣ GREETING & ONBOARDING

### Test 1.1: First Contact
**You say:** `hello`

**Expected Agent:** 🧠 VEDA (blue)

**Expected Response:**
- Warm greeting in Hinglish: "Hey dost!" or "Namaste!"
- Introduces herself as VEDA
- Asks what you want to learn or which chapter
- Friendly, conversational tone

**Example Response:**
> "Hey dost! VEDA here — ready to make math simple for you? Kaunsa chapter kar rahe ho?"

**Verify:**
- ✅ Agent name shows "VEDA"
- ✅ Blue color avatar
- ✅ No debug info visible (no "route_confidence" or "source: pattern")
- ✅ Uses casual language (not robotic)

---

### Test 1.2: Morning Greeting (Session Continuity)
**You say:** `good morning`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Acknowledges the greeting
- Continues conversation naturally (doesn't say "I'm closing session")
- May reference previous context if this is a returning session

**Verify:**
- ✅ VEDA responds (NOT Atlas with "session closed")
- ✅ Session continues (can send more messages)
- ✅ Friendly tone

---

### Test 1.3: Who Are You?
**You say:** `who are you?`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Explains she's VEDA, an AI tutor for board exams
- Mentions her teaching style (Socratic, visual, personalized)
- Invites you to start learning

**Verify:**
- ✅ Clear explanation of VEDA's role
- ✅ Encouraging tone
- ✅ Offers to help

---

## 2️⃣ TEACHING MODE (VEDA)

### Test 2.1: Concept Explanation
**You say:** `explain pythagoras theorem`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Real-world hook (e.g., "Imagine a ladder against a wall...")
- Visual explanation with relatable examples
- Socratic questions to check understanding
- NOT dry textbook definitions
- May offer to show diagram or JSXGraph visualization

**Verify:**
- ✅ Starts with relatable scenario
- ✅ Asks questions to engage you
- ✅ Conversational, not lecture-style
- ✅ Offers visual aids if appropriate

**Example Response:**
> "Dost, imagine you're setting up a ladder to reach your roof. The ladder leans against the wall at an angle. Now, there's a magical relationship between three lengths here: the ladder's length, the distance from the wall, and the height it reaches. Want to guess what that relationship might be?"

---

### Test 2.2: Follow-Up Question
**You say:** `can you show me an example?`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Provides concrete example with numbers
- Walks through step-by-step
- Checks understanding along the way
- Maintains conversational tone

**Verify:**
- ✅ Clear example with actual numbers
- ✅ Step-by-step breakdown
- ✅ Context from previous message maintained

---

### Test 2.3: Confused Student
**You say:** `i'm confused about this`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Empathetic acknowledgment ("No worries, let's break it down")
- Offers to restart with simpler explanation
- Asks what specifically is confusing
- Encouraging, not judgmental

**Verify:**
- ✅ Empathetic response
- ✅ Offers different approach
- ✅ Patient tone

---

## 3️⃣ PRACTICE MODE (ORACLE)

### Test 3.1: Slash Command Practice
**You say:** `/test`

**Expected Agent:** 🔮 ORACLE (purple/teal)

**Expected Response:**
- Presents a practice question
- Shows marks (e.g., "[3 marks]" or mentions difficulty)
- Natural intro like "Let's try this one" (NOT "Challenge accepted. High-focus mode ON.")
- Question is clear and complete
- Invites you to solve it

**Verify:**
- ✅ Oracle agent responds
- ✅ Question is clearly formatted
- ✅ Natural language intro (not template)
- ✅ No debug data like "source: pattern", "question_id: PAT_123"

---

### Test 3.2: Practice Request
**You say:** `give me a practice question on trigonometry`

**Expected Agent:** 🔮 ORACLE

**Expected Response:**
- Generates trigonometry question
- Appropriate difficulty level
- Shows marks/points
- Clear problem statement

**Verify:**
- ✅ Question topic matches request (trigonometry)
- ✅ Mathematical notation is readable
- ✅ Natural conversational wrapper

---

### Test 3.3: Answer Submission
**You say:** `45 degrees` (or any answer)

**Expected Agent:** 🔮 ORACLE or 🧠 VEDA

**Expected Response:**
- Evaluates your answer (correct/incorrect)
- Provides feedback
- If wrong: offers hints or explanation
- If correct: encouragement + offers next question

**Verify:**
- ✅ Answer is evaluated
- ✅ Constructive feedback
- ✅ Natural response (not just "Correct" or "Wrong")

---

## 4️⃣ CHALLENGE MODE (SPARK)

### Test 4.1: Slash Command Challenge
**You say:** `/spark`

**Expected Agent:** ⚡ SPARK (red/orange)

**Expected Response:**
- High-energy intro ("Alright, let's push your limits!")
- Harder question than Oracle
- Motivating tone
- Clear problem statement

**Verify:**
- ✅ Spark agent responds
- ✅ Energetic, challenging tone
- ✅ Question is more complex
- ✅ Natural language (not "High-focus mode ON")

---

### Test 4.2: Challenge Request
**You say:** `give me a hard question`

**Expected Agent:** ⚡ SPARK

**Expected Response:**
- Difficult question (5-mark level)
- Challenging but fair
- Encouraging preamble
- High confidence in your ability

**Verify:**
- ✅ Spark responds (not Oracle)
- ✅ Question is genuinely harder
- ✅ Motivating tone

---

## 5️⃣ PLANNING MODE (ATLAS)

### Test 5.1: Slash Command Plan
**You say:** `/plan`

**Expected Agent:** 🗺️ ATLAS (teal/green)

**Expected Response:**
- Shows your study schedule/exam timeline
- Conversational format ("Here's your game plan...")
- NOT bullet list with dashes ("- Day 1: Algebra revision")
- Motivational tone
- Offers to customize or break down

**Verify:**
- ✅ Atlas agent responds
- ✅ Natural conversational format
- ✅ Shows exam timeline if available
- ✅ No robotic bullet lists

**Example Response:**
> "Looking at your exam window (March 2026), here's what I recommend: Monday we'll tackle Algebra for about 60m, then Tuesday focuses on Geometry practice for 45m. Want me to break this down into a daily checklist?"

---

### Test 5.2: Schedule Query
**You say:** `when is my exam?`

**Expected Agent:** 🗺️ ATLAS

**Expected Response:**
- Tells you exam date/window
- May suggest study timeline
- Conversational tone

**Verify:**
- ✅ Atlas responds
- ✅ Provides date information
- ✅ Natural language

---

## 6️⃣ WELLBEING MODE (PULSE)

### Test 6.1: Slash Command Calm
**You say:** `/chill`

**Expected Agent:** 💚 PULSE (green)

**Expected Response:**
- Calming, supportive tone
- May suggest breathing exercises or short break
- Acknowledges stress
- Offers perspective

**Verify:**
- ✅ Pulse agent responds
- ✅ Empathetic tone
- ✅ Practical suggestions

---

### Test 6.2: Stress Expression
**You say:** `i'm so stressed about this exam`

**Expected Agent:** 💚 PULSE

**Expected Response:**
- Validates feelings ("It's totally normal to feel stressed")
- Offers coping strategies
- Reframes perspective
- Encourages without dismissing concerns

**Verify:**
- ✅ Pulse responds (not VEDA)
- ✅ Acknowledges emotions
- ✅ Practical advice given

---

## 7️⃣ CONVERSATION FLOW

### Test 7.1: Thank You (Critical!)
**You say:** `thank you`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Acknowledges thanks
- Conversation CONTINUES (does NOT end session)
- May ask what's next or offer more help
- Friendly response

**Verify:**
- ✅ VEDA responds (NOT Atlas with "session closed")
- ✅ Session continues (can send more messages)
- ✅ No "I've closed this session" message

**This was the bug from your screenshots - now fixed!**

---

### Test 7.2: Thanks After Learning
**You say:** `thanks, that helped`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Positive acknowledgment
- Offers next steps
- Session continues

**Verify:**
- ✅ VEDA responds
- ✅ No session closure
- ✅ Natural continuation

---

### Test 7.3: Context Memory
**Sequence:**
1. **You say:** `explain quadratic equations`
2. **VEDA explains**
3. **You say:** `can you give me an example?` (no context in the message)

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Provides example OF QUADRATIC EQUATIONS (not something random)
- Shows context is maintained
- Directly answers without asking "example of what?"

**Verify:**
- ✅ Understands "example" refers to quadratic equations
- ✅ Context maintained across messages
- ✅ Relevant example provided

---

### Test 7.4: Multiple Interactions in One Session
**Sequence:**
1. `hello` → VEDA greets
2. `explain pythagoras` → VEDA teaches
3. `give me a question` → ORACLE provides practice
4. `who are you?` → VEDA responds (not new onboarding)
5. `thank you` → VEDA acknowledges, session continues

**Verify:**
- ✅ All messages in same session (session_id consistent)
- ✅ Context flows naturally
- ✅ No duplicate introductions
- ✅ No premature session closures

---

## 8️⃣ SESSION CLOSURE

### Test 8.1: Explicit Goodbye
**You say:** `bye`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Friendly goodbye message
- Mentions progress is saved
- Invites return: "Come back anytime"
- Warm tone, not abrupt

**Verify:**
- ✅ VEDA says goodbye (not Atlas)
- ✅ Mentions progress saved
- ✅ Friendly closing

**Example Response:**
> "Take care! Your progress is saved. Message me anytime you're ready to continue — I'll remember where we left off. 😊"

---

### Test 8.2: That's All
**You say:** `that's all for now`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Acknowledges completion
- Friendly closure
- Session ends properly

**Verify:**
- ✅ Session closes appropriately
- ✅ Natural goodbye message

---

## 9️⃣ ERROR HANDLING

### Test 9.1: Gibberish Input
**You say:** `asdfghjkl`

**Expected Agent:** 🧠 VEDA (default)

**Expected Response:**
- Politely asks for clarification
- Offers examples of what you can ask
- NOT raw error messages or stack traces
- Friendly tone

**Verify:**
- ✅ No error 500
- ✅ No stack traces shown
- ✅ Helpful response

---

### Test 9.2: Complex LaTeX
**You say:** `explain $$\frac{d}{dx}(x^2) = 2x$$`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- LaTeX renders correctly (not raw code)
- Explains the calculus concept
- Mathematical notation is readable

**Verify:**
- ✅ Math symbols render properly
- ✅ Response includes proper notation
- ✅ Explanation is clear

---

## 🔟 PERSONALIZATION

### Test 10.1: Vernacular Detection (Hinglish)
**You say:** `bhai, quadratic equations samjha do`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Responds in Hinglish style
- Uses "dost", "bhai", casual language
- Maintains teaching quality
- Code-switching is natural

**Verify:**
- ✅ Response uses Hinglish
- ✅ Not pure formal English
- ✅ Natural code-switching

---

### Test 10.2: Formal English Request
**You say:** `Could you please explain the concept of derivatives?`

**Expected Agent:** 🧠 VEDA

**Expected Response:**
- Matches formality level (slightly formal but still friendly)
- Clear explanation
- May adapt language style

**Verify:**
- ✅ Appropriate formality
- ✅ Still engaging, not robotic
- ✅ Clear explanation

---

## ✅ SUCCESS CRITERIA SUMMARY

Your platform is working correctly if:

### Routing ✅
- [x] Casual greetings (hello, thanks) route to VEDA
- [x] Teaching requests route to VEDA
- [x] Practice requests route to ORACLE
- [x] Challenge requests route to SPARK
- [x] Planning requests route to ATLAS
- [x] Stress/anxiety routes to PULSE
- [x] Only explicit goodbyes (bye, goodbye, that's all) end session

### Agent Personalities ✅
- [x] VEDA: Warm, Socratic, uses vernacular
- [x] ORACLE: Encouraging, practice-focused
- [x] SPARK: High-energy, challenging
- [x] ATLAS: Strategic, planning-focused
- [x] PULSE: Empathetic, calming

### User Experience ✅
- [x] No premature session closures
- [x] Context maintained across messages
- [x] Natural conversation flow
- [x] No debug data visible (unless DEBUG=true)
- [x] Error messages are friendly (no stack traces)
- [x] Math notation renders correctly
- [x] Responses are conversational (not templates)

### Technical ✅
- [x] Session IDs persist correctly
- [x] No 404/500 errors
- [x] Response time < 5 seconds
- [x] LaTeX/KaTeX renders properly
- [x] Frontend displays agent colors/emojis correctly

---

## 🎯 Quick 5-Minute Smoke Test

If you're short on time, test these 5 scenarios:

1. **Hello Test:** Say "hello" → Should get VEDA greeting ✅
2. **Thank You Test:** Say "thank you" → Should NOT close session ✅
3. **Practice Test:** Say "/test" → Should get Oracle practice question ✅
4. **Context Test:** Ask "explain X" then "give example" → Should remember X ✅
5. **Goodbye Test:** Say "bye" → Should close session with VEDA goodbye ✅

If all 5 pass, your platform is working well! 🎉

---

## 📊 Tracking Your Tests

Use this simple format in your notes:

```
Test Date: 2026-02-16
Session ID: [copy from browser console]

✅ Test 1.1: Greeting - PASSED
✅ Test 7.1: Thank You - PASSED (was broken, now fixed!)
✅ Test 3.1: Practice - PASSED
❌ Test 5.1: Planning - NEEDS FIX (still showing bullet lists)
✅ Test 8.1: Goodbye - PASSED

Overall: 4/5 scenarios working correctly
```

---

## 🚀 Next Steps After Testing

1. **If all tests pass:** You're ready for production! 🎉
2. **If some tests fail:** Check [ARCHITECTURE_AUDIT_REPORT.md](ARCHITECTURE_AUDIT_REPORT.md) for fixes
3. **For streaming:** Implement [STREAMING_IMPLEMENTATION_GUIDE.md](STREAMING_IMPLEMENTATION_GUIDE.md)
4. **For polish:** Apply [QUICK_FLUIDITY_FIXES.md](QUICK_FLUIDITY_FIXES.md)

---

**Happy Testing!** 🧪✨

If you find issues, refer to the documentation files we created or let me know!
