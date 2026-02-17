# 🚀 Quick Start Guide - Enable JSXGraph Visuals

**Goal:** Get JSXGraph visuals working in 10 minutes

---

## Step 1: Get FREE Gemini API Key (2 minutes)

1. Visit: https://aistudio.google.com/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AI...`)

**Free Tier:**
- ✅ 15 requests/minute
- ✅ Perfect for development
- ✅ No credit card needed

---

## Step 2: Set Environment Variable (1 minute)

### Windows PowerShell:
```powershell
# Temporary (current session only)
$env:GEMINI_API_KEY = "your-api-key-here"

# Permanent (recommended)
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-api-key-here", "User")
```

### Windows CMD:
```cmd
setx GEMINI_API_KEY "your-api-key-here"
```

**Important:** Close and reopen PowerShell after setting permanent variable

---

## Step 3: Verify Backend Works (2 minutes)

```bash
cd C:\Users\Lenovo\lokaah_app
python verify_jsxgraph_integration.py
```

**Expected Output:**
```
✅ PASS - Backend Generation
✅ PASS - Hybrid Orchestrator
✅ PASS - Visual Concepts
✅ PASS - Flutter Compatibility
✅ PASS - VEDA Integration
✅ PASS - Asset Configuration

Final Score: 6/6 tests passed
🎉 ALL TESTS PASSED - PRODUCTION READY!
```

---

## Step 4: Test JSXGraph Generation (3 minutes)

Create test file `test_jsx_visual.py`:

```python
from app.oracle.true_ai_oracle import TrueAIOracle

# Initialize
oracle = TrueAIOracle()

# Generate visual question
result = oracle.generate_question(
    concept="trigonometry_heights",
    marks=3,
    difficulty=0.6
)

print("=" * 60)
print("QUESTION:")
print(result.question_text)
print("\nANSWER:")
print(result.final_answer)
print("\nJSXGRAPH CODE:")
print(result.jsxgraph_code[:500] if result.jsxgraph_code else "No JSXGraph")
print("=" * 60)
```

Run it:
```bash
python test_jsx_visual.py
```

**Expected:** See JSXGraph JavaScript code generated!

---

## Step 5: Test in Flutter (2 minutes)

### Option A: Hardcoded Test (No Backend Needed)

In QuestionScreen or any page:

```dart
import 'package:lokaah_app/widgets/jsxgraph_viewer.dart';

// ...inside build method:

JSXGraphViewer(
  jsxCode: '''
    // Simple triangle
    var A = board.create('point', [0, 0], {name: 'A', size: 4});
    var B = board.create('point', [4, 0], {name: 'B', size: 4});
    var C = board.create('point', [2, 3], {name: 'C', size: 4});
    
    board.create('polygon', [A, B, C], {
      fillColor: 'blue',
      fillOpacity: 0.3
    });
    
    board.create('text', [2, -0.5, 'Find the area'], {fontSize: 16});
  ''',
  boundingBox: [-1, 4, 5, -2],
  showAxis: true,
  showGrid: true,
  onInteraction: (data) {
    print('Student interaction: $data');
  },
  onReady: () {
    print('✅ JSXGraph loaded!');
  },
)
```

Run Flutter:
```bash
flutter run
```

**Expected:** See interactive triangle in app!

### Option B: Connect to Backend (Full Flow)

1. Start FastAPI backend:
```bash
cd C:\Users\Lenovo\lokaah_app
python -m uvicorn app.api.routes:app --reload
```

2. In Flutter, create API service:
```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<Map<String, dynamic>> getQuestion() async {
  final response = await http.post(
    Uri.parse('http://localhost:8000/oracle/generate'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'concept': 'trigonometry_heights',
      'marks': 3,
      'difficulty': 0.6
    }),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to generate question');
  }
}
```

3. Use in widget:
```dart
ElevatedButton(
  onPressed: () async {
    final questionData = await getQuestion();
    
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => Scaffold(
          appBar: AppBar(title: Text('Practice Question')),
          body: Column(
            children: [
              Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  questionData['question_text'],
                  style: TextStyle(fontSize: 18),
                ),
              ),
              Expanded(
                child: JSXGraphViewer(
                  jsxCode: questionData['jsx_graph_code'],
                  boundingBox: questionData['graph_bounding_box']?.cast<double>(),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  },
  child: Text('Get AI Question with Visual'),
)
```

