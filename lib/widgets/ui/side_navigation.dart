import 'package:flutter/material.dart';
import '../../theme/lokaah_theme.dart';

/// 🧭 SIDE NAVIGATION (Desktop/Tablet)
/// NotebookLM-style compact side nav

class SideNavigation extends StatelessWidget {
  final int selectedIndex;
  final Function(int) onDestinationSelected;
  final bool isExpanded;

  const SideNavigation({
    Key? key,
    required this.selectedIndex,
    required this.onDestinationSelected,
    this.isExpanded = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    final destinations = [
      _NavDestination(
        icon: Icons.home_outlined,
        selectedIcon: Icons.home_rounded,
        label: 'Home',
        emoji: '🏠',
      ),
      _NavDestination(
        icon: Icons.menu_book_outlined,
        selectedIcon: Icons.menu_book_rounded,
        label: 'Learn',
        emoji: '📚',
      ),
      _NavDestination(
        icon: Icons.psychology_outlined,
        selectedIcon: Icons.psychology_rounded,
        label: 'VEDA',
        emoji: '🤖',
      ),
      _NavDestination(
        icon: Icons.emoji_events_outlined,
        selectedIcon: Icons.emoji_events_rounded,
        label: 'Progress',
        emoji: '🏆',
      ),
      _NavDestination(
        icon: Icons.person_outlined,
        selectedIcon: Icons.person_rounded,
        label: 'Profile',
        emoji: '👤',
      ),
    ];

    return Container(
      width: isExpanded ? 200 : 70,
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(
          right: BorderSide(
            color: theme.colorScheme.outline.withOpacity(0.5),
          ),
        ),
      ),
      child: Column(
        children: [
          // Logo area
          Container(
            height: 70,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
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
                      'L',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ),
                ),
                if (isExpanded) ...[
                  const SizedBox(width: 12),
                  Text(
                    'LOKAAH',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1,
                    ),
                  ),
                ],
              ],
            ),
          ),

          const Divider(height: 1),

          // Navigation items
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 8),
              itemCount: destinations.length,
              itemBuilder: (context, index) {
                final dest = destinations[index];
                final isSelected = selectedIndex == index;

                return _NavItem(
                  destination: dest,
                  isSelected: isSelected,
                  isExpanded: isExpanded,
                  onTap: () => onDestinationSelected(index),
                );
              },
            ),
          ),

          const Divider(height: 1),

          // Bottom actions
          Padding(
            padding: const EdgeInsets.all(12),
            child: _buildThemeToggle(context, isExpanded),
          ),
        ],
      ),
    );
  }

  Widget _buildThemeToggle(BuildContext context, bool isExpanded) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return GestureDetector(
      onTap: () {
        // Toggle theme
      },
      child: Container(
        padding: EdgeInsets.symmetric(
          horizontal: isExpanded ? 12 : 0,
          vertical: 12,
        ),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceVariant,
          borderRadius: BorderRadius.circular(10),
        ),
        child: isExpanded
            ? Row(
                children: [
                  Icon(
                    isDark ? Icons.dark_mode : Icons.light_mode,
                    size: 20,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    isDark ? 'Dark Mode' : 'Light Mode',
                    style: theme.textTheme.labelMedium,
                  ),
                  const Spacer(),
                  Icon(
                    Icons.chevron_right,
                    size: 18,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ],
              )
            : Center(
                child: Icon(
                  isDark ? Icons.dark_mode : Icons.light_mode,
                  size: 20,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
      ),
    );
  }
}

class _NavDestination {
  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final String emoji;

  _NavDestination({
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.emoji,
  });
}

class _NavItem extends StatelessWidget {
  final _NavDestination destination;
  final bool isSelected;
  final bool isExpanded;
  final VoidCallback onTap;

