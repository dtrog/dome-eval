"""Stage 2 (milestone 2): score saved generations with one or more judges.

Design notes, to implement once milestone 1 runs:
- Read generations.jsonl from a finished generate run; never regenerate.
- One output file per judge, so judges can be added later without rerunning others.
- Judges return structured JSON (scores in [0, 1] per criterion), validated with pydantic.
- Granite Guardian: built-in risks and BYOC criteria; general judges: same criteria text.
"""
