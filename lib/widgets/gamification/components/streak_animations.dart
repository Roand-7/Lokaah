import 'package:flutter/material.dart';
import 'dart:math';

/// 🔥 STREAK ANIMATIONS
/// Fire effects, combo counters, and motivational visuals

class FireStreakWidget extends StatefulWidget {
  final int streak;
  final bool isActive;

  const FireStreakWidget({
    Key? key,
    required this.streak,
    this.isActive = true,
  }) : super(key: key);

  @override
  _FireStreakWidgetState createState() => _FireStreakWidgetState();
}

class _FireStreakWidgetState extends State<FireStreakWidget>
    with TickerProviderStateMixin {
  late List<AnimationController> _flameControllers;
  final Random random = Random();

  @override
  void initState() {
    super.initState();
    _initFlameControllers();
  }

  void _initFlameControllers() {
    _flameControllers = List.generate(
      5,
      (index) => AnimationController(
        vsync: this,
        duration: Duration(milliseconds: 600 + random.nextInt(400)),
      )..repeat(reverse: true),
    );
  }

  @override
  void dispose() {
    for (var controller in _flameControllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isActive) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.orange.shade600,
            Colors.red.shade700,
            Colors.deepOrange.shade900,
          ],
        ),
        borderRadius: BorderRadius.circular(25),
        boxShadow: [
          BoxShadow(
            color: Colors.orange.withOpacity(0.6),
            blurRadius: 20,
            spreadRadius: 5,
          ),
          BoxShadow(
            color: Colors.red.withOpacity(0.4),
            blurRadius: 40,
            spreadRadius: 10,
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Animated flames
          SizedBox(
            width: 40,
            height: 30,
            child: Stack(
              alignment: Alignment.bottomCenter,
              children: _flameControllers.asMap().entries.map((entry) {
                final index = entry.key;
                final controller = entry.value;
                
                return AnimatedBuilder(
                  animation: controller,
                  builder: (context, child) {
                    final height = 15 + controller.value * 15;
                    final offset = (index - 2) * 8.0;
                    
                    return Positioned(
                      bottom: 0,
                      left: 20 + offset - 5,
                      child: Container(
                        width: 10,
                        height: height,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.bottomCenter,
                            end: Alignment.topCenter,
                            colors: [
                              Colors.yellow,
                              Colors.orange,
                              Colors.red.withOpacity(0.8),
                            ],
                          ),
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(5 + random.nextDouble() * 3),
                            topRight: Radius.circular(5 + random.nextDouble() * 3),
                          ),
                        ),
                      ),
                    );
                  },
                );
              }).toList(),
            ),
          ),
          
          const SizedBox(width: 8),
          
          // Streak count
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${widget.streak}',
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  shadows: [
                    Shadow(
                      color: Colors.orange,
                      blurRadius: 10,
                    ),
                  ],
                ),
              ),
              Text(
                widget.streak >= 10 ? 'UNSTOPPABLE!' : 'STREAK',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: Colors.yellow.shade200,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// ⚡ COMBO COUNTER
/// Shows multiplier for consecutive correct answers

class ComboCounter extends StatefulWidget {
  final int combo;
  final int maxCombo;

  const ComboCounter({
    Key? key,
    required this.combo,
    this.maxCombo = 0,
  }) : super(key: key);

  @override
  _ComboCounterState createState() => _ComboCounterState();
}

class _ComboCounterState extends State<ComboCounter>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _shakeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );

    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween(begin: 1.0, end: 1.5),
        weight: 30,
        curve: Curves.elasticOut,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.5, end: 1.0),
        weight: 70,
      ),
    ]).animate(_controller);

    _shakeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.elasticIn),
    );

    if (widget.combo > 1) {
      _controller.forward(from: 0);
    }
  }

  @override
  void didUpdateWidget(ComboCounter oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.combo > oldWidget.combo) {
      _controller.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.combo < 2) return const SizedBox.shrink();

    final isHighCombo = widget.combo >= 5;
    
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Transform.rotate(
            angle: sin(_shakeAnimation.value * pi * 4) * 0.1,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: isHighCombo
                      ? [Colors.purple.shade600, Colors.pink.shade600]
                      : [Colors.blue.shade600, Colors.cyan.shade600],
                ),
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: isHighCombo
                        ? Colors.purple.withOpacity(0.6)
                        : Colors.blue.withOpacity(0.5),
                    blurRadius: 20,
                    spreadRadius: 5,
                  ),
                ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    isHighCombo ? Icons.local_fire_department : Icons.flash_on,
                    color: Colors.yellow,
                    size: 24,
                  ),
                  const SizedBox(width: 8),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${widget.combo}x COMBO',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      if (widget.combo >= 3)
                        Text(
                          '+${widget.combo * 5} BONUS XP',
                          style: TextStyle(
                            color: Colors.yellow.shade200,
                            fontSize: 11,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

/// 🎯 DAILY GOAL PROGRESS
/// Shows progress toward daily target with satisfying animations

class DailyGoalProgress extends StatefulWidget {
  final int current;
  final int target;

  const DailyGoalProgress({
    Key? key,
    required this.current,
    required this.target,
  }) : super(key: key);

  @override
  _DailyGoalProgressState createState() => _DailyGoalProgressState();
}

class _DailyGoalProgressState extends State<DailyGoalProgress>
    with TickerProviderStateMixin {
  late AnimationController _fillController;
  late Animation<double> _fillAnimation;

  @override
  void initState() {
    super.initState();
    _fillController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );

    _updateAnimation();
  }

  @override
  void didUpdateWidget(DailyGoalProgress oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.current != oldWidget.current) {
      _updateAnimation();
    }
  }

  void _updateAnimation() {
    final progress = (widget.current / widget.target).clamp(0.0, 1.0);
    _fillAnimation = Tween<double>(
      begin: _fillAnimation?.value ?? 0,
      end: progress,
    ).animate(CurvedAnimation(
      parent: _fillController,
      curve: Curves.easeOutCubic,
    ));
    _fillController.forward(from: 0);
  }

  @override
  void dispose() {
    _fillController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isComplete = widget.current >= widget.target;
    final percentage = (widget.current / widget.target * 100).toInt();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isComplete
              ? [Colors.green.shade800, Colors.teal.shade800]
              : [Colors.grey.shade900, Colors.black87],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: isComplete ? Colors.green : Colors.grey.shade700,
          width: 2,
        ),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    isComplete ? Icons.check_circle : Icons.track_changes,
                    color: isComplete ? Colors.green : Colors.blue,
                    size: 24,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'Daily Goal',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: isComplete
                      ? Colors.green.withOpacity(0.3)
                      : Colors.blue.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  isComplete ? 'COMPLETED! 🎉' : '$percentage%',
                  style: TextStyle(
                    color: isComplete ? Colors.green : Colors.blue,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Progress bar
          Stack(
            children: [
              // Background
              Container(
                height: 16,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              
              // Animated fill
              AnimatedBuilder(
                animation: _fillController,
                builder: (context, child) {
                  return Container(
                    height: 16,
                    width: MediaQuery.of(context).size.width * 
                        0.7 * _fillAnimation.value,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: isComplete
                            ? [Colors.green.shade400, Colors.teal.shade400]
                            : [Colors.blue.shade400, Colors.cyan.shade400],
                      ),
                      borderRadius: BorderRadius.circular(8),
                      boxShadow: [
                        BoxShadow(
                          color: isComplete
                              ? Colors.green.withOpacity(0.5)
                              : Colors.blue.withOpacity(0.5),
                          blurRadius: 10,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                  );
                },
              ),
              
              // Milestone markers
              ...List.generate(4, (index) {
                final milestone = (index + 1) * (widget.target / 4);
                final isReached = widget.current >= milestone;
                
                return Positioned(
                  left: (MediaQuery.of(context).size.width * 0.7) * 
                      ((index + 1) / 4) - 6,
                  top: 2,
                  child: Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: isReached ? Colors.white : Colors.grey,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: isReached ? Colors.green : Colors.grey.shade600,
                        width: 2,
                      ),
                    ),
                  ),
                );
              }),
            ],
          ),
          
          const SizedBox(height: 8),
          
          Text(
            '${widget.current} / ${widget.target} questions',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 12,
            ),
          ),
          
          if (isComplete)
            Container(
              margin: const EdgeInsets.only(top: 8),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.amber.shade600, Colors.orange.shade600],
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                '+100 BONUS XP',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// 🎊 ACHIEVEMENT TOAST
/// Brief notification when achievements are unlocked

