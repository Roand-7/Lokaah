# Pattern Factory

Automated pipeline to generate large volumes of CBSE Class 10 pattern JSONs.

## Files

- `app/oracle/pattern_factory/golden_pattern.json`: canonical schema example.
- `generate_patterns.py`: creates per-chapter pattern files and `all_patterns.json`.
- `validate_patterns.py`: runs sandboxed solver checks repeatedly for quality control.

## Generate 240 patterns

```bash
python generate_patterns.py --count-per-chapter 16
```

Output folder:

- `app/oracle/pattern_factory/generated/`

## Validate all generated patterns

```bash
python validate_patterns.py --iterations 100
```