---

## 🎯 Success Checklist

After completing steps above, you should have:

- ✅ Environment variable set
- ✅ Verification script passes (6/6)
- ✅ Python test generates JSXGraph code
- ✅ Flutter shows interactive diagram
- ✅ Touch/click interactions work on graph

---

## 🐛 Troubleshooting

### API Key Not Working
```bash
# Verify it's set
echo $env:GEMINI_API_KEY  # PowerShell
echo %GEMINI_API_KEY%     # CMD

# Test directly
python -c "import os; print('Key:', os.getenv('GEMINI_API_KEY'))"
```

### Import Errors
```bash
# Ensure you're in correct directory
cd C:\Users\Lenovo\lokaah_app

# Verify Python path
python -c "import sys; print('\\n'.join(sys.path))"
```

### Flutter WebView Not Loading
```dart
// Check pubspec.yaml has:
dependencies:
  webview_flutter: ^4.4.2
  webview_flutter_android: ^3.13.0
  webview_flutter_wkwebview: ^3.10.0

// Then:
flutter pub get
flutter clean
flutter run
```

### CORS Error (Backend Connection)
```python
# Add to app/api/routes.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 💡 Next Steps After Success

1. **Generate 10 questions** and review quality
2. **Test different concepts** (geometry, algebra, trigonometry)
3. **Measure generation time** (should be 2-5 seconds)
4. **Test on physical Android/iOS device**
5. **Show to beta users** for feedback

---

## 📊 Cost Monitoring

Track your API usage:

```python
from app.oracle.hybrid_orchestrator import HybridOrchestrator

orchestrator = HybridOrchestrator(ai_ratio=0.5)  # 50% AI

# Generate some questions
for i in range(100):
    orchestrator.generate_question("math", 3, 0.5)

# Check costs
stats = orchestrator.get_stats()
print(f"AI calls: {stats['ai_count']}")
print(f"Est. cost: ${stats.get('estimated_api_cost_usd', 0):.4f}")
```

**Gemini Pricing:**
- Input: ~$0.10 per 1M tokens
- Output: ~$0.40 per 1M tokens
- Average question: ~1000 tokens in/out
- **~$0.0005 per question** ($0.50 per 1000 questions)

---

## 🎓 Example Output

**Question Generated:**
```
Rajesh flies a kite at India Gate in Delhi. The string is 50 meters long 
and makes an angle of 60° with the ground. If Rajesh is holding the string 
at a height of 1.5 meters above the ground, find:
(a) The height of the kite from the ground
(b) The horizontal distance from Rajesh to the point directly below the kite
```

**JSXGraph Code Generated:**
```javascript
var ground = board.create('line', [[0,0], [10,0]], {
  strokeColor: '#8B4513',
  strokeWidth: 2,
  name: 'Ground'
});

var R = board.create('point', [1, 1.5], {
  name: 'Rajesh',
  size: 4,
  color: 'blue'
});

var K = board.create('point', [
  1 + 50 * Math.cos(60 * Math.PI / 180),
  1.5 + 50 * Math.sin(60 * Math.PI / 180)
], {
  name: 'Kite',
  size: 4,
  color: 'red'
});

board.create('segment', [R, K], {
  strokeColor: 'black',
  strokeWidth: 2,
  dash: 2,
  name: 'String (50m)'
});

// ... more diagram elements
```

**Result:** Beautiful interactive diagram in Flutter!

---

## 🎉 You're Done!

**Congratulations!** You now have:
- 🧠 AI generating unique math questions
- 📐 Interactive JSXGraph visualizations
- 📱 Flutter app rendering them beautifully
- 💰 Cost-optimized hybrid system

**Ready to revolutionize CBSE math! 🚀**

---

**Questions?** 
- Check [JSXGRAPH_VERIFICATION_REPORT.md](./JSXGRAPH_VERIFICATION_REPORT.md)
- Run `python verify_jsxgraph_integration.py`
- Test specific features with `python test_jsx_visual.py`
