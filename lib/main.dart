import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'core/config/supabase_config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Supabase
  await Supabase.initialize(
    url: SupabaseConfig.supabaseUrl,
    anonKey: SupabaseConfig.supabaseAnonKey,
  );

  runApp(const ProviderScope(child: LokaahApp()));
}

class LokaahApp extends StatelessWidget {
  const LokaahApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LOKAAH',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      home: const TestScreen(),
    );
  }
}

class TestScreen extends StatefulWidget {
  const TestScreen({super.key});

  @override
  State<TestScreen> createState() => _TestScreenState();
}

class _TestScreenState extends State<TestScreen> {
  String statusMessage = 'Press button to test connection';
  bool isLoading = false;

  Future<void> testConnection() async {
    setState(() {
      isLoading = true;
      statusMessage = 'Testing Supabase connection...';
    });

    try {
      final supabase = Supabase.instance.client;

      // Test database query
      final response = await supabase
          .from('users')
          .select('count')
          .count(CountOption.exact);

      setState(() {
        isLoading = false;
        statusMessage = '✅ Connected! Users in DB: ${response.count}';
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        statusMessage = '❌ Error: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('LOKAAH - Day 1 Test'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                '🚀 LOKAAH',
                style: TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'Flutter App is Running!',
                style: TextStyle(fontSize: 20),
              ),
              const SizedBox(height: 40),
              if (isLoading)
                const CircularProgressIndicator()
              else
                ElevatedButton(
                  onPressed: testConnection,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 32,
                      vertical: 16,
                    ),
                  ),
                  child: const Text(
                    'Test Supabase Connection',
                    style: TextStyle(fontSize: 16),
                  ),
                ),
              const SizedBox(height: 20),
              Text(
                statusMessage,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: statusMessage.contains('✅')
                      ? Colors.green
                      : statusMessage.contains('❌')
                          ? Colors.red
                          : Colors.grey,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