  const _NavItem({
    required this.destination,
    required this.isSelected,
    required this.isExpanded,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
        padding: EdgeInsets.symmetric(
          horizontal: isExpanded ? 12 : 0,
          vertical: 10,
        ),
        decoration: BoxDecoration(
          color: isSelected
              ? LokaahTheme.primary.withOpacity(0.1)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
        ),
        child: isExpanded
            ? Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: isSelected
                          ? LokaahTheme.primary.withOpacity(0.2)
                          : theme.colorScheme.surfaceVariant,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Center(
                      child: Text(
                        destination.emoji,
                        style: const TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    destination.label,
                    style: theme.textTheme.labelLarge?.copyWith(
                      color: isSelected
                          ? LokaahTheme.primary
                          : theme.colorScheme.onSurface,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                    ),
                  ),
                ],
              )
            : Center(
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: isSelected
                        ? LokaahTheme.primary.withOpacity(0.2)
                        : theme.colorScheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Center(
                    child: Text(
                      destination.emoji,
                      style: const TextStyle(fontSize: 18),
                    ),
                  ),
                ),
              ),
      ),
    );
  }
}

/// 📱 BOTTOM NAVIGATION (Mobile)

class MobileBottomNav extends StatelessWidget {
  final int selectedIndex;
  final Function(int) onDestinationSelected;

  const MobileBottomNav({
    Key? key,
    required this.selectedIndex,
    required this.onDestinationSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        border: Border(
          top: BorderSide(
            color: theme.colorScheme.outline.withOpacity(0.3),
          ),
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _MobileNavItem(
                icon: Icons.home_outlined,
                selectedIcon: Icons.home_rounded,
                label: 'Home',
                emoji: '🏠',
                isSelected: selectedIndex == 0,
                onTap: () => onDestinationSelected(0),
              ),
              _MobileNavItem(
                icon: Icons.menu_book_outlined,
                selectedIcon: Icons.menu_book_rounded,
                label: 'Learn',
                emoji: '📚',
                isSelected: selectedIndex == 1,
                onTap: () => onDestinationSelected(1),
              ),
              _MobileNavItem(
                icon: Icons.psychology_outlined,
                selectedIcon: Icons.psychology_rounded,
                label: 'VEDA',
                emoji: '🤖',
                isSelected: selectedIndex == 2,
                onTap: () => onDestinationSelected(2),
                isCenter: true,
              ),
              _MobileNavItem(
                icon: Icons.emoji_events_outlined,
                selectedIcon: Icons.emoji_events_rounded,
                label: 'Win',
                emoji: '🏆',
                isSelected: selectedIndex == 3,
                onTap: () => onDestinationSelected(3),
              ),
              _MobileNavItem(
                icon: Icons.person_outlined,
                selectedIcon: Icons.person_rounded,
                label: 'Me',
                emoji: '👤',
                isSelected: selectedIndex == 4,
                onTap: () => onDestinationSelected(4),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _MobileNavItem extends StatelessWidget {
  final IconData icon;
  final IconData selectedIcon;
  final String label;
  final String emoji;
  final bool isSelected;
  final bool isCenter;
  final VoidCallback onTap;

  const _MobileNavItem({
    required this.icon,
    required this.selectedIcon,
    required this.label,
    required this.emoji,
    required this.isSelected,
    this.isCenter = false,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected && !isCenter
              ? LokaahTheme.primary.withOpacity(0.1)
              : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            isCenter
                ? Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      gradient: LokaahTheme.primaryGradient,
                      borderRadius: BorderRadius.circular(14),
                      boxShadow: LokaahTheme.glowShadow,
                    ),
                    child: Center(
                      child: Text(
                        emoji,
                        style: const TextStyle(fontSize: 24),
                      ),
                    ),
                  )
                : Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      color: isSelected
                          ? LokaahTheme.primary.withOpacity(0.2)
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Center(
                      child: Text(
                        emoji,
                        style: const TextStyle(fontSize: 20),
                      ),
                    ),
                  ),
            const SizedBox(height: 4),
            Text(
              label,
              style: theme.textTheme.labelSmall?.copyWith(
                color: isSelected || isCenter
                    ? LokaahTheme.primary
                    : theme.colorScheme.onSurfaceVariant,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
