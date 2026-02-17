import 'package:flutter/material.dart';
import 'dart:math';
import '../effects/particle_system.dart';

/// 🎊 LEVEL UP CELEBRATION MODAL
/// Full-screen celebration when user levels up
/// Triggers: confetti, particle explosion, scale animations

class LevelUpCelebration extends StatefulWidget {
  final int newLevel;
  final int xpGained;
  final VoidCallback onComplete;

  const LevelUpCelebration({
    Key? key,
    required this.newLevel,
    required this.xpGained,
    required this.onComplete,
  }) : super(key: key);

  @override
  _LevelUpCelebrationState createState() => _LevelUpCelebrationState();
}

class _LevelUpCelebrationState extends State<LevelUpCelebration>
    with TickerProviderStateMixin {
  late AnimationController _scaleController;
  late AnimationController _rotateController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotateAnimation;
  late Animation<double> _opacityAnimation;

  @override
  void initState() {
    super.initState();
    
    _scaleController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );

    _rotateController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );

    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween(begin: 0.0, end: 1.3),
        weight: 40,
        curve: Curves.elasticOut,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.3, end: 1.0),
        weight: 20,
        curve: Curves.easeOut,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.0, end: 1.0),
        weight: 30,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.0, end: 0.8),
        weight: 10,
      ),
    ]).animate(_scaleController);

    _rotateAnimation = Tween<double>(
      begin: -0.2,
      end: 0,
    ).animate(CurvedAnimation(
      parent: _rotateController,
      curve: Curves.elasticOut,
    ));

    _opacityAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: 1.0), weight: 10),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.0), weight: 70),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 0.0), weight: 20),
    ]).animate(_scaleController);

    _scaleController.forward();
    _rotateController.forward();

    // Auto dismiss
    Future.delayed(const Duration(milliseconds: 3500), () {
      if (mounted) widget.onComplete();
    });
  }

  @override
  void dispose() {
    _scaleController.dispose();
    _rotateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.black.withOpacity(0.8),
      child: Stack(
        children: [
          // Confetti background
          const ConfettiExplosion(),
          
          // Particle explosion
          ParticleSystem(
            particleCount: 80,
            color: Colors.amber,
            onComplete: () {},
          ),
          
          // Main content
          Center(
            child: AnimatedBuilder(
              animation: Listenable.merge([_scaleController, _rotateController]),
              builder: (context, child) {
                return Opacity(
                  opacity: _opacityAnimation.value,
                  child: Transform.scale(
                    scale: _scaleAnimation.value,
                    child: Transform.rotate(
                      angle: _rotateAnimation.value,
                      child: Container(
                        padding: const EdgeInsets.all(40),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                            colors: [
                              const Color(0xFF9C27B0),
                              const Color(0xFF7B1FA2),
                              const Color(0xFF4A148C),
                            ],
                          ),
                          borderRadius: BorderRadius.circular(30),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.purple.withOpacity(0.5),
                              blurRadius: 50,
                              spreadRadius: 10,
                            ),
                          ],
                          border: Border.all(
                            color: Colors.amber,
                            width: 3,
                          ),
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            // Level up text with glow
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 24,
                                vertical: 8,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.amber,
                                borderRadius: BorderRadius.circular(20),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.amber.withOpacity(0.6),
                                    blurRadius: 20,
                                    spreadRadius: 5,
                                  ),
                                ],
                              ),
                              child: const Text(
                                'LEVEL UP!',
                                style: TextStyle(
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.black87,
                                  letterSpacing: 2,
                                ),
                              ),
                            ),
                            
                            const SizedBox(height: 30),
                            
                            // Big level number
                            Stack(
                              alignment: Alignment.center,
                              children: [
                                // Glow effect
                                Text(
                                  '${widget.newLevel}',
                                  style: TextStyle(
                                    fontSize: 120,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.amber.withOpacity(0.3),
                                  ),
                                ),
                                // Main number
                                Text(
                                  '${widget.newLevel}',
                                  style: const TextStyle(
                                    fontSize: 100,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                    shadows: [
                                      Shadow(
                                        color: Colors.amber,
                                        blurRadius: 30,
                                      ),
                                      Shadow(
                                        color: Colors.purple,
                                        blurRadius: 60,
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            
                            const SizedBox(height: 20),
                            
                            // XP gained
                            Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.star,
                                  color: Colors.amber,
                                  size: 28,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  '+${widget.xpGained} XP',
                                  style: const TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                              ],
                            ),
                            
                            const SizedBox(height: 30),
                            
                            // Unlocked text
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 20,
                                vertical: 10,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(15),
                              ),
                              child: Column(
                                children: [
                                  const Text(
                                    '🎉 New Title Unlocked!',
                                    style: TextStyle(
                                      color: Colors.white70,
                                      fontSize: 14,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    _getTitleForLevel(widget.newLevel),
                                    style: const TextStyle(
                                      color: Colors.amber,
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            
                            const SizedBox(height: 30),
                            
                            // Continue button
                            ElevatedButton(
                              onPressed: widget.onComplete,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.amber,
                                foregroundColor: Colors.black87,
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 40,
                                  vertical: 16,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(30),
                                ),
                                elevation: 10,
                                shadowColor: Colors.amber.withOpacity(0.5),
                              ),
                              child: const Text(
                                'AWESOME! 🚀',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          
          // Floating particles around
          ...List.generate(6, (index) {
            final angle = index * pi / 3;
            return Positioned(
              left: MediaQuery.of(context).size.width / 2 + 
                  cos(angle) * 150 - 25,
              top: MediaQuery.of(context).size.height / 2 + 
                  sin(angle) * 150 - 25,
              child: _OrbitingStar(
                delay: index * 0.5,
                color: index % 2 == 0 ? Colors.amber : Colors.white,
              ),
            );
          }),
        ],
      ),
    );
  }

  String _getTitleForLevel(int level) {
    final titles = {
      1: 'Math Newbie',
      2: 'Number Cruncher',
      3: 'Equation Solver',
      5: 'Geometry Guru',
      7: 'Algebra Ace',
      10: 'Math Wizard',
      15: 'Calculus King',
      20: 'Math Legend',
      25: 'Newton Reborn',
      30: 'Math God',
    };
    
    for (int i = level; i >= 1; i--) {
      if (titles.containsKey(i)) return titles[i]!;
    }
    return 'Math Master';
  }
}

/// ⭐ Orbiting star animation
class _OrbitingStar extends StatefulWidget {
  final double delay;
  final Color color;

  const _OrbitingStar({
    required this.delay,
    required this.color,
  });

  @override
  __OrbitingStarState createState() => __OrbitingStarState();
}

class __OrbitingStarState extends State<_OrbitingStar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );
    
    Future.delayed(Duration(milliseconds: (widget.delay * 1000).toInt()), () {
      if (mounted) _controller.repeat();
    });
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
        final scale = 0.8 + sin(_controller.value * 2 * pi) * 0.3;
        return Transform.scale(
          scale: scale,
          child: Icon(
            Icons.star,
            color: widget.color,
            size: 30,
          ),
        );
      },
    );
  }
}

/// 🏅 BADGE UNLOCK CELEBRATION
class BadgeUnlockCelebration extends StatefulWidget {
  final String badgeName;
  final String badgeEmoji;
  final String badgeDescription;
  final VoidCallback onComplete;

  const BadgeUnlockCelebration({
    Key? key,
    required this.badgeName,
    required this.badgeEmoji,
    required this.badgeDescription,
    required this.onComplete,
  }) : super(key: key);

  @override
  _BadgeUnlockCelebrationState createState() => _BadgeUnlockCelebrationState();
}

class _BadgeUnlockCelebrationState extends State<BadgeUnlockCelebration>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );

    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween(begin: 0.0, end: 1.5),
        weight: 30,
        curve: Curves.elasticOut,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.5, end: 1.0),
        weight: 20,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.0, end: 1.0),
        weight: 40,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.0, end: 0.0),
        weight: 10,
      ),
    ]).animate(_controller);

    _rotationAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween(begin: -2 * pi, end: 0),
        weight: 40,
        curve: Curves.easeOutBack,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 0, end: 0),
        weight: 60,
      ),
    ]).animate(_controller);

    _controller.forward().then((_) => widget.onComplete());
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.black.withOpacity(0.7),
      child: Center(
        child: AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Transform.rotate(
                angle: _rotationAnimation.value,
                child: Container(
                  padding: const EdgeInsets.all(30),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Colors.amber.shade400,
                        Colors.orange.shade600,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(25),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.amber.withOpacity(0.6),
                        blurRadius: 40,
                        spreadRadius: 15,
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text(
                        '🎉 BADGE UNLOCKED!',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 20),
                      Text(
                        widget.badgeEmoji,
                        style: const TextStyle(fontSize: 80),
                      ),
                      const SizedBox(height: 15),
                      Text(
                        widget.badgeName,
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        widget.badgeDescription,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
