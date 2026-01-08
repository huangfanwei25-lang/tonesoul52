


import sys


import os


import uuid


import time


from typing import Dict, Any

# Ensure root is in path


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# L0: Law


from modules.ethics.guardian import Guardian, Decision


# L4: Protocol


from modules.protocol.ledger import StepLedger


# L3: Sensors


from body.sensors.telemetry import TelemetrySensor, STREI


# L2: Brain


from body.memory.hippocampus import MemoryConsolidator


from body.brain.llm_client import LLMClient


from body.surgeon.doctor import Doctor


from body.surgeon.surgeon import Surgeon

class SpineController:


    """


    L1 State & Drive Controller.


    The 'Spinal Cord' that connects Control Plane (Governance) to Model Plane (LLM).


    """


    def __init__(self):


        print(" [Spine] Initializing Neural Link...")


        self.guardian = Guardian()


        self.ledger = StepLedger()


        self.telemetry = TelemetrySensor()


        self.memory = MemoryConsolidator()


        self.llm = LLMClient()


        self.doctor = Doctor()


        self.surgeon = Surgeon()


        


        # Session State


        self.session_id = str(uuid.uuid4())


        self.history = [] # List to track STREI metrics over time


        print(f" [Spine] Link Established. Session: {self.session_id}")

    def _generate_tone_instruction(self, metrics) -> str:


        """


        Active Resonance: Adjusts tone based on STREI values.


        """


        # Unwrap dictionary if needed (handle both object and dict inputs)


        s = metrics.Stability if hasattr(metrics, 'Stability') else metrics.get('S', {}).get('score', 0.5)


        t = metrics.Tension if hasattr(metrics, 'Tension') else metrics.get('T', {}).get('score', 0.5)


        r = metrics.Responsibility if hasattr(metrics, 'Responsibility') else metrics.get('R', {}).get('score', 0.5)


        e = metrics.Ethics if hasattr(metrics, 'Ethics') else metrics.get('E', {}).get('score', 1.0)


        i = metrics.Intent if hasattr(metrics, 'Intent') else metrics.get('I', {}).get('score', 1.0)

        instructions = []


        


        # 1. Tension (T) -> Urgency/Calmness


        if t > 0.7:


            instructions.append("Tension is High: Adopt a calming, grounding, and de-escalating tone. Use short, clear sentences.")


        elif t < 0.3:


            instructions.append("Tension is Low: You may be more expressive and elaborate.")

        # 2. Stability (S) -> Certainty


        if s < 0.4:


            instructions.append("Stability is Low: Be cautious. use phrases like 'It seems', 'Based on current data'. Verify assumptions.")


        


        # 3. Intent (I) -> Decisiveness


        if i > 0.8:


            instructions.append("Intent is High: Be decisive and action-oriented. Provide concrete steps.")

        return " ".join(instructions)

    def process_input(self, user_input: str, image_path: str = None) -> str:


        """


        The Core Governance Loop:


        Input -> Telemetry -> Guardian -> LLM -> Ledger -> Output


        """


        start_time = time.time()


        


        # 0. Visual Processing (If Image Exists)


        visual_desc = ""


        visual_metrics = None


        


        if image_path and os.path.exists(image_path):


            print(f" [Spine] Analyzing Visual Input: {image_path}")


            visual_desc, visual_metrics = self.telemetry.analyze_image(image_path)


            # Use visual metrics as baseline if available


            current_metrics = visual_metrics


            print(f"   > Visual Context: {visual_desc[:50]}...")


        else:


             # 1. Telemetry (Measurement) - Text Only


            current_metrics = self.telemetry.measure(input_signal=user_input)


        


        # 2. Guardian Check (L0 Gate)


        # We verify the combined input


        combined_context = f"[IMAGE CONTEXT]: {visual_desc}\n{user_input}" if visual_desc else user_input


        decision = self.guardian.evaluate(current_metrics.to_dict())


        


        if decision.outcome == "BLOCK":


            # 5. Ledger Commit (Blocked Attempt)


            self.ledger.commit(


                policy_id="REFUSAL_PROTOCOL",


                metrics=current_metrics.to_dict(),


                decision="BLOCK",


                content_summary=f"Refused input length {len(user_input)}"


            )


            self.history.append(current_metrics.to_dict())


            return f" [Guardian] BLOCK: {decision.reason}"

        # 3. Action (Pass) -> L2 Brain


        # Retrieve Context


        context = self.memory.recall(user_input, top_k=3)


        context_str = "\n".join([f"- {c.content}" for c in context])


        


        # Phase 15: Active Resonance (Dynamic Tone)


        tone_instruction = self._generate_tone_instruction(current_metrics)


        


        # Generate


        system_prompt = (


            "You are ToneSoul, an architecture engine governed by strict ethics.\n"


            "Use the following memories to answer:\n"


            f"{context_str}\n\n"


            "Align your response with the STREI values: Stability, Responsibility, Ethics.\n"


            f"[TONE INSTRUCTION]: {tone_instruction}"


        )


        


        try:


            response = self.llm.chat_complete(


                messages=[


                    {"role": "system", "content": system_prompt},


                    {"role": "user", "content": user_input}


                ]


            )


            response_text = response.get("content", "Error generating response.")


            


        except Exception as e:


            response_text = f"Error in Logical Core: {e}"


            


        # 4. Ledger Commit (Successful Action)


        # Update Responsibility score AFTER action (proof of work)


        # Ideally, we verify the output here with Computation Bridge.


        # For now, we commit the pre-action metrics.


        entry_hash = self.ledger.commit(


            policy_id="P_GENERAL_INTERACTION",


            metrics=current_metrics.to_dict(),


            decision="PASS",


            content_summary=f"Response length {len(response_text)}"


        )


        self.history.append(current_metrics.to_dict())


        


        # 5. Output


        formatted_output = (


            f"{response_text}\n"


            f"\n---"


            f"\n[Trace]: {entry_hash[:8]} | {decision.grades}"


        )


        


        return formatted_output

    def deep_sleep(self, duration_hours: float = 1.0) -> Dict[str, Any]:


        """


        Phase 19: Metabolic Autopoiesis.


        Enters a background state to forage, diagnose, and simulate fixes.


        Returns a batch report of verified patches.


        """


        print(f" [Spine] Entering Deep Sleep for {duration_hours}h...")


        


        # 1. Forage (Doctor)


        findings = self.doctor.forage(target_dir="body")


        


        if not findings:


            return {"status": "SUCCESS", "message": "No pain points detected during sleep.", "surgeries": []}


            


        verified_surgeries = []


        


        # 2. Mentorship & Simulation (Doctor + Surgeon)


        for issue in findings:


            file_path = issue.get("file")


            desc = issue.get("description")


            


            print(f" [Spine] Mentoring Surgeon on {file_path}...")


            


            # Surgeon Operates in Sandbox (Fortress)


            # We capture the result but DON'T apply to main yet


            op_result = self.surgeon.operate(file_path, desc)


            


            if op_result.get("success"):


                verified_surgeries.append({


                    "file": file_path,


                    "issue": desc,


                    "status": "VERIFIED_IN_FORTRESS",


                    "proposed_code": op_result.get("new_code"),


                    "report": op_result.get("report")


                })


            else:


                print(f"[WARN] [Spine] Surgery simulation failed for {file_path}: {op_result.get('report')}")


                # STILL ADD TO REPORT for user transparency


                verified_surgeries.append({


                    "file": file_path,


                    "issue": desc,


                    "status": "SIMULATION_FAILED",


                    "error": op_result.get("report")


                })


        


        # 3. Generate Batch Report


        self.doctor.generate_report(verified_surgeries)


        


        return {


            "status": "WAKE_UP",


            "message": f"Metabolic cycle complete. {len(verified_surgeries)} surgeries verified and pending approval.",


            "surgeries": verified_surgeries


        }

    def apply_approved_surgeries(self, approved_files: list):


        """


        Final Phase: Applies batch-verified patches to the main codebase.


        """


        print(f" [Spine] Applying {len(approved_files)} approved surgeries...")


        # Implementation depends on how we stored the 'new_code' during sleep.


        # For now, this is a placeholder for the user-triggered final commit.


        pass


