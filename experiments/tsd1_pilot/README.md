# TSD-1 Pilot (H1: Tension-Diversity Correlation)

Goal
- Validate whether TSR tension (T) correlates with output diversity across multiple responses to the same prompt.

Inputs
- data/prompts.json: list of prompts with id/category/text.
- data/responses.json: list of responses with prompt_id/response_id/text.

Run
- python experiments/tsd1_pilot/scripts/run_trials.py --prompts experiments/tsd1_pilot/data/prompts.json --responses experiments/tsd1_pilot/data/responses.json --out-dir experiments/tsd1_pilot/results

Outputs
- results/trials.jsonl: per-response TSR metrics.
- results/summary.json: per-prompt diversity + correlation stats.
