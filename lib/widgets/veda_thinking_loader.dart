import 'package:flutter/material.dart';
import 'dart:math';

/// 🧠 VEDA Thinking Loader
/// Masks latency by making AI generation feel like "thinking"
/// Turns 2-5 second wait into an engaging experience

class VedaThinkingLoader extends StatefulWidget {
  final VoidCallback? onComplete;
  final int estimatedWaitMs;
  final String concept;

  const VedaThinkingLoader({
    Key? key,
    this.onComplete,
    this.estimatedWaitMs = 2000,
    required this.concept,
  }) : super(key: key);

  @override
  _VedaThinkingLoaderState createState() => _VedaThinkingLoaderState();
}

class _VedaThinkingLoaderState extends State<VedaThinkingLoader>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _dotController;
  late AnimationController _messageController;
  
  int _currentMessageIndex = 0;
  bool _isComplete = false;

  // Different messages for different "phases" of thinking
  late List<String> _thinkingMessages;

  @override
  void initState() {
    super.initState();
    
    // Customize messages based on concept
    _thinkingMessages = _getThinkingMessages(widget.concept);
    
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _dotController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat();

    _messageController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );

    // Cycle through messages
    _startMessageCycle();
    
    // Complete after estimated time
    Future.delayed(Duration(milliseconds: widget.estimatedWaitMs), () {
      if (mounted) {
        setState(() => _isComplete = true);
        _pulseController.stop();
        Future.delayed(const Duration(milliseconds: 500), () {
          widget.onComplete?.call();
        });
      }
    });
  }

  List<String> _getThinkingMessages(String concept) {
    final messagesByConcept = {
      'trigonometry': [
        'Imagining a right triangle...',
        'Calculating angles...',
        'Finding the perfect height...',
        'Adding some real-world context...',
      ],
      'algebra': [
        'Solving for x...',
        'Balancing the equation...',
        'Finding patterns...',
        'Crafting a word problem...',
      ],
      'geometry': [
        'Drawing shapes...',
        'Calculating areas...',
        'Plotting coordinates...',
        'Creating a diagram...',
      ],
      'probability': [
        'Shuffling the deck...',
        'Rolling the dice...',
        'Calculating odds...',
        'Counting outcomes...',
      ],
    };

    final specific = messagesByConcept[concept.toLowerCase()] ?? [
      'Analyzing the concept...',
      'Crafting a unique question...',
      'Adding Indian context...',
      'Double-checking the math...',
    ];

    return [
      'VEDA is thinking...',
      ...specific,
      'Almost ready...',
    ];
  }

  void _startMessageCycle() {
    Future.delayed(const Duration(milliseconds: 600), () {
      if (mounted && !_isComplete) {
        setState(() {
          _currentMessageIndex = (_currentMessageIndex + 1) % _thinkingMessages.length;
        });
        _startMessageCycle();
      }
    });
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _dotController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: Center(
        child: AnimatedBuilder(
          animation: Listenable.merge([_pulseController, _dotController]),
          builder: (context, child) {
            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Animated Brain/Mascot
                Transform.scale(
                  scale: 0.8 + (_pulseController.value * 0.1),
                  child: Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          Colors.purple.shade400,
                          Colors.deepPurple.shade700,
                        ],
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.purple.withOpacity(0.3 + (_pulseController.value * 0.3)),
                          blurRadius: 30 + (_pulseController.value * 20),
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: Center(
                      child: _isComplete
                          ? const Icon(
                              Icons.check,
                              size: 60,
                              color: Colors.white,
                            )
                          : const Text(
                              '🧠',
                              style: TextStyle(fontSize: 50),
                            ),
                    ),
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // Thinking Message with fade
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: Text(
                    _thinkingMessages[_currentMessageIndex],
                    key: ValueKey<int>(_currentMessageIndex),
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey.shade700,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                
                const SizedBox(height: 24),
                
                // Animated dots
                if (!_isComplete)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(3, (index) {
                      final delay = index * 0.3;
                      final dotValue = (_dotController.value + delay) % 1.0;
                      return AnimatedBuilder(
                        animation: _dotController,
                        builder: (context, child) {
                          return Container(
                            width: 12,
                            height: 12,
                            margin: const EdgeInsets.symmetric(horizontal: 4),
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.purple.withOpacity(
                                0.3 + (sin(dotValue * pi * 2) + 1) * 0.35,
                              ),
                            ),
                          );
                        },
                      );
                    }),
                  ),
                
                if (_isComplete)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.green.shade100,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.check_circle, color: Colors.green.shade700),
                        const SizedBox(width: 8),
                        Text(
                          'Ready!',
                          style: TextStyle(
                            color: Colors.green.shade700,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                
                const SizedBox(height: 48),
                
                // Fun fact or tip
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 32),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.amber.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.amber.shade200),
                  ),
                  child: Row(
                    children: [
                      const Text('💡', style: TextStyle(fontSize: 24)),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _getRandomTip(),
                          style: TextStyle(
                            color: Colors.amber.shade900,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  String _getRandomTip() {
    final tips = [
      'Tip: Take deep breaths while solving. It helps!',
      'Did you know? The word "algebra" comes from Arabic!',
      'Pro tip: Draw the diagram first, then solve.',
      'Remember: Wrong answers are just learning opportunities!',
      'Fun fact: Ancient Indians invented zero! 🇮🇳',
      'Mindset: "I can\'t do this... yet!"',
      'Strategy: Break big problems into small steps.',
      'CBSE Insight: 3-mark questions usually need 3 steps!',
    ];
    return tips[Random().nextInt(tips.length)];
  }
}

/// ⚡ Quick Loading Indicator (for pattern questions < 100ms)
class QuickLoadingPulse extends StatelessWidget {
  const QuickLoadingPulse({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: Colors.purple.shade100,
        ),
        child: const CircularProgressIndicator(
          strokeWidth: 3,
          valueColor: AlwaysStoppedAnimation<Color>(Colors.purple),
        ),
      ),
    );
  }
}

/// 🎭 Smart Loading Wrapper
/// Automatically chooses between quick pulse and VEDA thinking based on source
class SmartLoadingWrapper extends StatelessWidget {
  final bool isAiQuestion; // true = AI (slow), false = Pattern (fast)
  final String concept;
  final Widget child;
  final bool isLoading;
  final VoidCallback? onLoadingComplete;

  const SmartLoadingWrapper({
    Key? key,
    required this.isAiQuestion,
    required this.concept,
    required this.child,
    required this.isLoading,
    this.onLoadingComplete,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (!isLoading) return child;

    // Pattern questions - just quick pulse
    if (!isAiQuestion) {
      return const QuickLoadingPulse();
    }

    // AI questions - full VEDA thinking experience
    return VedaThinkingLoader(
      concept: concept,
      estimatedWaitMs: 2500,
      onComplete: onLoadingComplete,
    );
  }
}
