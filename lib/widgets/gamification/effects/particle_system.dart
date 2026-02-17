import 'package:flutter/material.dart';
import 'dart:math';

/// ✨ PARTICLE EFFECTS SYSTEM
/// Creates satisfying visual feedback for XP gains, level ups, etc.

class Particle {
  Offset position;
  Offset velocity;
  double life;
  double maxLife;
  Color color;
  double size;
  double rotation;
  double rotationSpeed;

  Particle({
    required this.position,
    required this.velocity,
    required this.maxLife,
    required this.color,
    required this.size,
    this.rotation = 0,
    this.rotationSpeed = 0,
  }) : life = maxLife;

  bool get isDead => life <= 0;

  void update() {
    position += velocity;
    velocity += const Offset(0, 0.1); // Gravity
    life -= 1;
    rotation += rotationSpeed;
  }
}

class ParticleSystem extends StatefulWidget {
  final int particleCount;
  final Color color;
  final VoidCallback? onComplete;
  final Duration duration;

  const ParticleSystem({
    Key? key,
    this.particleCount = 50,
    this.color = Colors.amber,
    this.onComplete,
    this.duration = const Duration(milliseconds: 2000),
  }) : super(key: key);

  @override
  _ParticleSystemState createState() => _ParticleSystemState();
}

class _ParticleSystemState extends State<ParticleSystem>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  List<Particle> particles = [];
  final Random random = Random();

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );

    _initParticles();
    _controller.forward().then((_) {
      widget.onComplete?.call();
    });
  }

  void _initParticles() {
    final center = Offset(
      MediaQuery.of(context).size.width / 2,
      MediaQuery.of(context).size.height / 2,
    );

    for (int i = 0; i < widget.particleCount; i++) {
      final angle = random.nextDouble() * 2 * pi;
      final speed = 5 + random.nextDouble() * 10;
      
      particles.add(Particle(
        position: center,
        velocity: Offset(
          cos(angle) * speed,
          sin(angle) * speed - 5, // Initial upward burst
        ),
        maxLife: 30 + random.nextDouble() * 30,
        color: _getRandomColor(),
        size: 4 + random.nextDouble() * 8,
        rotation: random.nextDouble() * 2 * pi,
        rotationSpeed: (random.nextDouble() - 0.5) * 0.2,
      ));
    }
  }

  Color _getRandomColor() {
    final colors = [
      widget.color,
      Colors.orange,
      Colors.yellow,
      Colors.white,
      Colors.amber.shade300,
    ];
    return colors[random.nextInt(colors.length)];
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
        // Update particles
        for (var particle in particles) {
          particle.update();
        }
        particles.removeWhere((p) => p.isDead);

        return CustomPaint(
          size: Size.infinite,
          painter: ParticlePainter(particles),
        );
      },
    );
  }
}

class ParticlePainter extends CustomPainter {
  final List<Particle> particles;

  ParticlePainter(this.particles);

  @override
  void paint(Canvas canvas, Size size) {
    for (var particle in particles) {
      final paint = Paint()
        ..color = particle.color.withOpacity(particle.life / particle.maxLife)
        ..style = PaintingStyle.fill;

      canvas.save();
      canvas.translate(particle.position.dx, particle.position.dy);
      canvas.rotate(particle.rotation);
      
      // Draw star shape for particles
      final path = Path();
      for (int i = 0; i < 5; i++) {
        final angle = i * 2 * pi / 5 - pi / 2;
        final outerRadius = particle.size;
        final innerRadius = particle.size * 0.4;
        
        if (i == 0) {
          path.moveTo(
            cos(angle) * outerRadius,
            sin(angle) * outerRadius,
          );
        } else {
          path.lineTo(
            cos(angle) * outerRadius,
            sin(angle) * outerRadius,
          );
        }
        
        final innerAngle = (i + 0.5) * 2 * pi / 5 - pi / 2;
        path.lineTo(
          cos(innerAngle) * innerRadius,
          sin(innerAngle) * innerRadius,
        );
      }
      path.close();
      
      canvas.drawPath(path, paint);
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

/// 💫 FLOATING TEXT ANIMATION
/// "+45 XP" that floats up and fades

class FloatingText extends StatefulWidget {
  final String text;
  final Offset startPosition;
  final Color color;
  final double fontSize;

  const FloatingText({
    Key? key,
    required this.text,
    required this.startPosition,
    this.color = Colors.amber,
    this.fontSize = 32,
  }) : super(key: key);

  @override
  _FloatingTextState createState() => _FloatingTextState();
}

class _FloatingTextState extends State<FloatingText>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _positionAnimation;
  late Animation<double> _opacityAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );

    _positionAnimation = Tween<double>(
      begin: 0,
      end: -100,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOut,
    ));

