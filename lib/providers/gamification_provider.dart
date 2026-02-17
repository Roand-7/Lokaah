import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:math';

/// 🎮 GAMIFICATION SYSTEM
/// Makes the "struggle" feel rewarding like Duolingo

// ======================= STATE CLASSES =======================

class GamificationState {
  final int totalXP;
  final int currentStreak;
  final int longestStreak;
  final int level;
  final double levelProgress; // 0.0 to 1.0
  final List<String> unlockedBadges;
  final Map<String, int> conceptMastery; // concept -> XP
  final DateTime? lastActiveDate;
  final int questionsToday;
  final int correctToday;
  final bool isOnFire; // 3+ correct in a row
  final int fireStreak;

  GamificationState({
    this.totalXP = 0,
    this.currentStreak = 0,
    this.longestStreak = 0,
    this.level = 1,
    this.levelProgress = 0.0,
    this.unlockedBadges = const [],
    this.conceptMastery = const {},
    this.lastActiveDate,
    this.questionsToday = 0,
    this.correctToday = 0,
    this.isOnFire = false,
    this.fireStreak = 0,
  });

  GamificationState copyWith({
    int? totalXP,
    int? currentStreak,
    int? longestStreak,
    int? level,
    double? levelProgress,
    List<String>? unlockedBadges,
    Map<String, int>? conceptMastery,
    DateTime? lastActiveDate,
    int? questionsToday,
    int? correctToday,
    bool? isOnFire,
    int? fireStreak,
  }) {
    return GamificationState(
      totalXP: totalXP ?? this.totalXP,
      currentStreak: currentStreak ?? this.currentStreak,
      longestStreak: longestStreak ?? this.longestStreak,
      level: level ?? this.level,
      levelProgress: levelProgress ?? this.levelProgress,
      unlockedBadges: unlockedBadges ?? this.unlockedBadges,
      conceptMastery: conceptMastery ?? this.conceptMastery,
      lastActiveDate: lastActiveDate ?? this.lastActiveDate,
      questionsToday: questionsToday ?? this.questionsToday,
      correctToday: correctToday ?? this.correctToday,
      isOnFire: isOnFire ?? this.isOnFire,
      fireStreak: fireStreak ?? this.fireStreak,
    );
  }

  // XP needed for next level = level * 100
  int get xpForNextLevel => level * 100;
  int get xpInCurrentLevel => totalXP - ((level - 1) * (level) * 50);

  Map<String, dynamic> toJson() => {
    'totalXP': totalXP,
    'currentStreak': currentStreak,
    'longestStreak': longestStreak,
    'level': level,
    'unlockedBadges': unlockedBadges,
    'conceptMastery': conceptMastery,
    'lastActiveDate': lastActiveDate?.toIso8601String(),
    'questionsToday': questionsToday,
    'correctToday': correctToday,
    'fireStreak': fireStreak,
  };

  factory GamificationState.fromJson(Map<String, dynamic> json) {
    return GamificationState(
      totalXP: json['totalXP'] ?? 0,
      currentStreak: json['currentStreak'] ?? 0,
      longestStreak: json['longestStreak'] ?? 0,
      level: json['level'] ?? 1,
      unlockedBadges: List<String>.from(json['unlockedBadges'] ?? []),
      conceptMastery: Map<String, int>.from(json['conceptMastery'] ?? {}),
      lastActiveDate: json['lastActiveDate'] != null 
          ? DateTime.parse(json['lastActiveDate']) 
          : null,
      questionsToday: json['questionsToday'] ?? 0,
      correctToday: json['correctToday'] ?? 0,
      fireStreak: json['fireStreak'] ?? 0,
    );
  }
}

// ======================= BADGE DEFINITIONS =======================

class Badge {
  final String id;
  final String name;
  final String description;
  final String emoji;
  final int xpBonus;
  final bool Function(GamificationState) condition;

  Badge({
    required this.id,
    required this.name,
    required this.description,
    required this.emoji,
    this.xpBonus = 0,
    required this.condition,
  });
}

