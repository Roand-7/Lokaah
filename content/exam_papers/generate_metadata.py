import os
import re
import csv


def parse_filename(filename):
    """Extract metadata from actual filename formats"""

    name = filename.replace('.pdf', '').replace('.PDF', '')

    # Pattern 1: 30-1-1_2022_Maths Standard or 30_1_1_2023_Maths Standard
    # Also matches 30_4_1_2023Maths Standard (no space before Maths)
    pattern1 = r'(\d+)[-_](\d+)[-_](\d+)[-_](\d{4})[_\s]*Maths?\s*(Standard|Basic)'
    match = re.search(pattern1, name, re.IGNORECASE)
    if match:
        code, series, set_num, year, level = match.groups()
        return {
            'filename': filename,
            'year': int(year),
            'level': level.title(),
            'code': code,
            'series': series,
            'set': set_num,
            'region': 'All India',
            'paper_type': 'Board'
        }

    # Pattern 2: 30-1-1_2024_(Mathematics Standard) or 30-1-1_2025_Mathematics Standard
    pattern2 = r'(\d+)[-_](\d+)[-_](\d+)[-_](\d{4})[_\s]*.*?(Standard|Basic)'
    match = re.search(pattern2, name, re.IGNORECASE)
    if match:
        code, series, set_num, year, level = match.groups()
        return {
            'filename': filename,
            'year': int(year),
            'level': level.title(),
            'code': code,
            'series': series,
            'set': set_num,
            'region': 'All India',
            'paper_type': 'Board'
        }

    # Pattern 3: 430-1-1_2024_MATHEMATICS (BASIC) or 430-1-1_2025_Mathematics Basic
    pattern3 = r'(\d+)[-_](\d+)[-_](\d+)[-_](\d{4})[_\s]*.*?(Standard|Basic)'
    match = re.search(pattern3, name, re.IGNORECASE)
    if match:
        code, series, set_num, year, level = match.groups()
        return {
            'filename': filename,
            'year': int(year),
            'level': level.title(),
            'code': code,
            'series': series,
            'set': set_num,
            'region': 'All India',
            'paper_type': 'Board'
        }

    # Pattern 4: 30-1 SET-1_2018_(Mathematics)
    pattern4 = r'(\d+)[-_](\d+)\s*SET[-_ ]?(\d+)[-_](\d{4})'
    match = re.search(pattern4, name, re.IGNORECASE)
    if match:
        code, series, set_num, year = match.groups()
        return {
            'filename': filename,
            'year': int(year),
            'level': 'Standard',
            'code': code,
            'series': series,
            'set': set_num,
            'region': 'All India',
            'paper_type': 'Board'
        }

    # Pattern 5: Sample papers with year in name
    # Maths_SQP 2017-18 or SQP-Mathametics-Class-X 2016-17 or SQP Maths set -II class X 2015-16
    if re.search(r'SQP', name, re.IGNORECASE):
        pattern5 = r'(\d{4})-(\d{2})'
        match = re.search(pattern5, name)
        if match:
            year_prefix = match.group(1)
            year_suffix = match.group(2)
            # Convert 2017-18 to 2017
            year = int(year_prefix)
            return {
                'filename': filename,
                'year': year,
                'level': 'Sample',
                'code': '30',
                'series': 'NA',
                'set': 'NA',
                'region': 'All India',
                'paper_type': 'Sample'
            }

    # If nothing matches
    return {
        'filename': filename,
        'year': 'PARSE_ERROR',
        'level': 'PARSE_ERROR',
        'code': 'PARSE_ERROR',
        'series': 'PARSE_ERROR',
        'set': 'PARSE_ERROR',
        'region': 'PARSE_ERROR',
        'paper_type': 'PARSE_ERROR'
    }


def main():
    raw_folder = 'raw'
    metadata_folder = 'metadata'

    pdf_files = [f for f in os.listdir(raw_folder) if f.lower().endswith('.pdf')]

    print(f"Found {len(pdf_files)} PDF files\n")

    records = []
    error_count = 0

    for pdf in pdf_files:
        record = parse_filename(pdf)
        records.append(record)

        if record['year'] == 'PARSE_ERROR':
            error_count += 1
            print(f"❌ FAILED: {pdf}")
        else:
            print(
                f"✅ {pdf} -> {record['year']}, {record['level']}, "
                f"Code:{record['code']}, Series:{record['series']}, Set:{record['set']}"
            )

    # Write CSV
    csv_path = os.path.join(metadata_folder, 'papers_index.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['filename', 'year', 'level', 'code', 'series', 'set', 'region', 'paper_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"\n{'='*60}")
    print(f"✅ CSV created: {csv_path}")
    print(f"Total records: {len(records)}")
    print(f"Parse errors: {error_count}")

    # Summary
    years = {}
    levels = {}
    for r in records:
        y = r['year']
        l = r['level']
        years[y] = years.get(y, 0) + 1
        levels[l] = levels.get(l, 0) + 1

    print(f"\n📊 Summary:")
    print("By Year:", dict(sorted(years.items())))
    print("By Level:", levels)


if __name__ == '__main__':
    main()
