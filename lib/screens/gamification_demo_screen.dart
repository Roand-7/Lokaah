import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../widgets/gamification/components/stunning_xp_bar.dart';
import '../widgets/gamification/components/level_up_celebration.dart';
import '../widgets/gamification/components/streak_animations.dart';
import '../widgets/gamification/effects/particle_system.dart';

/// 🎮 GAMIFICATION DEMO SCREEN
/// Showcase all visual effects in one place

class GamificationDemoScreen extends StatefulWidget {
  const GamificationDemoScreen({Key? key}) : super(key: key);

  @override
  _GamificationDemoScreenState createState() => _GamificationDemoScreenState();
}

class _GamificationDemoScreenState extends State<GamificationDemoScreen> {
  int _demoLevel = 5;
  int _demoXP = 240;
  int _demoStreak = 7;
  bool _isOnFire = true;
  int _fireStreak = 5;
  int _combo = 0;
  bool _showParticles = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A2E),
      body: Stack(
        children: [
          // Background gradient
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  const Color(0xFF1A1A2E),
                  const Color(0xFF16213E),
                  const Color(0xFF0F3460),
                ],
              ),
            ),
          ),
          
          // Particles overlay
          if (_showParticles)
            ParticleSystem(
              particleCount: 60,
              color: Colors.amber,
              onComplete: () {
                setState(() => _showParticles = false);
              },
            ),
          
          // Main content
          SafeArea(
            child: Column(
              children: [
                // Demo XP Bar
                StunningXPBar(
                  level: _demoLevel,
                  currentXP: _demoXP,
                  xpForNextLevel: 300,
                  streak: _demoStreak,
                  isOnFire: _isOnFire,
                  fireStreak: _fireStreak,
                ),
                
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        const SizedBox(height: 20),
                        
                        _buildSectionTitle('🔥 Streak Animations'),
                        const SizedBox(height: 16),
                        FireStreakWidget(
                          streak: _fireStreak,
                          isActive: _isOnFire,
                        ),
                        
                        const SizedBox(height: 32),
                        
                        _buildSectionTitle('⚡ Combo Counter'),
                        const SizedBox(height: 16),
                        ComboCounter(combo: _combo),
                        
                        const SizedBox(height: 32),
                        
                        _buildSectionTitle('🎯 Daily Goal'),
                        const SizedBox(height: 16),
                        DailyGoalProgress(
                          current: 7,
                          target: 10,
                        ),
                        
                        const SizedBox(height: 32),
                        
                        _buildSectionTitle('🎮 Interactive Demo'),
                        const SizedBox(height: 16),
                        _buildDemoControls(),
                        
                        const SizedBox(height: 32),
                        
                        _buildSectionTitle('🎨 Visual Effects'),
                        const SizedBox(height: 16),
                        _buildEffectButtons(),
                        
                        const SizedBox(height: 40),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: Colors.white,
      ),
    );
  }

  Widget _buildDemoControls() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withOpacity(0.1)),
      ),
      child: Column(
        children: [
          // XP Controls
          Row(
            children: [
              Expanded(
                child: _buildControlButton(
                  icon: Icons.add,
                  label: 'Gain XP',
                  color: Colors.green,
                  onTap: () {
                    setState(() {
                      _demoXP += 25;
                      _showParticles = true;
                    });
                    HapticFeedback.lightImpact();
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildControlButton(
                  icon: Icons.upgrade,
                  label: 'Level Up',
                  color: Colors.purple,
                  onTap: () {
                    _showLevelUpDialog();
                    HapticFeedback.heavyImpact();
                  },
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Streak Controls
          Row(
            children: [
              Expanded(
                child: _buildControlButton(
                  icon: Icons.local_fire_department,
                  label: 'Fire Streak',
                  color: Colors.orange,
                  onTap: () {
                    setState(() {
                      _isOnFire = !_isOnFire;
                      _fireStreak = _isOnFire ? 5 : 0;
                    });
                    HapticFeedback.mediumImpact();
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildControlButton(
                  icon: Icons.flash_on,
                  label: 'Combo',
                  color: Colors.blue,
                  onTap: () {
                    setState(() {
                      _combo = (_combo + 1) % 8;
                    });
                    HapticFeedback.mediumImpact();
                  },
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // Reset
          _buildControlButton(
            icon: Icons.refresh,
            label: 'Reset Demo',
            color: Colors.grey,
            onTap: () {
              setState(() {
                _demoLevel = 5;
                _demoXP = 240;
                _demoStreak = 7;
                _isOnFire = true;
                _fireStreak = 5;
                _combo = 0;
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              color.withOpacity(0.8),
              color,
            ],
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.4),
              blurRadius: 10,
              spreadRadius: 2,
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white),
            const SizedBox(width: 8),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEffectButtons() {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        _buildEffectButton(
          label: 'Level Up Celebration',
          onTap: () => _showLevelUpDialog(),
        ),
        _buildEffectButton(
          label: 'Badge Unlock',
          onTap: () => _showBadgeDialog(),
        ),
        _buildEffectButton(
          label: 'Particles',
          onTap: () => setState(() => _showParticles = true),
        ),
        _buildEffectButton(
          label: 'Achievement Toast',
          onTap: () => _showToast(),
        ),
      ],
    );
  }

  Widget _buildEffectButton({
    required String label,
    required VoidCallback onTap,
  }) {
    return ElevatedButton(
      onPressed: onTap,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.white.withOpacity(0.1),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: Colors.white.withOpacity(0.2)),
        ),
      ),
      child: Text(label),
    );
  }

  void _showLevelUpDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => LevelUpCelebration(
        newLevel: _demoLevel + 1,
        xpGained: 150,
        onComplete: () {
          Navigator.pop(context);
          setState(() {
            _demoLevel++;
            _demoXP = 50;
          });
        },
      ),
    );
  }

  void _showBadgeDialog() {
    final badges = [
      ('Speed Demon', '⚡', 'Solve 5 questions under 60s'),
      ('Perfect Score', '💯', 'Get 5 correct in a row'),
      ('Week Warrior', '⚡', '7-day streak'),
      ('Trig Master', '📐', 'Master Trigonometry'),
    ];
    
    final badge = badges[DateTime.now().millisecond % badges.length];
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => BadgeUnlockCelebration(
        badgeName: badge.$1,
        badgeEmoji: badge.$2,
        badgeDescription: badge.$3,
        onComplete: () => Navigator.pop(context),
      ),
    );
  }

  void _showToast() {
    final overlay = Overlay.of(context);
    late OverlayEntry entry;
    
    entry = OverlayEntry(
      builder: (context) => AchievementToast(
        title: '3-Day Streak! 🔥',
        subtitle: 'You\'re on fire! Keep it up!',
        icon: Icons.local_fire_department,
        color: Colors.orange.shade700,
        onDismiss: () => entry.remove(),
      ),
    );
    
    overlay.insert(entry);
  }
}

/// Achievement Toast for demo
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

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 4000),
    );
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
        final slideValue = Tween<Offset>(
          begin: const Offset(0, -2),
          end: Offset.zero,
        ).animate(CurvedAnimation(
          parent: _controller,
          curve: const Interval(0, 0.2, curve: Curves.elasticOut),
        )).value;

        final opacityValue = TweenSequence<double>([
          TweenSequenceItem(tween: Tween(begin: 0.0, end: 1.0), weight: 10),
          TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.0), weight: 80),
          TweenSequenceItem(tween: Tween(begin: 1.0, end: 0.0), weight: 10),
        ]).animate(_controller).value;

        return Positioned(
          top: 100,
          left: 20,
          right: 20,
          child: SlideTransition(
            position: AlwaysStoppedAnimation(slideValue),
            child: Opacity(
              opacity: opacityValue,
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [widget.color, widget.color.withOpacity(0.8)],
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: widget.color.withOpacity(0.4),
                      blurRadius: 20,
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
                      child: Icon(widget.icon, color: Colors.white, size: 28),
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
