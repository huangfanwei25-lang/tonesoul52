# Memory and Skill Promotion Research Scan (2023-2025)

Scope: recent work on long-term memory, agent memory safety, and skill acquisition.
Sources: OpenAlex + arXiv API queries on 2025-12-26.

## Shortlist (recent + relevant)

1) MemoryBank: Enhancing Large Language Models with Long-Term Memory
- Venue: AAAI 2024
- Why: classic long-term memory store; aligns with Seed -> Episode consolidation.
- OpenAlex: https://openalex.org/W4393147158

2) HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models
- Venue: arXiv 2024
- Why: memory retrieval architecture; supports Episode retrieval design.
- OpenAlex: https://openalex.org/W4398886972

3) MemGPT: Towards LLMs as Operating Systems
- Venue: arXiv 2023
- Why: multi-tier memory management; maps to short/long memory separation.
- OpenAlex: https://openalex.org/W4387636003

4) Generative Agents: Interactive Simulacra of Human Behavior
- Venue: 2023 (preprint + published versions)
- Why: memory stream + reflection; supports episodic summaries.
- OpenAlex: https://openalex.org/W4387835442

5) Voyager: An Open-Ended Embodied Agent with Large Language Models
- Venue: arXiv 2023
- Why: skill acquisition loop; motivates Skill promotion thresholds.
- OpenAlex: https://openalex.org/W4378505261

6) Augmenting Language Models with Long-Term Memory
- Venue: arXiv 2023
- Why: long-term memory augmentation; broad baseline.
- OpenAlex: https://openalex.org/W4380559074

7) Memory Matters: The Need to Improve Long-Term Memory in LLM-Agents
- Venue: AAAI Symposium Series 2024
- Why: evaluation of long-term memory deficits; informs promotion gating.
- OpenAlex: https://openalex.org/W4391116828

8) AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases
- Venue: arXiv 2024
- Why: memory poisoning risks; motivates counterexample thresholds.
- OpenAlex: https://openalex.org/W4403781307

9) MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval
- Venue: arXiv 2025
- Why: persistent memory attacks; justify higher gate pass rates.
- arXiv: http://arxiv.org/abs/2512.16962v1

10) A-MEM: Agentic Memory for LLM Agents
- Venue: arXiv 2025
- Why: emerging agent memory patterns; informs future episode schema.
- OpenAlex: https://openalex.org/W4407759090

11) From Human Memory to AI Memory: A Survey on Memory Mechanisms in the Era of LLMs
- Venue: arXiv 2025
- Why: survey; overview of memory mechanisms and benchmarks.
- OpenAlex: https://openalex.org/W4415064627

## Implications for YSTM memory evolution

- Consolidation: MemoryBank + Generative Agents support Seed -> Episode compression.
- Retrieval: HippoRAG + MemGPT support indexed access to Episode summaries.
- Skill formation: Voyager supports explicit skill promotion when patterns repeat.
- Safety: AgentPoison + MemoryGraft suggest medium-high thresholds and counterexample checks.

## Design alignment (current policy)

- min_support=5: balances evidence volume with recency.
- min_pass_rate=0.85 + counterexample_rate<=0.15: aligned with memory poisoning risks.
- min_energy_samples=3 + max_energy_stddev=0.12: ensures stability before skill promotion.
- min_recent_runs=2 in 30d: keeps skills from going stale.

## Next research hooks (optional)

- Evaluate memory failure benchmarks to tune thresholds (AAAI Symposium memory eval).
- Add memory integrity checks (poisoned memory detection) as gate inputs.
- Separate "skill library" from "policy template" with versioned rollback.
