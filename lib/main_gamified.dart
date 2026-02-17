import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'core/config/supabase_config.dart';
import 'widgets/gamification/gamification_overlay.dart';
import 'widgets/gamification/components/level_up_celebration.dart';
import 'providers/gamification_provider.dart';
import 'screens/enhanced_question_screen.dart';

/// 🚀 GAMIFIED LOKAAH APP
/// Showcases stunning gamification features

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: SupabaseConfig.supabaseUrl,
    anonKey: SupabaseConfig.supabaseAnonKey,
  );

  runApp(
    ProviderScope(
      child: GamifiedLokaahApp(),
    ),
  );
}

class GamifiedLokaahApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LOKAAH - Gamified',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      home: const GamifiedHomeScreen(),
    );
  }
}

class GamifiedHomeScreen extends ConsumerStatefulWidget {
  const GamifiedHomeScreen({Key? key}) : super(key: key);

  @override
  _GamifiedHomeScreenState createState() => _GamifiedHomeScreenState();
}

class _GamifiedHomeScreenState extends ConsumerState<GamifiedHomeScreen> {
  @override
  Widget build(BuildContext context) {
    return GamificationOverlay(
      child: Scaffold(
        body: Stack(
          children: [
            // Main content (pushed down for XP bar)
            Padding(
              padding: const EdgeInsets.only(top: 80),
              child: _buildMainContent(),
            ),
            
            // Gamification FAB
            Positioned(
              right: 16,
              bottom: 100,
              child: FloatingActionButton.extended(
                onPressed: () => _showGamificationPanel(),
                backgroundColor: Colors.purple,
                icon: const Icon(Icons.emoji_events, color: Colors.white),
                label: Consumer(
                  builder: (context, ref, child) {
                    final level = ref.watch(currentLevelProvider);
                    return Text(
                      'Lvl $level',
                      style: const TextStyle(color: Colors.white),
                    );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMainContent() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '🎯 Practice Mathematics',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Master CBSE Class 10 with AI-powered learning',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade600,
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Quick actions
            Row(
              children: [
                Expanded(
                  child: _buildActionCard(
                    icon: '📐',
                    title: 'Trigonometry',
                    subtitle: 'Heights & Distances',
                    color: Colors.blue,
                    onTap: () => _startPractice('trigonometry'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionCard(
                    icon: '📊',
                    title: 'Algebra',
                    subtitle: 'Quadratic Equations',
                    color: Colors.purple,
                    onTap: () => _startPractice('algebra'),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            Row(
              children: [
                Expanded(
                  child: _buildActionCard(
                    icon: '📏',
                    title: 'Geometry',
                    subtitle: 'Triangles & Circles',
                    color: Colors.green,
                    onTap: () => _startPractice('geometry'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionCard(
                    icon: '🎲',
                    title: 'Probability',
                    subtitle: 'Chance & Statistics',
                    color: Colors.orange,
                    onTap: () => _startPractice('probability'),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 32),
            
            // Test celebrations
            const Text(
              '🎮 Test Gamification',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            
            const SizedBox(height: 12),
            
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _testXPGain(),
                    icon: const Icon(Icons.add),
                    label: const Text('Gain XP'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _testLevelUp(),
                    icon: const Icon(Icons.upgrade),
                    label: const Text('Level Up'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.purple,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _testBadge(),
                    icon: const Icon(Icons.emoji_events),
                    label: const Text('Badge'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard({
    required String icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              color.withOpacity(0.1),
              color.withOpacity(0.05),
            ],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(icon, style: const TextStyle(fontSize: 32)),
            const SizedBox(height: 12),
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _startPractice(String concept) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EnhancedQuestionScreen(
          onLoadQuestion: () async {
            // Mock question - replace with actual API
            await Future.delayed(const Duration(seconds: 2));
            return GeneratedQuestion(
              id: 'mock_$concept',
              text: 'Sample $concept question for testing gamification...',
              difficulty: 'medium',
              marks: 3,
              concept: concept,
              source: 'ai',
              conceptTags: [concept],
              answerType: 'numeric',
              correctAnswer: 42,
              solutionSteps: ['Step 1', 'Step 2', 'Step 3'],
              finalAnswer: '42',
              socraticHints: [
                {'hint': 'Think about the formula', 'nudge': 'Recall basic principles'},
              ],
            );
          },
          concept: concept,
        ),
      ),
    );
  }

  void _showGamificationPanel() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const GamificationBottomSheet(),
    );
  }

  void _testXPGain() {
    ref.read(gamificationProvider.notifier).addCorrectAnswer(
      concept: 'test',
      difficulty: 2,
      attempts: 1,
      timeSeconds: 45,
    );
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('✨ +35 XP gained!'),
        duration: Duration(seconds: 1),
        backgroundColor: Colors.green,
      ),
    );
  }

  void _testLevelUp() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => LevelUpCelebration(
        newLevel: 5,
        xpGained: 150,
        onComplete: () => Navigator.pop(context),
      ),
    );
  }

  void _testBadge() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => BadgeUnlockCelebration(
        badgeName: 'Speed Demon',
        badgeEmoji: '⚡',
        badgeDescription: 'Solve 5 questions in under 60 seconds',
        onComplete: () => Navigator.pop(context),
      ),
    );
  }
}

/// Mock for GeneratedQuestion
class GeneratedQuestion {
  final String id;
  final String text;
  final String difficulty;
  final int marks;
  final String concept;
  final String source;
  final List<String> conceptTags;
  final String? jsxGraphCode;
  final String answerType;
  final dynamic correctAnswer;
  final List<String> solutionSteps;
  final String finalAnswer;
  final List<Map<String, String>> socraticHints;

  GeneratedQuestion({
    required this.id,
    required this.text,
    required this.difficulty,
    required this.marks,
    required this.concept,
    required this.source,
    required this.conceptTags,
    this.jsxGraphCode,
    required this.answerType,
    required this.correctAnswer,
    required this.solutionSteps,
    required this.finalAnswer,
    required this.socraticHints,
  });
}

/// Placeholder - import from actual file
class GamificationBottomSheet extends StatelessWidget {
  const GamificationBottomSheet({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
      ),
      child: const Center(child: Text('Gamification Panel')),
    );
  }
}