    _opacityAnimation = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 0.0, end: 1.0), weight: 10),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.0), weight: 60),
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 0.0), weight: 30),
    ]).animate(_controller);

    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween(begin: 0.5, end: 1.2),
        weight: 20,
        curve: Curves.elasticOut,
      ),
      TweenSequenceItem(tween: Tween(begin: 1.2, end: 1.0), weight: 80),
    ]).animate(_controller);

    _controller.forward();
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
          left: widget.startPosition.dx - 50,
          top: widget.startPosition.dy + _positionAnimation.value,
          child: Opacity(
            opacity: _opacityAnimation.value,
            child: Transform.scale(
              scale: _scaleAnimation.value,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: widget.color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: widget.color, width: 2),
                  boxShadow: [
                    BoxShadow(
                      color: widget.color.withOpacity(0.5),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Text(
                  widget.text,
                  style: TextStyle(
                    fontSize: widget.fontSize,
                    fontWeight: FontWeight.bold,
                    color: widget.color,
                    shadows: [
                      Shadow(
                        color: widget.color.withOpacity(0.5),
                        blurRadius: 10,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

/// 🎆 CONFETTI EXPLOSION
/// For level ups and major achievements

class ConfettiExplosion extends StatefulWidget {
  final VoidCallback? onComplete;

  const ConfettiExplosion({Key? key, this.onComplete}) : super(key: key);

  @override
  _ConfettiExplosionState createState() => _ConfettiExplosionState();
}

class _ConfettiExplosionState extends State<ConfettiExplosion>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  final Random random = Random();

  @override
  void initState() {
    super.initState();
    _controllers = List.generate(
      100,
      (index) => AnimationController(
        vsync: this,
        duration: Duration(milliseconds: 2000 + random.nextInt(1000)),
      ),
    );

    // Stagger animations
    for (int i = 0; i < _controllers.length; i++) {
      Future.delayed(Duration(milliseconds: i * 10), () {
        if (mounted) _controllers[i].forward();
      });
    }

    // Call onComplete after all done
    Future.delayed(const Duration(milliseconds: 3500), () {
      widget.onComplete?.call();
    });
  }

  @override
  void dispose() {
    for (var controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: _controllers.asMap().entries.map((entry) {
        final index = entry.key;
        final controller = entry.value;
        
        final colors = [
          Colors.red,
          Colors.blue,
          Colors.green,
          Colors.yellow,
          Colors.purple,
          Colors.orange,
          Colors.pink,
        ];
        
        return AnimatedBuilder(
          animation: controller,
          builder: (context, child) {
            final progress = controller.value;
            
            // Start from top center
            final startX = MediaQuery.of(context).size.width / 2;
            final startY = MediaQuery.of(context).size.height / 3;
            
            // Random trajectory
            final angle = (index / _controllers.length) * 2 * pi + random.nextDouble();
            final distance = progress * 400;
            
            final x = startX + cos(angle) * distance + random.nextDouble() * 100 - 50;
            final y = startY + sin(angle) * distance * 0.5 + progress * progress * 300;
            
            final rotation = progress * 4 * pi;
            
            return Positioned(
              left: x,
              top: y,
              child: Transform.rotate(
                angle: rotation,
                child: Opacity(
                  opacity: 1 - progress,
                  child: Container(
                    width: 10,
                    height: 20,
                    decoration: BoxDecoration(
                      color: colors[index % colors.length],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
              ),
            );
          },
        );
      }).toList(),
    );
  }
}
