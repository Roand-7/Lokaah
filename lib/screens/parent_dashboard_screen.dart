import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/gamification_provider.dart';

/// 👨‍👩‍👧 PARENT DASHBOARD
/// Gives parents visibility into child's progress
/// Builds trust through transparency

class ParentDashboardScreen extends ConsumerWidget {
  const ParentDashboardScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gamification = ref.watch(gamificationProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Parent Dashboard'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 👤 Child Profile Card
            _buildChildProfileCard(gamification),
            
            const SizedBox(height: 24),
            
            // 📊 Today's Activity
            _buildTodayActivityCard(gamification),
            
            const SizedBox(height: 24),
            
            // 📈 Weekly Progress Chart
            _buildWeeklyProgressChart(),
            
            const SizedBox(height: 24),
            
            // 🎯 Concept Mastery
            _buildConceptMasteryCard(gamification),
            
            const SizedBox(height: 24),
            
            // 🏆 Badges Earned
            _buildBadgesSection(gamification),
            
            const SizedBox(height: 24),
            
            // ⚠️ Areas Needing Attention
            _buildWeakAreasCard(gamification),
            
            const SizedBox(height: 24),
            
            // 📱 Trust Indicators
            _buildTrustIndicators(),
          ],
        ),
      ),
    );
  }

  Widget _buildChildProfileCard(GamificationState state) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            colors: [Colors.deepPurple.shade400, Colors.deepPurple.shade700],
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white,
                border: Border.all(color: Colors.amber, width: 3),
              ),
              child: Center(
                child: Text(
                  '${state.level}',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.deepPurple.shade700,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Rahul\'s Progress',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Level ${state.level} Math Wizard',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _buildStatChip('🔥 ${state.currentStreak} day streak'),
                      const SizedBox(width: 8),
                      _buildStatChip('⭐ ${state.totalXP} XP'),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatChip(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildTodayActivityCard(GamificationState state) {
    final accuracy = state.questionsToday > 0
        ? (state.correctToday / state.questionsToday * 100).toStringAsFixed(0)
        : '0';
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Today\'s Activity',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildActivityStat(
                  icon: '📝',
                  value: '${state.questionsToday}',
                  label: 'Questions',
                  color: Colors.blue,
                ),
                _buildActivityStat(
                  icon: '✅',
                  value: '${state.correctToday}',
                  label: 'Correct',
                  color: Colors.green,
                ),
                _buildActivityStat(
                  icon: '🎯',
                  value: '$accuracy%',
                  label: 'Accuracy',
                  color: Colors.orange,
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Daily goal progress
            LinearProgressIndicator(
              value: (state.correctToday / 10).clamp(0.0, 1.0),
              backgroundColor: Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(
                state.correctToday >= 10 ? Colors.green : Colors.blue,
              ),
              minHeight: 8,
            ),
            const SizedBox(height: 8),
            Text(
              state.correctToday >= 10
                  ? '🎉 Daily goal completed! Great job!'
                  : '${10 - state.correctToday} more to reach daily goal',
              style: TextStyle(
                fontSize: 12,
                color: state.correctToday >= 10 ? Colors.green : Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityStat({
    required String icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Column(
      children: [
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(icon, style: const TextStyle(fontSize: 28)),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }

  Widget _buildWeeklyProgressChart() {
    // Mock weekly data - replace with actual data
    final weekData = [
      DayProgress('Mon', 8),
      DayProgress('Tue', 12),
      DayProgress('Wed', 6),
      DayProgress('Thu', 15),
      DayProgress('Fri', 10),
      DayProgress('Sat', 20),
      DayProgress('Sun', 5),
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Weekly Activity',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Questions solved per day',
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: 25,
                  barTouchData: BarTouchData(enabled: false),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          final index = value.toInt();
                          if (index < 0 || index >= weekData.length) {
                            return const SizedBox.shrink();
                          }
                          return Text(
                            weekData[index].day,
                            style: const TextStyle(fontSize: 12),
                          );
                        },
                      ),
                    ),
                    leftTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  gridData: const FlGridData(show: false),
                  borderData: FlBorderData(show: false),
                  barGroups: weekData.asMap().entries.map((entry) {
                    return BarChartGroupData(
                      x: entry.key,
                      barRods: [
                        BarChartRodData(
                          toY: entry.value.questions.toDouble(),
                          color: Colors.deepPurple,
                          width: 20,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConceptMasteryCard(GamificationState state) {
    final concepts = state.conceptMastery.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Concept Mastery',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            if (concepts.isEmpty)
              const Center(
                child: Text(
                  'No data yet. Keep practicing!',
                  style: TextStyle(color: Colors.grey),
                ),
              )
            else
              ...concepts.take(5).map((concept) {
                final progress = (concept.value / 500).clamp(0.0, 1.0);
                final isMastered = concept.value >= 500;
                
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            concept.key,
                            style: const TextStyle(fontWeight: FontWeight.w500),
                          ),
                          Text(
                            isMastered ? 'Mastered 🏆' : '${concept.value}/500 XP',
                            style: TextStyle(
                              fontSize: 12,
                              color: isMastered ? Colors.green : Colors.grey.shade600,
                              fontWeight: isMastered ? FontWeight.bold : FontWeight.normal,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      LinearProgressIndicator(
                        value: progress,
                        backgroundColor: Colors.grey.shade200,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          isMastered ? Colors.green : Colors.deepPurple,
                        ),
                        minHeight: 6,
                      ),
                    ],
                  ),
                );
              }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildBadgesSection(GamificationState state) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Badges Earned',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  '${state.unlockedBadges.length}/${allBadges.length}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (state.unlockedBadges.isEmpty)
              const Center(
                child: Text(
                  'No badges yet. Complete questions to earn them!',
                  style: TextStyle(color: Colors.grey),
                ),
              )
            else
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: state.unlockedBadges.map((badgeId) {
                  final badge = allBadges.firstWhere(
                    (b) => b.id == badgeId,
                    orElse: () => Badge(
                      id: badgeId,
                      name: 'Unknown',
                      description: '',
                      emoji: '🏅',
                      condition: (_) => false,
                    ),
                  );
                  
                  return Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.amber.shade50,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.amber.shade200),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(badge.emoji, style: const TextStyle(fontSize: 20)),
                        const SizedBox(width: 8),
                        Text(
                          badge.name,
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeakAreasCard(GamificationState state) {
    // Find concepts with low XP
    final weakAreas = state.conceptMastery.entries
        .where((e) => e.value < 100)
        .map((e) => e.key)
        .toList();

    if (weakAreas.isEmpty) return const SizedBox.shrink();

    return Card(
      color: Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning, color: Colors.orange.shade700),
                const SizedBox(width: 8),
                Text(
                  'Areas Needing Practice',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange.shade900,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...weakAreas.map((area) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Icon(Icons.arrow_right, color: Colors.orange.shade700),
                  Text(
                    area,
                    style: TextStyle(color: Colors.orange.shade900),
                  ),
                ],
              ),
            )).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildTrustIndicators() {
    return Card(
      color: Colors.green.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Why Parents Trust LOKAAH',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildTrustItem(
              icon: Icons.check_circle,
              text: '100% Math Accuracy - Python-verified calculations',
            ),
            _buildTrustItem(
              icon: Icons.check_circle,
              text: 'CBSE Aligned - Follows official curriculum',
            ),
            _buildTrustItem(
              icon: Icons.check_circle,
              text: 'No Hallucinations - AI creates scenarios, Python solves',
            ),
            _buildTrustItem(
              icon: Icons.check_circle,
              text: 'Screen Time Limits - Healthy usage reminders',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTrustItem({required IconData icon, required String text}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.green.shade700),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 13,
                color: Colors.green.shade900,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class DayProgress {
  final String day;
  final int questions;

  DayProgress(this.day, this.questions);
}
