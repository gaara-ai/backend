import time
import numpy as np
from typing import Optional, Protocol
from abc import ABC, abstractmethod


class BaseTTSEngine(ABC):
    """Abstract base class for TTS engines."""
    
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Synthesize text to speech audio bytes."""
        pass
    
    @abstractmethod
    def play(self, text: str) -> bool:
        """Synthesize and play text immediately."""
        pass


class OpenAITTSEngine(BaseTTSEngine):
    """OpenAI TTS engine implementation."""
    
    def __init__(self, api_key: str, voice: str = "alloy", model: str = "tts-1"):
        self.api_key = api_key
        self.voice = voice
        self.model = model
    
    def synthesize(self, text: str) -> bytes:
        """Synthesize text using OpenAI TTS."""
        # Implementation would use OpenAI API
        return b""
    
    def play(self, text: str) -> bool:
        """Synthesize and play text."""
        # Implementation would use OpenAI API and audio playback
        return True


class VoiceFeedbackManager:
    """Manages voice feedback with intelligent cooldown logic."""
    
    def __init__(
        self,
        tts_engine: BaseTTSEngine,
        correction_cooldown: float = 5.0,
        praise_cooldown: float = 10.0
    ):
        """Initialize voice feedback manager."""
        self.tts_engine = tts_engine
        self.correction_cooldown = correction_cooldown
        self.praise_cooldown = praise_cooldown
        
        self.last_spoken_message: Optional[str] = None
        self.last_spoken_timestamp: float = 0.0
        
        self.praise_keywords = [
            "excellent", "perfect", "great", "good", "maintain", 
            "beautiful", "well done", "nice"
        ]
    
    def should_speak(self, sentence: str, alignment_score: Optional[float] = None) -> bool:
        """Determine if message should be spoken based on cooldown rules."""
        
        if not sentence or not sentence.strip():
            return False
        
        current_time = time.time()
        
        if not self.last_spoken_message:
            return True
        
        is_praise = self._is_praise_message(sentence)
        is_same_message = sentence == self.last_spoken_message
        time_since_last = current_time - self.last_spoken_timestamp
        
        if is_praise:
            if alignment_score and alignment_score > 90:
                return time_since_last >= self.praise_cooldown
            return time_since_last >= self.praise_cooldown
        
        if is_same_message:
            return time_since_last >= self.correction_cooldown
        
        return time_since_last >= 1.0
    
    def speak(self, sentence: str, alignment_score: Optional[float] = None, 
              pose_name: Optional[str] = None, force: bool = False) -> bool:
        """Speak the coaching sentence if cooldown allows."""
        
        if not force and not self.should_speak(sentence, alignment_score):
            return False
        
        try:
            success = self.tts_engine.play(sentence)
            
            if success:
                current_time = time.time()
                self.last_spoken_message = sentence
                self.last_spoken_timestamp = current_time
            
            return success
            
        except Exception:
            return False
    
    def reset(self):
        """Reset feedback manager state."""
        self.last_spoken_message = None
        self.last_spoken_timestamp = 0.0
    
    def _is_praise_message(self, sentence: str) -> bool:
        """Check if message is praise."""
        sentence_lower = sentence.lower()
        return any(keyword in sentence_lower for keyword in self.praise_keywords)