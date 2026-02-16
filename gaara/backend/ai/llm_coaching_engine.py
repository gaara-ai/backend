from typing import List, Optional
import openai


class LLMCoachingEngine:
    """LLM-based natural language coaching generation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
        
        self.issue_mappings = {
            'knees_bent': 'straighten your knees gently',
            'elbows_bent': 'extend your elbows fully',
            'hips_low': 'lift your hips higher',
            'spine_misaligned': 'lengthen through your spine',
            'heels_lifted': 'press your heels toward the floor',
            'chest_collapsed': 'open your chest softly',
            'shoulders_elevated': 'relax your shoulders down',
            'back_knee_bent': 'extend your back leg fully',
            'front_knee_too_bent': 'avoid pushing your knee too far',
            'pelvis_lifted': 'keep your pelvis grounded'
        }
    
    def generate_coaching(
        self,
        pose_name: str,
        issues: List[str],
        tone: str = "calm"
    ) -> str:
        """Generate natural coaching sentence using LLM."""
        
        if not issues:
            return "Excellent alignment. Maintain steady breathing."
        
        # Map issues to readable corrections
        corrections = [
            self.issue_mappings.get(issue, issue)
            for issue in issues[:3]  # Limit to top 3 issues
        ]
        
        prompt = self._build_prompt(pose_name, corrections, tone)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional yoga teacher. Convert corrections into ONE short, calm coaching sentence under 20 words."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            sentence = response.choices[0].message.content.strip()
            return sentence
            
        except Exception as e:
            # Fallback to rule-based
            return self._fallback_generation(corrections)
    
    def _build_prompt(self, pose_name: str, corrections: List[str], tone: str) -> str:
        """Build LLM prompt."""
        corrections_text = "\n".join([f"- {c}" for c in corrections])
        
        return f"""Pose: {pose_name}
Issues detected:
{corrections_text}
Tone: {tone}, encouraging

Generate ONE coaching sentence combining these corrections. Keep it under 20 words."""
    
    def _fallback_generation(self, corrections: List[str]) -> str:
        """Fallback rule-based generation."""
        if len(corrections) == 1:
            return f"Try to {corrections[0]}."
        elif len(corrections) == 2:
            return f"{corrections[0].capitalize()} and {corrections[1]}."
        else:
            return f"{corrections[0].capitalize()}, {corrections[1]}, and {corrections[2]}."