class AchievementToast extends StatefulWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;
  final VoidCallback onDismiss;

  const AchievementToast({
    Key? key,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
    required this.onDismiss,
  }) : super(key: key);

  @override
  _AchievementToastState createState() => _AchievementToastState();
}

class _AchievementToastState extends State<AchievementToast>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _opacityAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 4000),
    );

    _slideAnimation = TweenSequence<Offset>([
      TweenSequenceItem(
        tween: Tween(begin: const Offset(0, -2), end: Offset.zero),
        weight: 10,
        curve: Curves.elasticOut,
      ),
      TweenSequenceItem(
        tween: Tween(begin: Offset.zero, end: Offset.zero),
        weight: 75,
      ),
      TweenSequenceItem(
        tween: Tween(begin: Offset.zero, end: const Offset(0, -2)),
        weight: 15,
        curve: Curves.easeIn,
      ),
    ]).animate(_controller);

    _opacityAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: 1.0), weight: 10),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.0), weight: 80),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 0.0), weight: 10),
    ]).animate(_controller);

    _controller.forward().then((_) => widget.onDismiss());
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Positioned(
          top: 100,
          left: 20,
          right: 20,
          child: SlideTransition(
            position: _slideAnimation,
            child: Opacity(
              opacity: _opacityAnimation.value,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      widget.color,
                      widget.color.withOpacity(0.8),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: widget.color.withOpacity(0.4),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        widget.icon,
                        color: Colors.white,
                        size: 28,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.title,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            widget.subtitle,
                            style: TextStyle(
                              color: Colors.white.withOpacity(0.8),
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () {
                        _controller.stop();
                        widget.onDismiss();
                      },
                      icon: const Icon(Icons.close, color: Colors.white70),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
