import 'package:flutter/material.dart';
import '../../theme/lokaah_theme.dart';
import '../../widgets/ui/side_navigation.dart';
import '../../widgets/ui/glass_card.dart';
import '../../widgets/gamification/components/stunning_xp_bar.dart';
import '../../providers/gamification_provider.dart';

/// 🏠 MAIN SHELL LAYOUT
/// NotebookLM-inspired three-pane layout
/// Desktop: SideNav | Content | RightPanel
/// Mobile: BottomNav with collapsible drawers

class MainShell extends StatefulWidget {
  const MainShell({Key? key}) : super(key: key);

  @override
  _MainShellState createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _selectedIndex = 0;
  bool _isRightPanelOpen = true;

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth > 1200;
    final isTablet = screenWidth > 768 && screenWidth <= 1200;
    final isMobile = screenWidth <= 768;

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      body: Row(
        children: [
          // Left Navigation (Desktop/Tablet)
          if (isDesktop || isTablet)
            SideNavigation(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (index) {
                setState(() => _selectedIndex = index);
              },
              isExpanded: isDesktop,
            ),

          // Main Content Area
          Expanded(
            child: Column(
              children: [
                // XP Bar (always visible)
                _buildXPBar(),

                // Main content
                Expanded(
                  child: Row(
                    children: [
                      // Center content
                      Expanded(
                        child: _buildMainContent(),
                      ),

                      // Right Panel (Desktop only)
                      if (isDesktop && _isRightPanelOpen)
                        _buildRightPanel(),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),

      // Mobile Bottom Navigation
      bottomNavigationBar: isMobile
          ? MobileBottomNav(
              selectedIndex: _selectedIndex,
              onDestinationSelected: (index) {
                setState(() => _selectedIndex = index);
              },
            )
          : null,

      // Mobile Right Panel as Drawer
      endDrawer: isMobile ? _buildRightPanelDrawer() : null,
    );
  }

  Widget _buildXPBar() {
    // Mock data - replace with actual provider
    return const StunningXPBar(
      level: 5,
      currentXP: 240,
      xpForNextLevel: 300,
      streak: 7,
      isOnFire: true,
      fireStreak: 5,
    );
  }

  Widget _buildMainContent() {
    final screens = [
      const HomeScreen(),
      const LearnScreen(),
      const VedaScreen(),
      const ProgressScreen(),
      const ProfileScreen(),
    ];

    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 300),
      child: screens[_selectedIndex],
    );
  }

  Widget _buildRightPanel() {
    return Container(
      width: 320,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(
          left: BorderSide(
            color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
          ),
        ),
      ),
      child: Column(
        children: [
          // Panel header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(
                  color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
                ),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'VEDA Assistant',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.more_vert, size: 20),
                  onPressed: () {},
                ),
              ],
            ),
          ),

          // Chat area
          Expanded(
            child: _buildVedaChat(),
          ),

          // Quick stats
          _buildQuickStats(),
        ],
      ),
    );
  }

  Widget _buildRightPanelDrawer() {
    return Drawer(
      width: MediaQuery.of(context).size.width * 0.85,
      child: _buildRightPanel(),
    );
  }

  Widget _buildVedaChat() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildVedaMessage(
          'Hi! I\'m VEDA, your AI tutor. What would you like to learn today?',
          isFirst: true,
        ),
        const SizedBox(height: 12),
        _buildSuggestionChip('Quadratic Equations'),
        const SizedBox(height: 8),
        _buildSuggestionChip('Trigonometry'),
        const SizedBox(height: 8),
        _buildSuggestionChip('Probability'),
      ],
    );
  }

  Widget _buildVedaMessage(String message, {bool isFirst = false}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            gradient: LokaahTheme.primaryGradient,
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Center(
            child: Text(
              '🧠',
              style: TextStyle(fontSize: 18),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: GlassCard(
            padding: const EdgeInsets.all(12),
            backgroundColor: LokaahTheme.primary.withOpacity(0.05),
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSuggestionChip(String label) {
    return Align(
      alignment: Alignment.centerLeft,
      child: GestureDetector(
        onTap: () {},
        child: Container(
          margin: const EdgeInsets.only(left: 48),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceVariant,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
            ),
          ),
          child: Text(
            label,
            style: Theme.of(context).textTheme.labelLarge,
          ),
        ),
      ),
    );
  }

  Widget _buildQuickStats() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
          ),
        ),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: StatCard(
                  label: 'Today',
                  value: '7/10',
                  subtitle: 'Questions',
                  icon: Icons.check_circle,
                  color: LokaahTheme.success,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: StatCard(
                  label: 'Streak',
                  value: '7 🔥',
                  subtitle: 'Days',
                  icon: Icons.local_fire_department,
                  color: LokaahTheme.fireOrange,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// 🏠 HOME SCREEN

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Greeting
          Text(
            'Good evening, Rahul! 👋',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'Ready to continue your math journey?',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 24),

          // Continue learning card
          GlassCard(
            isElevated: true,
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: LokaahTheme.primary.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Center(
                        child: Text('📐', style: TextStyle(fontSize: 24)),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Continue Learning',
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              color: Theme.of(context).colorScheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Trigonometry - Heights & Distances',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      onPressed: () {},
                      icon: const Icon(Icons.arrow_forward),
                      color: LokaahTheme.primary,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: 0.65,
                    backgroundColor: Theme.of(context).colorScheme.surfaceVariant,
                    valueColor: const AlwaysStoppedAnimation(LokaahTheme.primary),
                    minHeight: 8,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '65% complete • 12 questions solved',
                  style: Theme.of(context).textTheme.labelMedium,
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Recommended topics
          Text(
            'Recommended for You',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),

          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _buildTopicCard('📊', 'Statistics', 'Mean & Median', context),
              _buildTopicCard('📈', 'Algebra', 'Quadratic Eq', context),
              _buildTopicCard('🎯', 'Probability', 'Basic Concepts', context),
              _buildTopicCard('📐', 'Geometry', 'Circles', context),
            ],
          ),

          const SizedBox(height: 24),

          // Daily challenge
          GlassCard(
            backgroundColor: LokaahTheme.success.withOpacity(0.05),
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    gradient: LokaahTheme.successGradient,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(
                    Icons.emoji_events,
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
                        'Daily Challenge',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Solve 10 questions to earn +100 XP bonus',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                ElevatedButton(
                  onPressed: () {},
                  child: const Text('Start'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopicCard(
    String emoji,
    String title,
    String subtitle,
    BuildContext context,
  ) {
    return GestureDetector(
      onTap: () {},
      child: Container(
        width: 160,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 32)),
            const SizedBox(height: 12),
            Text(
              title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.labelMedium,
            ),
          ],
        ),
      ),
    );
  }
}

/// 📚 LEARN SCREEN

class LearnScreen extends StatelessWidget {
  const LearnScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Learn Screen'),
    );
  }
}

/// 🤖 VEDA SCREEN

class VedaScreen extends StatelessWidget {
  const VedaScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('VEDA Screen'),
    );
  }
}

/// 🏆 PROGRESS SCREEN

class ProgressScreen extends StatelessWidget {
  const ProgressScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Progress Screen'),
    );
  }
}

/// 👤 PROFILE SCREEN

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('Profile Screen'),
    );
  }
}