final List<Badge> allBadges = [
  // Streak Badges
  Badge(
    id: 'first_step',
    name: 'First Step',
    description: 'Complete your first question',
    emoji: '👶',
    xpBonus: 10,
    condition: (s) => s.totalXP >= 10,
  ),
  Badge(
    id: 'three_day_streak',
    name: 'On a Roll',
    description: '3-day streak',
    emoji: '🔥',
    xpBonus: 50,
    condition: (s) => s.currentStreak >= 3,
  ),
  Badge(
    id: 'week_warrior',
    name: 'Week Warrior',
    description: '7-day streak',
    emoji: '⚡',
    xpBonus: 150,
    condition: (s) => s.currentStreak >= 7,
  ),
  Badge(
    id: 'month_master',
    name: 'Month Master',
    description: '30-day streak',
    emoji: '🏆',
    xpBonus: 1000,
    condition: (s) => s.currentStreak >= 30,
  ),
  
  // Achievement Badges
  Badge(
    id: 'perfect_score',
    name: 'Perfect Score',
    description: '5 correct answers in a row',
    emoji: '💯',
    xpBonus: 100,
    condition: (s) => s.fireStreak >= 5,
  ),
  Badge(
    id: 'night_owl',
    name: 'Night Owl',
    description: 'Practice after 10 PM',
    emoji: '🦉',
    xpBonus: 25,
    condition: (s) => false,
  ),
  Badge(
    id: 'early_bird',
    name: 'Early Bird',
    description: 'Practice before 7 AM',
    emoji: '🌅',
    xpBonus: 25,
    condition: (s) => false,
  ),
  Badge(
    id: 'math_wizard',
    name: 'Math Wizard',
    description: 'Reach Level 10',
    emoji: '🧙',
    xpBonus: 500,
    condition: (s) => s.level >= 10,
  ),
  Badge(
    id: 'trig_master',
    name: 'Trig Master',
    description: 'Master Trigonometry (500 XP)',
    emoji: '📐',
    xpBonus: 200,
    condition: (s) => (s.conceptMastery['trigonometry'] ?? 0) >= 500,
  ),
  Badge(
    id: 'algebra_ace',
    name: 'Algebra Ace',
    description: 'Master Algebra (500 XP)',
    emoji: '📊',
    xpBonus: 200,
    condition: (s) => (s.conceptMastery['algebra'] ?? 0) >= 500,
  ),
];

// ======================= NOTIFIER =======================

class GamificationNotifier extends StateNotifier<GamificationState> {
  SharedPreferences? _prefs;
  static const String _storageKey = 'gamification_data';

  GamificationNotifier() : super(GamificationState()) {
    _loadState();
  }

  Future<void> _loadState() async {
    _prefs = await SharedPreferences.getInstance();
    final String? saved = _prefs?.getString(_storageKey);
    
    if (saved != null) {
      try {
        final data = jsonDecode(saved);
        final loaded = GamificationState.fromJson(data);
        
        final now = DateTime.now();
        final lastActive = loaded.lastActiveDate;
        
        int newStreak = loaded.currentStreak;
        if (lastActive != null) {
          final daysSince = now.difference(lastActive).inDays;
          if (daysSince > 1) {
            newStreak = 0;
          }
        }
        
        final isNewDay = lastActive == null || 
            now.day != lastActive.day || 
            now.month != lastActive.month;
        
        state = loaded.copyWith(
          currentStreak: newStreak,
          questionsToday: isNewDay ? 0 : loaded.questionsToday,
          correctToday: isNewDay ? 0 : loaded.correctToday,
        );
      } catch (e) {
        print('Error loading gamification: $e');
      }
    }
  }

  Future<void> _saveState() async {
    if (_prefs != null) {
      await _prefs!.setString(_storageKey, jsonEncode(state.toJson()));
    }
  }

