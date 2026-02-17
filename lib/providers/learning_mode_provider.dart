import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 🎯 LEARNING MODE PROVIDER
/// Allows students to switch between Socratic and Direct modes
/// Addresses the "10 PM homework rush" problem

enum LearningMode {
  socratic,    // Full VEDA teaching experience
  guided,      // Some hints, but faster
  direct,      // Just give me the answer steps
}

enum TimeOfDay {
  morning,     // 5 AM - 12 PM
  afternoon,   // 12 PM - 5 PM
  evening,     // 5 PM - 10 PM
  night,       // 10 PM - 5 AM (TIRED MODE)
}

class LearningModeState {
  final LearningMode mode;
  final bool isAutoMode;  // Auto-switch based on time
  final TimeOfDay timeOfDay;
  final bool isTiredModeRecommended;

  LearningModeState({
    this.mode = LearningMode.socratic,
    this.isAutoMode = true,
    this.timeOfDay = TimeOfDay.morning,
    this.isTiredModeRecommended = false,
  });

  LearningModeState copyWith({
    LearningMode? mode,
    bool? isAutoMode,
    TimeOfDay? timeOfDay,
    bool? isTiredModeRecommended,
  }) {
    return LearningModeState(
      mode: mode ?? this.mode,
      isAutoMode: isAutoMode ?? this.isAutoMode,
      timeOfDay: timeOfDay ?? this.timeOfDay,
      isTiredModeRecommended: isTiredModeRecommended ?? this.isTiredModeRecommended,
    );
  }

  String get modeLabel {
    switch (mode) {
      case LearningMode.socratic:
        return 'Learn Deeply';
      case LearningMode.guided:
        return 'Quick Help';
      case LearningMode.direct:
        return 'Just Answer';
    }
  }

  String get modeDescription {
    switch (mode) {
      case LearningMode.socratic:
        return 'VEDA guides you step-by-step';
      case LearningMode.guided:
        return 'Hints + Solution when stuck';
      case LearningMode.direct:
        return 'Straight to the solution';
    }
  }

  IconType get modeIcon {
    switch (mode) {
      case LearningMode.socratic:
        return IconType.socratic;
      case LearningMode.guided:
        return IconType.guided;
      case LearningMode.direct:
        return IconType.direct;
    }
  }
}

enum IconType { socratic, guided, direct }

class LearningModeNotifier extends StateNotifier<LearningModeState> {
  SharedPreferences? _prefs;
  static const String _modeKey = 'learning_mode';
  static const String _autoKey = 'learning_mode_auto';

  LearningModeNotifier() : super(LearningModeState()) {
    _init();
  }

  Future<void> _init() async {
    _prefs = await SharedPreferences.getInstance();
    
    // Load saved mode
    final savedMode = _prefs?.getString(_modeKey);
    final isAuto = _prefs?.getBool(_autoKey) ?? true;
    
    LearningMode mode = LearningMode.socratic;
    if (savedMode != null) {
      mode = LearningMode.values.firstWhere(
        (e) => e.toString() == savedMode,
        orElse: () => LearningMode.socratic,
      );
    }
    
    // Check time
    final timeOfDay = _getTimeOfDay();
    final isTired = timeOfDay == TimeOfDay.night;
    
    // Auto-switch to direct mode at night if auto mode is on
    if (isAuto && isTired && mode == LearningMode.socratic) {
      mode = LearningMode.guided;
    }
    
    state = LearningModeState(
      mode: mode,
      isAutoMode: isAuto,
      timeOfDay: timeOfDay,
      isTiredModeRecommended: isTired,
    );
  }

  TimeOfDay _getTimeOfDay() {
    final hour = DateTime.now().hour;
    if (hour >= 5 && hour < 12) return TimeOfDay.morning;
    if (hour >= 12 && hour < 17) return TimeOfDay.afternoon;
    if (hour >= 17 && hour < 22) return TimeOfDay.evening;
    return TimeOfDay.night;
  }

  Future<void> setMode(LearningMode mode) async {
    state = state.copyWith(mode: mode, isAutoMode: false);
    await _prefs?.setString(_modeKey, mode.toString());
    await _prefs?.setBool(_autoKey, false);
  }

  Future<void> setAutoMode(bool isAuto) async {
    state = state.copyWith(isAutoMode: isAuto);
    await _prefs?.setBool(_autoKey, isAuto);
    
    if (isAuto) {
      // Re-evaluate based on time
      final timeOfDay = _getTimeOfDay();
      final isTired = timeOfDay == TimeOfDay.night;
      
      LearningMode newMode = LearningMode.socratic;
      if (isTired) newMode = LearningMode.guided;
      
      state = state.copyWith(
        mode: newMode,
        timeOfDay: timeOfDay,
        isTiredModeRecommended: isTired,
      );
      await _prefs?.setString(_modeKey, newMode.toString());
    }
  }

  /// Check if we should show tired mode suggestion
  bool shouldShowTiredSuggestion() {
    return state.isTiredModeRecommended && 
           state.mode == LearningMode.socratic &&
           !state.isAutoMode;
  }
}

final learningModeProvider = StateNotifierProvider<LearningModeNotifier, LearningModeState>(
  (ref) => LearningModeNotifier(),
);
