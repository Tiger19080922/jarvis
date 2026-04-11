"""
run.py — Entry point for Agent 02: AI India Digest.

Usage:
  python run.py              → full run, sends email
  python run.py --dry-run    → builds email, saves to /tmp, does not send
  python run.py --memory     → show memory status and exit

Ratchet rule: complete 10 supervised manual runs before scheduling.
Log each run result in your run log.
"""

import sys
import argparse
from datetime import datetime

from config import validate, LANGFUSE_ENABLED
import memory as mem


def get_trace():
    """Return a Langfuse trace if configured, else a no-op stub."""
    if not LANGFUSE_ENABLED:
        return _NoOpTrace()
    try:
        from langfuse import Langfuse
        lf = Langfuse()
        return lf.trace(
            name="agent_02_digest",
            metadata={
                "run_date": datetime.now().isoformat(),
                "agent":    "agent_02_digest",
            }
        )
    except Exception as e:
        print(f"[run] Langfuse init failed: {e}. Continuing without tracing.")
        return _NoOpTrace()


class _NoOpTrace:
    """Stub that accepts any method call silently."""
    def span(self, **kwargs):  return self
    def generation(self, **kwargs): return self
    def update(self, **kwargs): return self
    def __getattr__(self, name): return lambda **kwargs: self


def main():
    parser = argparse.ArgumentParser(description="AI India Digest — Agent 02")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build email but do not send. Saves HTML to /tmp.")
    parser.add_argument("--memory",  action="store_true",
                        help="Show memory status and exit.")
    args = parser.parse_args()

    # Memory status
    if args.memory:
        status = mem.status()
        print(f"Memory file status:")
        print(f"  Total stories: {status['total_stories']}")
        print(f"  Oldest entry:  {status['oldest']}")
        print(f"  Newest entry:  {status['newest']}")
        sys.exit(0)

    # Validate environment
    try:
        validate()
    except EnvironmentError as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)

    # Get tracer
    trace = get_trace()

    # Run pipeline
    import agent
    result = agent.run(dry_run=args.dry_run, trace=trace)

    # Exit code
    if result["status"] in ("sent", "dry_run"):
        sys.exit(0)
    else:
        print(f"[run] pipeline ended with status: {result['status']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
