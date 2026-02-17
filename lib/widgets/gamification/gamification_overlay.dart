import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'components/stunning_xp_bar.dart';
import 'components/level_up_celebration.dart';
import 'components/streak_animations.dart';
import 'effects/particle_system.dart';
import '../../providers/gamification_provider.dart';

/// 🎮 GAMIFICATION OVERLAY
/// Wraps the entire app with gamification effects
/// Handles all celebrations, toasts, and visual feedback

class GamificationOverlay extends ConsumerStatefulWidget {
  final Widget child;

  const GamificationOverlay({
    Key? key,
    required this.child,
  }) : super(key: key);

  @override
  _GamificationOverlayState createState() => _GamificationOverlayState();
}

class _GamificationOverlayState extends ConsumerState<GamificationOverlay> {
  final List<Widget> _activeEffects = [];

  @override
  Widget build(BuildContext context) {
    final gamification = ref.watch(gamificationProvider);
    
    // Listen for XP gains
    ref.listen<GamificationState>(gamificationProvider, (previous, current) {
      if (previous != null && current.totalXP > previous.totalXP) {
        _showXPGain(
          current.totalXP - previous.totalXP,
          gamification.isOnFire,
          gamification.fireStreak,
        );
      }
    });

    return Stack(
      children: [
        // Main app content
        widget.child,
        
        // Fixed XP Bar at top
        Positioned(
          top: 0,
          left: 0,
          right: 0,
          child: StunningXPBar(
            level: gamification.level,
            currentXP: gamification.xpInCurrentLevel,
            xpForNextLevel: gamification.xpForNextLevel,
            streak: gamification.currentStreak,
            isOnFire: gamification.isOnFire,
            fireStreak: gamification.fireStreak,
          ),
        ),
        
        // Active effects overlay
        ..._activeEffects,
      ],
    );
  }

  void _showXPGain(int xp, bool isOnFire, int fireStreak) {
    // Add floating text effect
    setState(() {
      _activeEffects.add(
        FloatingText(
          text: '+$xp XP',
          startPosition: Offset(
            MediaQuery.of(context).size.width / 2,
            MediaQuery.of(context).size.height / 2,
          ),
          color: isOnFire ? Colors.orange : Colors.green,
        ),
      );
    });

    // Remove after animation
    Future.delayed(const Duration(milliseconds: 2000), () {
      if (mounted) {
        setState(() {
          if (_activeEffects.isNotEmpty) {
            _activeEffects.removeAt(0);
          }
        });
      }
    });
  }

  void showLevelUp(int level, int xpGained) {
    setState(() {
      _activeEffects.add(
        LevelUpCelebration(
          newLevel: level,
          xpGained: xpGained,
          onComplete: () {
            setState(() {
              _activeEffects.removeWhere(
                (e) => e is LevelUpCelebration,
              );
            });
          },
        ),
      );
    });
  }

  void showBadgeUnlock(String name, String emoji, String description) {
    setState(() {
      _activeEffects.add(
        BadgeUnlockCelebration(
          badgeName: name,
          badgeEmoji: emoji,
          badgeDescription: description,
          onComplete: () {
            setState(() {
              _activeEffects.removeWhere(
                (e) => e is BadgeUnlockCelebration,
              );
            });
          },
        ),
      );
    });
  }
}

/// 🎯 GAMIFICATION BOTTOM SHEET
/// Shows detailed stats and achievements

class GamificationBottomSheet extends ConsumerWidget {
  const GamificationBottomSheet({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(gamificationProvider);

    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
      ),
      child: Column(
        children: [
          // Handle bar
          Container(
            margin: const EdgeInsets.only(top: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Colors.purple.shade400,
                        Colors.deepPurple.shade700,
                      ],
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.purple.withOpacity(0.3),
                        blurRadius: 20,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  child: Center(
                    child: Text(
                      '${state.level}',
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Your Progress',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${state.totalXP} Total XP',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Stats Grid
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                _buildStatCard(
                  icon: '🔥',
                  value: '${state.currentStreak}',
                  label: 'Day Streak',
                  color: Colors.orange,
                ),
                const SizedBox(width: 12),
                _buildStatCard(
                  icon: '✅',
                  value: '${state.correctToday}',
                  label: 'Correct Today',
                  color: Colors.green,
                ),
                const SizedBox(width: 12),
                _buildStatCard(
                  icon: '🏆',
                  value: '${state.unlockedBadges.length}',
                  label: 'Badges',
                  color: Colors.purple,
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Daily Goal
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: DailyGoalProgress(
              current: state.correctToday,
              target: 10,
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Badges Section
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.grey.shade50,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(30),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Your Badges',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${state.unlockedBadges.length}/15',
                        style: TextStyle(
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Expanded(
                    child: GridView.builder(
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 3,
                        childAspectRatio: 0.8,
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                      ),
                      itemCount: allBadges.length,
                      itemBuilder: (context, index) {
                        final badge = allBadges[index];
                        final isUnlocked = state.unlockedBadges.contains(badge.id);
                        
                        return _buildBadgeItem(badge, isUnlocked);
                      },
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

  Widget _buildStatCard({
    required String icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Expanded(
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
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Text(icon, style: const TextStyle(fontSize: 24)),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBadgeItem(Badge badge, bool isUnlocked) {
    return Container(
      decoration: BoxDecoration(
        color: isUnlocked ? Colors.white : Colors.grey.shade200,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isUnlocked ? Colors.amber : Colors.grey.shade300,
          width: isUnlocked ? 2 : 1,
        ),
        boxShadow: isUnlocked
            ? [
                BoxShadow(
                  color: Colors.amber.withOpacity(0.2),
                  blurRadius: 8,
                ),
              ]
            : null,
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            badge.emoji,
            style: TextStyle(
              fontSize: isUnlocked ? 32 : 24,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            badge.name,
            style: TextStyle(
              fontSize: 11,
              fontWeight: isUnlocked ? FontWeight.bold : FontWeight.normal,
              color: isUnlocked ? Colors.black87 : Colors.grey,
            ),
            textAlign: TextAlign.center,
          ),
          if (isUnlocked)
            Container(
              margin: const EdgeInsets.only(top: 4),
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.green.shade100,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '+${badge.xpBonus}',
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.green.shade700,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// Button to open gamification panel
class GamificationFAB extends ConsumerWidget {
  const GamificationFAB({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(gamificationProvider);
    
    return FloatingActionButton.extended(
      onPressed: () {
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          backgroundColor: Colors.transparent,
          builder: (context) => const GamificationBottomSheet(),
        );
      },
      backgroundColor: Colors.purple,
      icon: Stack(
        children: [
          const Icon(Icons.emoji_events, color: Colors.white),
          if (state.isOnFire)
            Positioned(
              right: -2,
              top: -2,
              child: Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: Colors.orange,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 1),
                ),
              ),
            ),
        ],
      ),
      label: Text(
        'Lvl ${state.level}',
        style: const TextStyle(color: Colors.white),
      ),
    );
  }
}
