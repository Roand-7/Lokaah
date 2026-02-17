import 'package:flutter/material.dart';
import '../widgets/jsxgraph_viewer.dart';
import '../models/generated_question.dart';

/// Example Question Screen with JSXGraph Integration
/// 
/// Demonstrates:
/// - Displaying AI-generated questions with interactive visualizations
/// - Capturing student interactions
/// - Extracting graph state for answer verification
/// - VEDA hint integration
class QuestionScreen extends StatefulWidget {
  final GeneratedQuestion question;

  const QuestionScreen({Key? key, required this.question}) : super(key: key);

  @override
  State<QuestionScreen> createState() => _QuestionScreenState();
}

class _QuestionScreenState extends State<QuestionScreen> {
  final GlobalKey<JSXGraphViewerState> _graphKey = GlobalKey();
  final TextEditingController _answerController = TextEditingController();
  
  Map<String, dynamic>? _currentGraphState;
  bool _isSubmitting = false;
  String? _feedback;

  @override
  void dispose() {
    _answerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('LOKAAH Practice'),
        backgroundColor: const Color(0xFF2C3E50),
        foregroundColor: Colors.white,
        actions: [
          // Hint button (VEDA integration)
          IconButton(
            icon: const Icon(Icons.lightbulb_outline),
            onPressed: _showHint,
            tooltip: 'Get a hint',
          ),
        ],
      ),
      body: Column(
        children: [
          // Question header with metadata
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            color: Colors.grey.shade100,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    _buildBadge('${widget.question.marks} marks', Colors.blue),
                    const SizedBox(width: 8),
                    _buildBadge(
                      widget.question.difficulty,
                      _getDifficultyColor(widget.question.difficulty),
                    ),
                    const SizedBox(width: 8),
                    _buildBadge(
                      widget.question.source.toUpperCase(),
                      widget.question.source == 'ai' ? Colors.purple : Colors.green,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  widget.question.concept,
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          
          // Question text
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              widget.question.text,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontSize: 16,
                    height: 1.5,
                  ),
            ),
          ),

