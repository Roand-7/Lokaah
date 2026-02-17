import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'theme/lokaah_theme.dart';
import 'core/config/supabase_config.dart';
import 'screens/main/main_shell.dart';

/// 🚀 LOKAAH - NotebookLM-Inspired UI
/// Clean, modern, scholarly design with gamification

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: SupabaseConfig.supabaseUrl,
    anonKey: SupabaseConfig.supabaseAnonKey,
  );

  runApp(
    ProviderScope(
      child: LokaahApp(),
    ),
  );
}

class LokaahApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LOKAAH',
      debugShowCheckedModeBanner: false,
      
      // Light theme (default - NotebookLM style)
      theme: LokaahTheme.lightTheme,
      
      // Dark theme
      darkTheme: LokaahTheme.darkTheme,
      
      // System default
      themeMode: ThemeMode.system,
      
      home: const MainShell(),
    );
  }
}

/// 🎨 DESIGN SHOWCASE SCREEN
/// Demonstrates all UI components

class DesignShowcase extends StatelessWidget {
  const DesignShowcase({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Design System'),
        actions: [
          IconButton(
            icon: const Icon(Icons.brightness_6),
            onPressed: () {
              // Toggle theme
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSection('Typography'),
            _buildTypographyShowcase(context),
            
            const SizedBox(height: 32),
            
            _buildSection('Cards'),
            _buildCardShowcase(context),
            
            const SizedBox(height: 32),
            
            _buildSection('Buttons'),
            _buildButtonShowcase(context),
            
            const SizedBox(height: 32),
            
            _buildSection('Colors'),
            _buildColorShowcase(),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: LokaahTheme.primary,
          letterSpacing: 1,
        ),
      ),
    );
  }

  Widget _buildTypographyShowcase(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    
    return Container(
      padding: const EdgeInsets.all(20),
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
          Text('Display Large', style: textTheme.displayLarge),
          Text('Display Medium', style: textTheme.displayMedium),
          Text('Display Small', style: textTheme.displaySmall),
          const Divider(),
          Text('Headline Large', style: textTheme.headlineLarge),
          Text('Headline Medium', style: textTheme.headlineMedium),
          Text('Headline Small', style: textTheme.headlineSmall),
          const Divider(),
          Text('Title Large', style: textTheme.titleLarge),
          Text('Title Medium', style: textTheme.titleMedium),
          Text('Title Small', style: textTheme.titleSmall),
          const Divider(),
          Text('Body Large', style: textTheme.bodyLarge),
          Text('Body Medium', style: textTheme.bodyMedium),
          Text('Body Small', style: textTheme.bodySmall),
        ],
      ),
    );
  }

  Widget _buildCardShowcase(BuildContext context) {
    return Column(
      children: [
        // Standard card
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            boxShadow: LokaahTheme.softShadow,
          ),
          child: const Text('Standard Card with Soft Shadow'),
        ),
        
        const SizedBox(height: 16),
        
        // Elevated card
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            boxShadow: LokaahTheme.mediumShadow,
          ),
          child: const Text('Elevated Card with Medium Shadow'),
        ),
        
        const SizedBox(height: 16),
        
        // Bordered card
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: Theme.of(context).colorScheme.outline,
            ),
          ),
          child: const Text('Bordered Card'),
        ),
      ],
    );
  }

  Widget _buildButtonShowcase(BuildContext context) {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        ElevatedButton(
          onPressed: () {},
          child: const Text('Primary'),
        ),
        ElevatedButton.icon(
          onPressed: () {},
          icon: const Icon(Icons.add),
          label: const Text('With Icon'),
        ),
        TextButton(
          onPressed: () {},
          child: const Text('Text Button'),
        ),
        OutlinedButton(
          onPressed: () {},
          child: const Text('Outlined'),
        ),
      ],
    );
  }

  Widget _buildColorShowcase() {
    final colors = [
      ('Primary', LokaahTheme.primary),
      ('Success', LokaahTheme.success),
      ('Warning', LokaahTheme.warning),
      ('Error', LokaahTheme.error),
      ('Info', LokaahTheme.info),
      ('XP Gold', LokaahTheme.xpGold),
      ('Fire', LokaahTheme.fireOrange),
    ];

    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: colors.map((color) {
        return Container(
          width: 100,
          height: 80,
          decoration: BoxDecoration(
            color: color.$2,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Center(
            child: Text(
              color.$1,
              style: TextStyle(
                color: color.$2.computeLuminance() > 0.5 
                    ? Colors.black 
                    : Colors.white,
                fontWeight: FontWeight.w600,
                fontSize: 12,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
