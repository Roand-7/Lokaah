import 'package:flutter/material.dart';
import 'dart:math';

/// 🌟 STUNNING XP PROGRESS BAR
/// Glassmorphic design with animated glow, particle effects, and satisfying progress

class StunningXPBar extends StatefulWidget {
  final int level;
  final int currentXP;
  final int xpForNextLevel;
  final int streak;
  final bool isOnFire;
  final int fireStreak;

  const StunningXPBar({
    Key? key,
    required this.level,
    required this.currentXP,
    required this.xpForNextLevel,
    this.streak = 0,
    this.isOnFire = false,
    this.fireStreak = 0,
  }) : super(key: key);

  @override
  _StunningXPBarState createState() => _StunningXPBarState();
}

class _StunningXPBarState extends State<StunningXPBar>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _shakeController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _shakeAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _shakeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _shakeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _shakeController, curve: Curves.elasticOut),
    );

    if (widget.isOnFire) {
      _shakeController.forward();
    }
  }

  @override
  void didUpdateWidget(StunningXPBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isOnFire && !oldWidget.isOnFire) {
      _shakeController.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _shakeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final progress = (widget.currentXP / widget.xpForNextLevel).clamp(0.0, 1.0);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            const Color(0xFF2D1B69),
            const Color(0xFF1A0F3C),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: widget.isOnFire
                ? Colors.orange.withOpacity(0.4)
                : Colors.purple.withOpacity(0.3),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // 🏆 LEVEL BADGE with glow
            AnimatedBuilder(
              animation: _pulseAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: widget.isOnFire ? _pulseAnimation.value : 1.0,
                  child: Container(
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: widget.isOnFire
                            ? [Colors.orange.shade400, Colors.red.shade600]
                            : [Colors.amber.shade300, Colors.orange.shade600],
                      ),
                      border: Border.all(
                        color: Colors.white.withOpacity(0.5),
                        width: 2,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: widget.isOnFire
                              ? Colors.orange.withOpacity(0.6)
                              : Colors.amber.withOpacity(0.5),
                          blurRadius: 20 * _pulseAnimation.value,
                          spreadRadius: 5,
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        '${widget.level}',
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          shadows: [
                            Shadow(
                              color: Colors.black38,
                              blurRadius: 4,
                              offset: Offset(0, 2),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
            
            const SizedBox(width: 16),
            
            // 📊 XP PROGRESS SECTION
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Level text and XP counter
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Level ${widget.level}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                      RichText(
                        text: TextSpan(
                          children: [
                            TextSpan(
                              text: '${widget.currentXP}',
                              style: const TextStyle(
                                color: Colors.amber,
                                fontWeight: FontWeight.bold,
                                fontSize: 13,
                              ),
                            ),
                            TextSpan(
                              text: ' / ${widget.xpForNextLevel} XP',
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.6),
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // Animated progress bar
                  Stack(
                    children: [
                      // Background
                      Container(
                        height: 12,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                      ),
                      
                      // Progress with shimmer effect
                      ClipRRect(
                        borderRadius: BorderRadius.circular(6),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 500),
                          curve: Curves.easeOutCubic,
                          height: 12,
                          width: MediaQuery.of(context).size.width * 0.6 * progress,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: widget.isOnFire
                                  ? [
                                      Colors.yellow.shade400,
                                      Colors.orange.shade500,
                                      Colors.red.shade500,
                                    ]
                                  : [
                                      Colors.green.shade400,
                                      Colors.teal.shade400,
                                    ],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: widget.isOnFire
                                    ? Colors.orange.withOpacity(0.8)
                                    : Colors.green.withOpacity(0.6),
                                blurRadius: 10,
                                spreadRadius: 2,
                              ),
                            ],
                          ),
                          child: widget.isOnFire
                              ? _FireShimmer()
                              : _ShimmerEffect(),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            const SizedBox(width: 16),
            
            // 🔥 FIRE STREAK BADGE
            if (widget.isOnFire)
              AnimatedBuilder(
                animation: _shakeController,
                builder: (context, child) {
                  return Transform.rotate(
                    angle: sin(_shakeAnimation.value * pi * 4) * 0.1,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.orange.shade600,
                            Colors.red.shade700,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.orange.withOpacity(0.6),
                            blurRadius: 15,
                            spreadRadius: 2,
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            '🔥',
                            style: TextStyle(fontSize: 18),
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '${widget.fireStreak}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              )
            else if (widget.streak > 0)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.blue.withOpacity(0.5)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('📅', style: TextStyle(fontSize: 14)),
                    const SizedBox(width: 4),
                    Text(
                      '${widget.streak}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// ✨ Shimmer effect for progress bar
class _ShimmerEffect extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ShaderMask(
      shaderCallback: (bounds) {
        return LinearGradient(
          colors: [
            Colors.white.withOpacity(0),
            Colors.white.withOpacity(0.5),
            Colors.white.withOpacity(0),
          ],
          stops: const [0.0, 0.5, 1.0],
        ).createShader(bounds);
      },
      blendMode: BlendMode.srcATop,
      child: Container(
        color: Colors.white,
      ),
    );
  }
}

/// 🔥 Fire shimmer for fire streak mode
class _FireShimmer extends StatefulWidget {
  @override
  __FireShimmerState createState() => __FireShimmerState();
}

class __FireShimmerState extends State<_FireShimmer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat();
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
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              colors: [
                Colors.yellow.withOpacity(0),
                Colors.yellow.withOpacity(0.8),
                Colors.orange.withOpacity(0),
              ],
              stops: [
                0.0,
                0.5 + sin(_controller.value * 2 * pi) * 0.3,
                1.0,
              ],
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcATop,
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.transparent,
                  Colors.white.withOpacity(0.3),
                  Colors.transparent,
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

/// 🌊 WAVE PROGRESS BAR (Alternative design)
class WaveXPBar extends StatefulWidget {
  final double progress;
  final Color color;

  const WaveXPBar({
    Key? key,
    required this.progress,
    this.color = Colors.blue,
  }) : super(key: key);

  @override
  _WaveXPBarState createState() => _WaveXPBarState();
}

class _WaveXPBarState extends State<WaveXPBar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    )..repeat();
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
        return CustomPaint(
          size: const Size(double.infinity, 12),
          painter: WavePainter(
            progress: widget.progress,
            color: widget.color,
            wavePhase: _controller.value * 2 * pi,
          ),
        );
      },
    );
  }
}

class WavePainter extends CustomPainter {
  final double progress;
  final Color color;
  final double wavePhase;

  WavePainter({
    required this.progress,
    required this.color,
    required this.wavePhase,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    final path = Path();
    final width = size.width * progress;
    
    path.moveTo(0, size.height);
    
    for (double x = 0; x <= width; x++) {
      final y = size.height / 2 + 
          sin((x / 20) + wavePhase) * 3 +
          sin((x / 15) + wavePhase * 1.5) * 2;
      path.lineTo(x, y);
    }
    
    path.lineTo(width, size.height);
    path.close();
    
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
