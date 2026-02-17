import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/generated_question.dart';
import '../widgets/jsxgraph_viewer.dart';
import '../widgets/gamification/xp_bar.dart';
import '../widgets/veda_thinking_loader.dart';
import '../providers/gamification_provider.dart';
import '../providers/learning_mode_provider.dart';

/// 🚀 ENHANCED QUESTION SCREEN
/// - Gamification integration
/// - Smart loading states
/// - Learning mode support
/// - Socratic fatigue prevention

class EnhancedQuestionScreen extends ConsumerStatefulWidget {
  final Future<GeneratedQuestion> Function() onLoadQuestion;
  final String concept;

  const EnhancedQuestionScreen({
    Key? key,
    required this.onLoadQuestion,
    required this.concept,
  }) : super(key: key);

  @override
  _EnhancedQuestionScreenState createState() => _EnhancedQuestionScreenState();
}

class _EnhancedQuestionScreenState extends ConsumerState<EnhancedQuestionScreen> {
  GeneratedQuestion? _question;
  bool _isLoading = true;
  bool _isSubmitting = false;
  String? _feedback;
  int _hintLevel = 0;
  int _attempts = 0;
  DateTime? _startTime;
  
  final TextEditingController _answerController = TextEditingController();
  final GlobalKey<JSXGraphViewerState> _graphKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    _startTime = DateTime.now();
    _loadQuestion();
  }

  Future<void> _loadQuestion() async {
    setState(() => _isLoading = true);
    
    try {
      final question = await widget.onLoadQuestion();
      setState(() {
        _question = question;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading question: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final learningMode = ref.watch(learningModeProvider);
    
    return Scaffold(
      body: Column(
        children: [
          // 🎮 Gamification Bar (Always visible)
          const XPProgressBar(),
          
          // Mode Indicator (if not socratic)
          if (learningMode.mode != LearningMode.socratic)
            _buildModeBanner(learningMode.mode),
          
          // Main Content
          Expanded(
            child: _isLoading
                ? SmartLoadingWrapper(
                    isAiQuestion: _question?.source == 'ai',
                    concept: widget.concept,
                    isLoading: true,
                    onLoadingComplete: () {}, // Handled by Future
                    child: const SizedBox.shrink(),
                  )
                : _buildQuestionContent(learningMode.mode),
          ),
        ],
      ),
    );
  }

  Widget _buildModeBanner(LearningMode mode) {
    final colors = {
      LearningMode.socratic: Colors.purple,
      LearningMode.guided: Colors.blue,
      LearningMode.direct: Colors.orange,
    };

    final icons = {
      LearningMode.socratic: Icons.psychology,
      LearningMode.guided: Icons.lightbulb_outline,
      LearningMode.direct: Icons.flash_on,
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: colors[mode]?.withOpacity(0.1),
      child: Row(
        children: [
          Icon(icons[mode], color: colors[mode], size: 18),
          const SizedBox(width: 8),
          Text(
            mode == LearningMode.direct 
                ? '⚡ Quick Mode: Direct solution available'
                : mode == LearningMode.guided
                    ? '💡 Guided Mode: Hints available'
                    : '🧠 Socratic Mode: Learning by discovery',
            style: TextStyle(
              color: colors[mode],
              fontWeight: FontWeight.w500,
              fontSize: 12,
            ),
          ),
          const Spacer(),
          TextButton(
            onPressed: () => _showModeSelector(),
            child: const Text('Change'),
          ),
        ],
      ),
    );
  }

  Widget _buildQuestionContent(LearningMode mode) {
    if (_question == null) return const SizedBox.shrink();

    return Column(
      children: [
        // Question Header
        _buildQuestionHeader(),
        
        // Question Text
        Expanded(
          flex: 2,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Text(
                  _question!.text,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontSize: 16,
                    height: 1.5,
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // JSXGraph Visualization
                if (_question!.jsxGraphCode != null)
                  Container(
                    height: 300,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: JSXGraphViewer(
                      key: _graphKey,
                      jsxCode: _question!.jsxGraphCode,
                    ),
                  ),
              ],
            ),
          ),
        ),
        
        // Hint Section (if socratic or guided)
        if (mode != LearningMode.direct && _hintLevel > 0)
          _buildHintCard(),
        
        // Solution Section (if direct mode or after 3 attempts)
        if ((mode == LearningMode.direct || _attempts >= 3) && _feedback != null)
          _buildSolutionCard(),
        
        // Answer Input
        _buildAnswerSection(mode),
      ],
    );
  }

  Widget _buildQuestionHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.grey.shade100,
      child: Row(
        children: [
          _buildBadge('${_question!.marks} marks', Colors.blue),
          const SizedBox(width: 8),
          _buildBadge(
            _question!.difficulty,
            _getDifficultyColor(_question!.difficulty),
          ),
          const SizedBox(width: 8),
          _buildBadge(
            _question!.source.toUpperCase(),
            _question!.source == 'ai' ? Colors.purple : Colors.green,
          ),
          const Spacer(),
          // Hint button (if socratic/guided)
          if (ref.read(learningModeProvider).mode != LearningMode.direct)
            IconButton(
              icon: const Icon(Icons.lightbulb_outline),
              onPressed: _showHint,
              tooltip: 'Get hint (${_hintLevel}/${_question?.socraticHints.length ?? 0})',
            ),
        ],
      ),
    );
  }

  Widget _buildBadge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        border: Border.all(color: color),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildHintCard() {
    final hints = _question?.socraticHints ?? [];
    if (_hintLevel > hints.length) return const SizedBox.shrink();

    final currentHint = hints[_hintLevel - 1];
    
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.amber.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.amber.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb, color: Colors.amber.shade700, size: 20),
              const SizedBox(width: 8),
              Text(
                'Hint $_hintLevel/${hints.length}',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.amber.shade900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            currentHint['hint'] ?? '',
            style: const TextStyle(fontSize: 14),
          ),
          if (currentHint['nudge'] != null) ...[
            const SizedBox(height: 8),
            Text(
              '💡 ${currentHint['nudge']}',
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSolutionCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green.shade300),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.school, color: Colors.green.shade700, size: 20),
              const SizedBox(width: 8),
              Text(
                'Solution',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.green.shade900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...(_question?.solutionSteps ?? []).asMap().entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: Colors.green.shade100,
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '${entry.key + 1}',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: Colors.green.shade700,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(entry.value),
                  ),
                ],
              ),
            );
          }).toList(),
          const Divider(),
          Text(
            'Answer: ${_question?.finalAnswer ?? ''}',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.green.shade900,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnswerSection(LearningMode mode) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        children: [
          // Show "Show Solution" button in direct mode immediately
          if (mode == LearningMode.direct && _feedback == null)
            ElevatedButton.icon(
              onPressed: () {
                setState(() {
                  _feedback = 'solution';
                  _attempts = 3; // Trigger solution display
                });
              },
              icon: const Icon(Icons.visibility),
              label: const Text('Show Solution'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 48),
              ),
            )
          else ...[
            TextField(
              controller: _answerController,
              decoration: InputDecoration(
                labelText: 'Your Answer',
                hintText: 'Enter your answer here',
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.edit),
                suffixIcon: _answerController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () => setState(() => _answerController.clear()),
                      )
                    : null,
              ),
              keyboardType: TextInputType.text,
              onChanged: (_) => setState(() {}),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submitAnswer,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF3498DB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text(
                        'Submit Answer',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
            ),
          ],
          
          // Skip button (if struggling)
          if (_attempts >= 2 && mode != LearningMode.direct)
            TextButton(
              onPressed: () {
                setState(() {
                  _feedback = 'skipped';
                  _attempts = 3;
                });
              },
              child: const Text('Skip to solution'),
            ),
        ],
      ),
    );
  }

  void _showHint() {
    setState(() {
      _hintLevel++;
    });
  }

  Future<void> _submitAnswer() async {
    if (_answerController.text.isEmpty) return;

    setState(() {
      _isSubmitting = true;
      _attempts++;
    });

    // Simulate API call
    await Future.delayed(const Duration(seconds: 1));

    // Mock correctness (replace with actual check)
    final isCorrect = _attempts == 1; // Mock
    final timeTaken = DateTime.now().difference(_startTime!).inSeconds;

    if (isCorrect) {
      // 🎉 Award XP!
      final result = await ref.read(gamificationProvider.notifier).addCorrectAnswer(
        concept: widget.concept,
        difficulty: _question?.marks ?? 1,
        attempts: _attempts,
        timeSeconds: timeTaken,
      );

      setState(() {
        _isSubmitting = false;
        _feedback = 'correct';
      });

      // Show XP popup
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => XPGainPopup(
            result: result,
            onComplete: () => Navigator.pop(context),
          ),
        );
      }
    } else {
      await ref.read(gamificationProvider.notifier).addIncorrectAnswer();
      
      setState(() {
        _isSubmitting = false;
        _feedback = 'incorrect';
      });

      // Auto-show hint after wrong answer
      final mode = ref.read(learningModeProvider).mode;
      if (mode == LearningMode.guided && _hintLevel < (_question?.socraticHints.length ?? 0)) {
        _showHint();
      }
    }
  }

  void _showModeSelector() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Choose Learning Mode',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildModeOption(
              LearningMode.socratic,
              '🧠 Learn Deeply',
              'Full Socratic teaching experience',
              Icons.psychology,
              Colors.purple,
            ),
            _buildModeOption(
              LearningMode.guided,
              '💡 Quick Help',
              'Hints + solution when stuck',
              Icons.lightbulb_outline,
              Colors.blue,
            ),
            _buildModeOption(
              LearningMode.direct,
              '⚡ Just Answer',
              'Straight to solution (for homework rush)',
              Icons.flash_on,
              Colors.orange,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildModeOption(
    LearningMode mode,
    String title,
    String subtitle,
    IconData icon,
    Color color,
  ) {
    final isSelected = ref.read(learningModeProvider).mode == mode;
    
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: color.withOpacity(0.1),
        child: Icon(icon, color: color),
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: isSelected ? Icon(Icons.check_circle, color: color) : null,
      onTap: () {
        ref.read(learningModeProvider.notifier).setMode(mode);
        Navigator.pop(context);
      },
    );
  }

  Color _getDifficultyColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return Colors.green;
      case 'medium':
        return Colors.orange;
      case 'hard':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}
