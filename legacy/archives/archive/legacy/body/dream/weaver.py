import json
import time
import os
import random
from typing import List, Dict, Any
from ..brain.llm_client import llm_client
from ..memory.hippocampus import MemoryConsolidator, Engram
from ..memory.memory_distiller import MemoryDistiller
try:
    from ..skills.librarian import search as librarian_search
except ImportError:
    librarian_search = None

class DreamWeaver:
    """
    The Engine of Offline Simulation (AI Dreaming).
    Performs 'Sandboxed Deduction' on unresolved topics.
    
    Methodology: Dialectical Simulation (Thesis -> Antithesis -> Synthesis)
    Goal: Produce structured future insights/audits.
    """
    
    def __init__(self, memory_system: MemoryConsolidator):
        self.memory = memory_system
        self.insights_file = "dream_insights.json"
        self.distiller = MemoryDistiller(memory_system)

    def enter_rem_cycle(self, duration_seconds: int = 60) -> List[Dict]:
        """
        Starts the dreaming process.
        Scans significant recent memories and runs simulations on them.
        """
        print(f" [DreamWeaver] Entering REM cycle for {duration_seconds}s...")
        start_time = time.time()
        
        # 1. Foraging: Find active topics (High Importance, High Tension)
        # Filter for high importance candidates
        candidates = [e for e in self.memory.engrams if e.importance > 0.6]
        
        # If no high importance memories, fallback to recent ones
        if not candidates:
            candidates = sorted(self.memory.engrams, key=lambda x: x.timestamp, reverse=True)[:5]
        
        selected_engrams = []
        if candidates:
            # Check for recent topics to avoid loops
            recent_memories = sorted(self.memory.engrams, key=lambda x: x.timestamp, reverse=True)[:10]
            recent_topics = set()
            for m in recent_memories:
                 # Extract topic from content "Dream Insight on {topic}: ..."
                 if "Dream Insight on " in m.content:
                     try:
                         t = m.content.split("Dream Insight on ")[1].split(":")[0]
                         recent_topics.add(t.strip())
                     except:
                         pass

            # Filter candidates
            candidates = [c for c in candidates if c.content not in recent_topics and c.source_record_id not in recent_topics]
            
            # Weighted random selection based on importance
            weights = [c.importance for c in candidates]
            if candidates:
                k = min(3, len(candidates))
                selected_engrams = random.choices(candidates, weights=weights, k=k)
                # Remove duplicates by ID
                seen_ids = set()
                unique_engrams = []
                for e in selected_engrams:
                    if e.engram_id not in seen_ids:
                        unique_engrams.append(e)
                        seen_ids.add(e.engram_id)
                selected_engrams = unique_engrams
            else:
                print(" [DreamWeaver] No suitable topics found (all recent). injecting random seed.")
                selected_engrams = [] # Will trigger seed injection in next cycle if implemented, or just sleep

        
        generated_insights = []
        
        for engram in selected_engrams: 
            if time.time() - start_time > duration_seconds:
                break
                
            report = self._synthesize(engram.content)
            if report:
                self._persist_insight(report)
                
                # FEEDBACK LOOP: Remember the dream!
                # The insight itself becomes a new memory, allowing evolution.
                dream_summary = f"Dream Insight on {report['topic']}: {report['simulation']['structure'][:500]}..."
                self.memory.engrave(
                    content=dream_summary, 
                    source_id="dream_weaver", 
                    importance=0.8, # Dreams are moderately important
                    tags=["dream_insight", "evolution"]
                )
                
                generated_insights.append(report)
                
        # 4. DISTILLATION: Semantic Compression (Auto-pruning substitute)
        # If memory is growing, distill the oldest bits
        if len(self.memory.engrams) > 50: # Threshold for distillation
            print(" [Deep Sleep] Memory density high. Initiating distillation...")
            self.distiller.distill(max_cluster_size=10)
                
        print(f" [DreamWeaver] Waking up. Generated {len(generated_insights)} insights.")
        return generated_insights

    def _synthesize(self, topic: str) -> Dict[str, Any]:
        """
        Runs the Dialectical Simulation on a topic.
        """
        print(f" [Dreaming] Simulating topic: '{topic[:30]}...'")
        
        # 1. Thesis (The Plan / Optimism)
        thesis_prompt = (
            f"Topic: {topic}\n"
            "Role: Visionary Architect.\n"
            "Task: Propose a bold, perfect future or plan based on this topic. "
            "Assume everything goes right. What is the maximum potential?\n"
            "Language: Traditional Chinese (Taiwan). output must be in Traditional Chinese."
        )
        thesis = llm_client.generate(thesis_prompt)
        
        # 1.5 Research (The Librarian)
        research_context = ""
        if librarian_search:
            research_context = self._conduct_research(topic, thesis)
        
        # 2. Antithesis (The Audit / Pessimism)
        antithesis_prompt = (
            f"Topic: {topic}\n"
            f"Proposed Vision: {thesis}\n"
            f"Related Research: {research_context}\n"
            "Role: Ruthless Auditor / Red Team.\n"
            "Task: Destroy this vision. Find every risk, flaw, bug, and failure mode. "
            "Simulate the worst-case scenario.\n"
            "Language: Traditional Chinese (Taiwan). output must be in Traditional Chinese."
        )
        antithesis = llm_client.generate(antithesis_prompt)
        
        # 3. Synthesis (The Structured Future)
        synthesis_prompt = (
            f"Thesis: {thesis}\n"
            f"Antithesis: {antithesis}\n"
            "Role: Strategic Director.\n"
            "Task: Synthesize these opposing views into a robust, actionable structure. "
            "Create a 'Future Report' that mitigates the risks while capturing the value. "
            "If the topic is about Code, provide specific optimization strategies.\n"
            "Format: Structured Markdown.\n"
            "Language: Traditional Chinese (Taiwan). output must be in Traditional Chinese."
        )
        synthesis = llm_client.generate(synthesis_prompt)
        
        insight = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "topic": topic,
            "simulation": {
                "vision": thesis,
                "risks": antithesis,
                "structure": synthesis
            }
        }
        
        # Add research to valid insight structure
        if research_context:
            insight["simulation"]["research"] = research_context

        # 4. LUCIDITY: The Surgeon Bridge (Phase 20)
        # If this was a Code Audit, ask the Surgeon to intervene based on the Synthesis.
        if "Code Audit:" in topic:
            try:
                # Dynamically import to avoid circular dependencies if any
                from ..surgeon.surgeon import Surgeon
                print(" [Lucidity] Detecting Actionable Code Insight...")
                
                # Extract filename from topic "Code Audit: filename.py"
                try:
                    filename = topic.split("Code Audit: ")[1].strip()
                    # The file path in topic is absolute or relative? In foraging it's usually absolute or relative.
                    # forage_codebase uses target_file which is relative if run from root.
                    # Let's clean it.
                    if "Users" in filename: # Absolute path likely
                         # Try to make it relative to repo root
                         if "ToneSoul-Architecture-Engine-main" in filename:
                             filename = filename.split("ToneSoul-Architecture-Engine-main\\")[-1].replace("\\", "/")
                except:
                    filename = None
                
                if filename:
                    # Activate Surgeon
                    # Use 'ollama' by default to avoid key dependency errors in auto-run unless configured
                    # But for 'smart' surgery we prefer 'openai'.
                    # Let's default to 'ollama' as it's safe for a local test, but mention it might be dumb.
                    # Actually, for the user demo, let's use 'ollama' if keys aren't set.
                    surgeon = Surgeon(provider="ollama") 
                    
                    # The "Issue" is the Synthesis (The structured improvement plan)
                    report_summary = synthesis[:500] 
                    print(f" [Lucidity] Paging Surgeon for {filename}...")
                    
                    # Trigger Operation
                    operation_result = surgeon.operate(filename, f"Implement the following improvements found in Dream Audit: {report_summary}")
                    
                    # Log result to insights
                    insight["surgeon_report"] = operation_result
            except Exception as e:
                print(f" [Lucidity] Failed to bridge to Surgeon: {e}")

        return insight

    def _conduct_research(self, topic: str, thesis: str) -> str:
        """
        Consults the Librarian (arXiv) to validate or enrich the thesis.
        """
        # 1. Ask Brain if we need research
        audit_prompt = (
            f"Topic: {topic}\nThesis: {thesis[:200]}...\n"
            "Question: Does this topic rely on specific scientific or technical knowledge "
            "that requires verification? If yes, provide a specialized English search query for arXiv.\n"
            "Format: JSON { 'needs_research': bool, 'query': str }"
        )
        try:
            decision_raw = llm_client.generate(audit_prompt)
            # Simple parsing (robustness needed for production)
            if "true" in decision_raw.lower() or "yes" in decision_raw.lower():
                # Extract query (naively for now, usually LLM puts it in quotes or JSON)
                query = topic # Fallback
                if "query" in decision_raw:
                    import re
                    match = re.search(r'"query":\s*"([^"]+)"', decision_raw)
                    if match:
                        query = match.group(1)
                
                print(f" [Librarian] Researching: '{query}'...")
                papers = librarian_search(query, max_results=3)
                
                if not papers:
                    return "No relevant papers found."
                
                summary = "Related Research:\n"
                for p in papers:
                    summary += f"- {p['title']}: {p['summary'][:150]}...\n"
                return summary
                
        except Exception as e:
            print(f" [Librarian] Research failed: {e}")
            
        return ""

    def _persist_insight(self, insight: Dict):
        """Saves the insight to the subconscious file. Keeps only last 50 entries."""
        data = []
        if os.path.exists(self.insights_file):
            try:
                with open(self.insights_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []
        
        data.append(insight)
        
        # Limit to last 50 entries
        if len(data) > 50:
            data = data[-50:]
        
        with open(self.insights_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(" [DreamWeaver] Insight saved to subconscious (Pruned to last 50).")