  Future<XPGainResult> addCorrectAnswer({
    required String concept,
    required int difficulty,
    required int attempts,
    required int timeSeconds,
  }) async {
    int xp = 10 * difficulty;
    
    if (timeSeconds < 60) xp += 5;
    if (attempts == 1) xp += 10;
    
    final newFireStreak = state.fireStreak + 1;
    if (newFireStreak >= 3) xp += 5 * newFireStreak;
    
    final newTotalXP = state.totalXP + xp;
    final newLevel = _calculateLevel(newTotalXP);
    final newLevelProgress = _calculateLevelProgress(newTotalXP, newLevel);
    
    final newConceptMastery = Map<String, int>.from(state.conceptMastery);
    newConceptMastery[concept] = (newConceptMastery[concept] ?? 0) + xp;
    
    final now = DateTime.now();
    final lastActive = state.lastActiveDate;
    int newStreak = state.currentStreak;
    
    if (lastActive == null || now.difference(lastActive).inDays >= 1) {
      if (lastActive == null || now.difference(lastActive).inDays == 1) {
        newStreak += 1;
      } else {
        newStreak = 1;
      }
    }
    
    final newState = state.copyWith(
      totalXP: newTotalXP,
      level: newLevel,
      levelProgress: newLevelProgress,
      conceptMastery: newConceptMastery,
      currentStreak: newStreak,
      longestStreak: newStreak > state.longestStreak ? newStreak : state.longestStreak,
      lastActiveDate: now,
      questionsToday: state.questionsToday + 1,
      correctToday: state.correctToday + 1,
      isOnFire: newFireStreak >= 3,
      fireStreak: newFireStreak,
    );
    
    final newBadges = <Badge>[];
    for (final badge in allBadges) {
      if (!state.unlockedBadges.contains(badge.id) && badge.condition(newState)) {
        newBadges.add(badge);
      }
    }
    
    final allBadgesList = [...state.unlockedBadges, ...newBadges.map((b) => b.id)];
    
    state = newState.copyWith(unlockedBadges: allBadgesList);
    await _saveState();
    
    return XPGainResult(
      xpGained: xp,
      newTotalXP: newTotalXP,
      leveledUp: newLevel > state.level,
      newLevel: newLevel,
      newBadges: newBadges,
      isOnFire: newFireStreak >= 3,
      fireStreak: newFireStreak,
    );
  }

  Future<void> addIncorrectAnswer() async {
    state = state.copyWith(
      fireStreak: 0,
      isOnFire: false,
      questionsToday: state.questionsToday + 1,
    );
    await _saveState();
  }

  int _calculateLevel(int totalXP) {
    final level = ((sqrt(100 + 8 * totalXP) - 10) / 2).floor() + 1;
    return max(1, level);
  }

  double _calculateLevelProgress(int totalXP, int level) {
    final xpForCurrentLevel = ((level - 1) * (level) * 50).toInt();
    final xpForNextLevel = (level * (level + 1) * 50).toInt();
    final xpInLevel = totalXP - xpForCurrentLevel;
    final xpNeeded = xpForNextLevel - xpForCurrentLevel;
    return (xpInLevel / xpNeeded).clamp(0.0, 1.0);
  }

  String getMotivationalMessage() {
    if (state.isOnFire) {
      final messages = [
        '🔥 ${state.fireStreak} in a row! You\'re on FIRE!',
        '⚡ Unstoppable! ${state.fireStreak} streak!',
        '💪 Beast mode activated!',
      ];
      return messages[Random().nextInt(messages.length)];
    }
    
    if (state.currentStreak > 0) {
      return '📅 ${state.currentStreak}-day streak! Keep it up!';
    }
    
    return '🎯 Start your streak today!';
  }
}

class XPGainResult {
  final int xpGained;
  final int newTotalXP;
  final bool leveledUp;
  final int newLevel;
  final List<Badge> newBadges;
  final bool isOnFire;
  final int fireStreak;

  XPGainResult({
    required this.xpGained,
    required this.newTotalXP,
    required this.leveledUp,
    required this.newLevel,
    required this.newBadges,
    required this.isOnFire,
    required this.fireStreak,
  });
}

// ======================= PROVIDERS =======================

final gamificationProvider = StateNotifierProvider<GamificationNotifier, GamificationState>(
  (ref) => GamificationNotifier(),
);

final currentLevelProvider = Provider<int>((ref) {
  return ref.watch(gamificationProvider).level;
});

final dailyProgressProvider = Provider<double>((ref) {
  final state = ref.watch(gamificationProvider);
  return (state.correctToday / 10).clamp(0.0, 1.0);
});