          // Interactive Graph (if question has visualization)
          if (widget.question.jsxGraphCode != null)
            Expanded(
              flex: 2,
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300, width: 2),
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: JSXGraphViewer(
                    key: _graphKey,
                    jsxCode: widget.question.jsxGraphCode,
                    boundingBox: widget.question.graphBoundingBox ?? [-10, 10, 10, -10],
                    showAxis: widget.question.showAxis ?? true,
                    showGrid: widget.question.showGrid ?? true,
                    theme: _getGraphTheme(widget.question.difficulty),
                    onInteraction: _handleInteraction,
                    onReady: () {
                      debugPrint('Graph ready for question: ${widget.question.id}');
                    },
                    onError: (error) {
                      _showSnackBar('Graph error: $error', isError: true);
                    },
                  ),
                ),
              ),
            ),

          // Feedback section
          if (_feedback != null)
            Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _feedback!.contains('✅') ? Colors.green.shade50 : Colors.red.shade50,
                border: Border.all(
                  color: _feedback!.contains('✅') ? Colors.green : Colors.red,
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(_feedback!, style: const TextStyle(fontSize: 14)),
            ),

          // Answer input section
          Expanded(
            flex: 1,
            child: Container(
              padding: const EdgeInsets.all(16.0),
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
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Different input methods based on question type
                  if (widget.question.requiresGraphInteraction)
                    _buildGraphAnswerSection()
                  else
                    _buildTextAnswerSection(),

                  const SizedBox(height: 16),

                  // Submit button
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
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGraphAnswerSection() {
    return Column(
      children: [
        const Text(
          'Use the interactive graph to answer the question',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 14, color: Colors.grey),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: _extractAnswerFromGraph,
          icon: const Icon(Icons.check_circle_outline),
          label: const Text('Use Graph Position as Answer'),
          style: OutlinedButton.styleFrom(
            foregroundColor: const Color(0xFF27AE60),
            side: const BorderSide(color: Color(0xFF27AE60)),
          ),
        ),
        if (_currentGraphState != null)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              'Graph state captured ✓',
              style: TextStyle(color: Colors.green.shade700, fontSize: 12),
            ),
          ),
      ],
    );
  }

  Widget _buildTextAnswerSection() {
    return TextField(
      controller: _answerController,
      decoration: InputDecoration(
        labelText: 'Your Answer',
        hintText: 'Enter your answer here',
        border: const OutlineInputBorder(),
        prefixIcon: const Icon(Icons.edit),
        suffixIcon: _answerController.text.isNotEmpty
            ? IconButton(
                icon: const Icon(Icons.clear),
                onPressed: () {
                  setState(() {
                    _answerController.clear();
                  });
                },
              )
            : null,
      ),
      keyboardType: widget.question.answerType == 'numeric'
          ? TextInputType.number
          : TextInputType.text,
      onChanged: (_) => setState(() {}),
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

  void _handleInteraction(Map<String, dynamic> interaction) {
    debugPrint('Student interaction: $interaction');
    
    // Real-time feedback for VEDA teaching loop
    if (interaction['type'] == 'pointMoved') {
      // Could trigger immediate feedback: "You're getting closer!"
      debugPrint('Student moved point: ${interaction['name']}');
    } else if (interaction['type'] == 'boardClicked') {
      debugPrint('Student clicked at (${interaction['x']}, ${interaction['y']})');
    }
  }

  Future<void> _extractAnswerFromGraph() async {
    final state = await _graphKey.currentState?.getGraphState();
    if (state != null) {
      setState(() {
        _currentGraphState = state;
      });
      _showSnackBar('Graph state captured successfully!');
    } else {
      _showSnackBar('Failed to capture graph state', isError: true);
    }
  }

  Future<void> _submitAnswer() async {
    if (_answerController.text.isEmpty && _currentGraphState == null) {
      _showSnackBar('Please provide an answer', isError: true);
      return;
    }

    setState(() {
      _isSubmitting = true;
      _feedback = null;
    });

    try {
      // Build attempt payload
      final attempt = {
        'question_id': widget.question.id,
        'student_id': 'student_123', // From auth context
        'text_answer': _answerController.text,
        'graph_state': _currentGraphState,
        'time_taken_seconds': 120, // Track actual time
        'timestamp': DateTime.now().toIso8601String(),
      };

      // Send to backend (replace with your API call)
      // final response = await api.submitAttempt(attempt);
      
      // Mock response for demo
      await Future.delayed(const Duration(seconds: 1));
      final isCorrect = true; // From API response

      setState(() {
        _feedback = isCorrect
            ? '✅ Excellent! That\'s correct. Ready for the next challenge?'
            : '❌ Not quite. Let\'s review the steps and try a similar question.';
      });

      if (isCorrect) {
        // Celebrate and move to next question
        _showSuccessDialog();
      }
    } catch (e) {
      _showSnackBar('Error submitting answer: $e', isError: true);
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }

  void _showHint() {
    // VEDA hint integration
    // Option 1: Show text hint
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Hint'),
        content: const Text('Think about the trigonometric ratio that relates opposite and adjacent sides...'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it!'),
          ),
        ],
      ),
    );

    // Option 2: Highlight element on graph
    _graphKey.currentState?.highlightElement('point1', color: Colors.orange);

    // Option 3: Add annotation to graph
    _graphKey.currentState?.addAnnotation(
      2, 3, 
      'Check this region',
      color: Colors.orange,
    );
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('🎉 Correct!'),
        content: const Text('Great job! Ready for the next question?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context); // Back to question list
            },
            child: const Text('Next Question'),
          ),
        ],
      ),
    );
  }

  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
        duration: const Duration(seconds: 2),
      ),
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

  String _getGraphTheme(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'success';
      case 'medium':
        return 'default';
      case 'hard':
        return 'warning';
      default:
        return 'default';
    }
  }
}
