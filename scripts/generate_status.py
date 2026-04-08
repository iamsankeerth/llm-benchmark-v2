#!/usr/bin/env python3
"""
Generate TEST_STATUS.md from test_progress.json
Run this after running benchmarks or anytime to update the status dashboard.
"""

import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.test_tracker import TestTracker

def main():
    tracker = TestTracker()
    
    status_report = tracker.generate_status_report()
    
    base_dir = Path(__file__).parent.parent
    status_file = base_dir / "TEST_STATUS.md"
    
    with open(status_file, 'w', encoding='utf-8') as f:
        f.write(status_report)
    
    print(f"Status report saved to: {status_file}")
    print()
    print(status_report)

if __name__ == "__main__":
    main()
