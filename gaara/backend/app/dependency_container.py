from typing import Optional
import logging

from core.physics_engine import YogaPhysicsEngine
from core.rule_engine import SuryaNamaskarRuleEngine
from core.safety_engine import SafetyAdaptationEngine
from core.correction_engine import YogaCorrectionEngine
from ai.llm_coaching_engine import LLMCoachingEngine
from config.settings import Settings

logger = logging.getLogger(__name__)


class DependencyContainer:
    """Dependency injection container for backend services."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._physics_engine: Optional[YogaPhysicsEngine] = None
        self._rule_engine: Optional[SuryaNamaskarRuleEngine] = None
        self._safety_engine: Optional[SafetyAdaptationEngine] = None
        self._correction_engine: Optional[YogaCorrectionEngine] = None
        self._llm_coaching_engine: Optional[LLMCoachingEngine] = None
    
    def initialize(self):
        """Initialize all dependencies."""
        logger.info("Initializing dependencies...")
        
        self._physics_engine = YogaPhysicsEngine()
        
        self._rule_engine = SuryaNamaskarRuleEngine(
            knowledge_base_path=self.settings.knowledge_base_path
        )
        
        self._safety_engine = SafetyAdaptationEngine(
            knowledge_base_path=self.settings.safety_rules_path
        )
        
        self._correction_engine = YogaCorrectionEngine(
            knowledge_base_path=self.settings.corrections_path
        )
        
        if self.settings.llm_enabled:
            self._llm_coaching_engine = LLMCoachingEngine(
                api_key=self.settings.openai_api_key,
                model=self.settings.llm_model_name
            )
        
        logger.info("Dependencies initialized successfully")
    
    @property
    def physics_engine(self) -> YogaPhysicsEngine:
        if self._physics_engine is None:
            raise RuntimeError("Dependencies not initialized")
        return self._physics_engine
    
    @property
    def rule_engine(self) -> SuryaNamaskarRuleEngine:
        if self._rule_engine is None:
            raise RuntimeError("Dependencies not initialized")
        return self._rule_engine
    
    @property
    def safety_engine(self) -> SafetyAdaptationEngine:
        if self._safety_engine is None:
            raise RuntimeError("Dependencies not initialized")
        return self._safety_engine
    
    @property
    def correction_engine(self) -> YogaCorrectionEngine:
        if self._correction_engine is None:
            raise RuntimeError("Dependencies not initialized")
        return self._correction_engine
    
    @property
    def llm_coaching_engine(self) -> Optional[LLMCoachingEngine]:
        return self._llm_coaching_engine