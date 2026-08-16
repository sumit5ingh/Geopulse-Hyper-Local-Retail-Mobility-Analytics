"""
Day 7 - GeoPulse Pipeline Runner """


import subprocess
import sys
import time

# Order important hai - har step pichle step ke output pe depend karta hai.
PIPELINE_STEPS = [
    ("Day 1-2: GPS Journey Generation", "generate_gps_data.py"),
    ("Day 3: Metadata Enrichment", "generate_gps_metadata.py"),
    ("Day 4: Footfall / Store Visit Detection", "generate_footfall_data.py"),
    ("Day 5: Catchment / Spatial Analysis", "generate_catchment_data.py"),
    ("Day 6: Data Validation", "validate_data.py"),
]


def run_step(step_name, script_name):
    """Ek script ko subprocess ke through run karta hai aur
    uska success/failure return karta hai."""

    print()
    print("=" * 60)
    print(f"RUNNING: {step_name}")
    print(f"Script:  {script_name}")
    print("=" * 60)

    start = time.time()

    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=False  # Live output console mein dikhega
    )

    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"\n[OK] {step_name} completed in {elapsed:.1f}s")
        return True
    else:
        print(f"\n[FAIL] {step_name} failed (exit code {result.returncode})")
        return False


def main():
    print("GEOPULSE - FULL PIPELINE RUN")
    print(f"Total steps: {len(PIPELINE_STEPS)}")

    overall_start = time.time()

    for step_name, script_name in PIPELINE_STEPS:
        success = run_step(step_name, script_name)

        if not success:
            print()
            print("=" * 60)
            print(f"PIPELINE STOPPED - '{step_name}' failed.")
            print("Fix the error above and re-run the pipeline.")
            print("=" * 60)
            sys.exit(1)

    total_elapsed = time.time() - overall_start

    print()
    print("=" * 60)
    print(f"PIPELINE COMPLETE - all {len(PIPELINE_STEPS)} steps passed "
          f"in {total_elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
