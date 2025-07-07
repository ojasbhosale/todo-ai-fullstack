
"""
AI service for task processing using Groq API.

This module provides AI-powered features for task management including:
- Task prioritization based on context
- Deadline suggestions
- Enhanced task descriptions
- Category recommendations
- Tag suggestions
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from groq import AsyncGroq

from app.core.config import settings

logger = logging.getLogger(__name__)


class AITaskProcessor:
    """
    AI-powered task processing using Groq's fast inference API.
    
    This class handles all AI operations for task management including
    priority scoring, deadline suggestions, and content enhancement.
    """
    
    def __init__(self):
        """Initialize the AI processor with Groq configuration."""
        try:
            # Initialize Groq client with API key
            self.client = AsyncGroq(
                api_key=settings.GROQ_API_KEY 
            )
            # Using Llama 3.1 70B for better reasoning and task analysis
            self.model = "llama-3.1-70b-versatile"
            # Fallback to smaller model if needed
            self.fallback_model = "llama-3.1-8b-instant"
            logger.info("Groq AI processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            self.client = None
        
    async def generate_task_suggestions(
        self,
        title: str,
        description: str = "",
        category: str = "",
        context_data: List[Dict] = None,
        user_preferences: Dict = None,
        current_workload: int = 0
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI suggestions for a task using Groq.
        
        Args:
            title: Task title
            description: Task description
            category: Task category
            context_data: List of context entries
            user_preferences: User preferences dict
            current_workload: Current number of pending tasks
            
        Returns:
            Dictionary containing AI suggestions
        """
        # Return fallback immediately if client is not initialized
        if not self.client:
            logger.warning("Groq client not available, using fallback suggestions")
            return self._get_fallback_suggestions(title, description, category)
        
        try:
            # Prepare context for AI analysis
            context_summary = self._prepare_context_summary(context_data or [])
            
            # Create the prompt for AI analysis
            prompt = self._create_task_analysis_prompt(
                title=title,
                description=description,
                category=category,
                context_summary=context_summary,
                user_preferences=user_preferences or {},
                current_workload=current_workload
            )
            
            # Try primary model first
            suggestions = await self._try_groq_completion(prompt, self.model)
            if suggestions:
                logger.info(f"AI suggestions generated successfully for task: {title}")
                return suggestions
            
            # Try fallback model
            logger.info("Trying fallback model...")
            suggestions = await self._try_groq_completion(prompt, self.fallback_model)
            if suggestions:
                logger.info(f"AI suggestions generated with fallback model for task: {title}")
                return suggestions
            
            # If both models fail, use fallback
            logger.warning("Both Groq models failed, using fallback suggestions")
            return self._get_fallback_suggestions(title, description, category)
            
        except Exception as e:
            logger.error(f"Error generating AI suggestions: {str(e)}")
            # Return fallback suggestions
            return self._get_fallback_suggestions(title, description, category)
    
    async def _try_groq_completion(self, prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """
        Try to get completion from Groq API with specified model.
        
        Args:
            prompt: The prompt to send to the model
            model: The model to use
            
        Returns:
            Parsed suggestions dict or None if failed
        """
        try:
            # Get AI response from Groq
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant specialized in task management and productivity. You help users prioritize tasks, suggest deadlines, and enhance task descriptions based on context analysis. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent JSON output
                max_tokens=1500,
                top_p=0.9,
                stream=False
            )
            
            # Parse the AI response
            ai_content = response.choices[0].message.content
            suggestions = self._parse_ai_response(ai_content)
            
            if suggestions and 'priority_score' in suggestions:
                return suggestions
            else:
                logger.warning(f"Invalid suggestions from {model}")
                return None
                
        except Exception as e:
            logger.error(f"Error with {model}: {str(e)}")
            return None
    
    def _prepare_context_summary(self, context_data: List[Dict]) -> str:
        """
        Prepare a summary of context data for AI analysis.
        
        Args:
            context_data: List of context entries
            
        Returns:
            Formatted context summary string
        """
        if not context_data:
            return "No additional context available."
        
        context_summary = "Recent context information:\n"
        for i, context in enumerate(context_data[:5]):  # Limit to 5 most recent
            source = context.get('source_type', 'unknown')
            content = context.get('content', '')[:200]  # Truncate long content
            context_summary += f"{i+1}. [{source}] {content}\n"
        
        return context_summary
    
    def _create_task_analysis_prompt(
        self,
        title: str,
        description: str,
        category: str,
        context_summary: str,
        user_preferences: Dict,
        current_workload: int
    ) -> str:
        """
        Create a comprehensive prompt for AI task analysis optimized for Groq models.
        """
        prompt = f"""
Analyze this task and provide intelligent suggestions. You must respond with valid JSON only.

TASK DETAILS:
- Title: {title}
- Description: {description}
- Category: {category or 'Not specified'}
- Current workload: {current_workload} pending tasks

CONTEXT:
{context_summary}

USER PREFERENCES:
{json.dumps(user_preferences, indent=2) if user_preferences else 'None specified'}

Respond with this exact JSON structure:

{{
    "priority_score": <integer between 1-10>,
    "suggested_deadline": "<ISO datetime string or null>",
    "enhanced_description": "<enhanced description with context>",
    "suggested_category": "<category suggestion>",
    "ai_suggested_tags": ["<tag1>", "<tag2>", "<tag3>"],
    "reasoning": "<explanation of priority and deadline reasoning>",
    "estimated_duration": "<estimated time to complete>",
    "context_insights": ["<insight1>", "<insight2>", "<insight3>"]
}}

PRIORITY SCORING GUIDELINES:
- 1-3: Low priority, can be done anytime
- 4-6: Medium priority, should be done within a week
- 7-8: High priority, should be done within 2-3 days
- 9-10: Critical/Urgent, needs immediate attention

For suggested_deadline, use ISO format like "2024-01-15T10:00:00" or null if no specific deadline is needed.

Respond with valid JSON only, no other text.
"""
        return prompt
    
    def _parse_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """
        Parse AI response and extract structured suggestions.
        """
        try:
            # Clean the response - remove any markdown formatting
            cleaned_content = ai_content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            # Try to extract JSON from the response
            start_idx = cleaned_content.find('{')
            end_idx = cleaned_content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = cleaned_content[start_idx:end_idx]
                suggestions = json.loads(json_str)
                
                # Validate and process the suggestions
                return self._validate_suggestions(suggestions)
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse AI response: {str(e)}")
            logger.debug(f"AI response content: {ai_content[:500]}...")
            # Return None to trigger fallback
            return None
    
    def _validate_suggestions(self, suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize AI suggestions.
        """
        validated = {}
        
        # Priority score validation
        priority = suggestions.get('priority_score', 5)
        try:
            validated['priority_score'] = max(1, min(10, int(priority)))
        except (ValueError, TypeError):
            validated['priority_score'] = 5
        
        # Deadline validation
        deadline_str = suggestions.get('suggested_deadline')
        if deadline_str and deadline_str.lower() not in ['null', 'none', '']:
            try:
                # Handle different datetime formats
                if 'T' in deadline_str:
                    deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                else:
                    deadline = datetime.fromisoformat(f"{deadline_str}T12:00:00")
                
                if deadline > datetime.now():
                    validated['suggested_deadline'] = deadline
                else:
                    validated['suggested_deadline'] = None
            except ValueError:
                validated['suggested_deadline'] = None
        else:
            validated['suggested_deadline'] = None
        
        # Text fields with fallbacks
        validated['enhanced_description'] = suggestions.get('enhanced_description', '')[:1000]  # Limit length
        validated['suggested_category'] = suggestions.get('suggested_category', '')[:100]
        validated['reasoning'] = suggestions.get('reasoning', '')[:500]
        validated['estimated_duration'] = suggestions.get('estimated_duration', '')[:100]
        
        # Lists with validation
        tags = suggestions.get('ai_suggested_tags', [])
        if isinstance(tags, list):
            validated['ai_suggested_tags'] = [str(tag)[:50] for tag in tags[:5]]  # Max 5 tags
        else:
            validated['ai_suggested_tags'] = []
        
        insights = suggestions.get('context_insights', [])
        if isinstance(insights, list):
            validated['context_insights'] = [str(insight)[:200] for insight in insights[:5]]  # Max 5 insights
        else:
            validated['context_insights'] = []
        
        return validated
    
    def _get_fallback_suggestions(
        self,
        title: str,
        description: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Provide fallback suggestions when AI processing fails.
        Enhanced with better keyword detection and logic.
        """
        # Basic fallback logic
        priority_score = 5  # Default medium priority
        
        # Enhanced keyword-based priority scoring
        urgent_keywords = ['urgent', 'asap', 'emergency', 'critical', 'deadline', 'immediately', 'now']
        high_keywords = ['important', 'priority', 'soon', 'meeting', 'presentation', 'interview']
        work_keywords = ['work', 'office', 'client', 'boss', 'manager', 'project']
        personal_keywords = ['personal', 'family', 'health', 'doctor', 'appointment']
        
        title_lower = title.lower()
        description_lower = description.lower()
        text_content = f"{title_lower} {description_lower}"
        
        # Priority scoring based on keywords
        if any(keyword in text_content for keyword in urgent_keywords):
            priority_score = 9
        elif any(keyword in text_content for keyword in high_keywords):
            priority_score = 7
        elif any(keyword in text_content for keyword in work_keywords):
            priority_score = 6
        elif any(keyword in text_content for keyword in personal_keywords):
            priority_score = 5
        
        # Suggest deadline based on priority
        if priority_score >= 9:
            suggested_deadline = datetime.now() + timedelta(hours=6)
        elif priority_score >= 7:
            suggested_deadline = datetime.now() + timedelta(days=1)
        elif priority_score >= 6:
            suggested_deadline = datetime.now() + timedelta(days=3)
        else:
            suggested_deadline = datetime.now() + timedelta(days=7)
        
        # Generate tags based on content
        tags = ['general']
        if any(keyword in text_content for keyword in work_keywords):
            tags.append('work')
        if any(keyword in text_content for keyword in personal_keywords):
            tags.append('personal')
        if any(keyword in text_content for keyword in urgent_keywords):
            tags.append('urgent')
        
        return {
            'priority_score': priority_score,
            'suggested_deadline': suggested_deadline,
            'enhanced_description': description or f"Complete the task: {title}",
            'suggested_category': category or 'General',
            'ai_suggested_tags': tags[:3],  # Limit to 3 tags
            'reasoning': 'Fallback suggestion using keyword analysis (Groq API unavailable)',
            'estimated_duration': self._estimate_duration_fallback(title, description),
            'context_insights': self._generate_fallback_insights(title, description)
        }
    
    def _estimate_duration_fallback(self, title: str, description: str) -> str:
        """Generate duration estimate based on task complexity."""
        text_content = f"{title} {description}".lower()
        
        if any(word in text_content for word in ['quick', 'brief', 'short', 'simple']):
            return '15-30 minutes'
        elif any(word in text_content for word in ['meeting', 'call', 'review']):
            return '30-60 minutes'
        elif any(word in text_content for word in ['project', 'research', 'analysis', 'write', 'create']):
            return '2-4 hours'
        elif any(word in text_content for word in ['complex', 'detailed', 'comprehensive']):
            return '4-8 hours'
        else:
            return '1-2 hours'
    
    def _generate_fallback_insights(self, title: str, description: str) -> List[str]:
        """Generate basic insights based on task content."""
        insights = []
        text_content = f"{title} {description}".lower()
        
        if len(text_content.split()) > 20:
            insights.append('Consider breaking this into smaller subtasks')
        
        if any(word in text_content for word in ['meeting', 'call', 'discussion']):
            insights.append('Prepare agenda or talking points in advance')
        
        if any(word in text_content for word in ['deadline', 'urgent', 'asap']):
            insights.append('Time-sensitive task - prioritize accordingly')
        
        if not insights:
            insights.append('Set clear success criteria for this task')
        
        return insights[:3]  # Limit to 3 insights


class ContextAnalyzer:
    """
    Service for analyzing context entries.
    Enhanced with better analysis capabilities.
    """
    
    @staticmethod
    def extract_keywords(content: str) -> List[str]:
        """Extract keywords from content with improved filtering."""
        common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'a', 'an', 'this', 'that', 'these', 'those', 'it', 'they', 'we', 'you', 'i',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'our', 'their'
        }
        
        # Clean and split content
        import re
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        keywords = [
            word for word in words
            if word not in common_words and len(word) > 2
        ]
        
        # Return top 10 most frequent keywords
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]
    
    @staticmethod
    def calculate_relevance_score(content: str) -> float:
        """Calculate relevance score for task management with enhanced scoring."""
        task_keywords = [
            'task', 'todo', 'deadline', 'urgent', 'important', 'meeting',
            'project', 'work', 'complete', 'finish', 'priority', 'schedule',
            'appointment', 'reminder', 'follow', 'action', 'deliver'
        ]
        
        content_lower = content.lower()
        score = sum(2 if keyword in content_lower else 0 for keyword in task_keywords[:10])
        score += sum(1 if keyword in content_lower else 0 for keyword in task_keywords[10:])
        
        # Normalize score
        max_possible_score = len(task_keywords[:10]) * 2 + len(task_keywords[10:])
        return min(score / max_possible_score, 1.0)
    
    @staticmethod
    def analyze_sentiment(content: str) -> str:
        """Analyze sentiment of content with enhanced word lists."""
        positive_words = [
            'good', 'great', 'excellent', 'happy', 'pleased', 'satisfied',
            'love', 'like', 'amazing', 'wonderful', 'perfect', 'awesome',
            'fantastic', 'brilliant', 'outstanding', 'superb'
        ]
        negative_words = [
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'disappointed',
            'frustrated', 'angry', 'upset', 'problem', 'issue', 'difficult',
            'challenging', 'struggle', 'fail', 'wrong'
        ]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    @staticmethod
    def extract_insights(content: str, source_type: str) -> List[str]:
        """Extract insights from content based on source type with enhanced logic."""
        insights = []
        content_lower = content.lower()
        
        if source_type == 'email':
            if 'meeting' in content_lower or 'call' in content_lower:
                insights.append('Contains meeting or call information')
            if 'deadline' in content_lower or 'due' in content_lower:
                insights.append('Contains deadline information')
            if 'attached' in content_lower or 'attachment' in content_lower:
                insights.append('Contains file attachments')
        
        elif source_type == 'whatsapp':
            if 'urgent' in content_lower or '!!' in content:
                insights.append('Marked as urgent')
            if '?' in content:
                insights.append('Contains questions needing response')
            if 'meeting' in content_lower:
                insights.append('Discussion about meeting')
        
        elif source_type == 'notes':
            if 'todo' in content_lower or 'task' in content_lower:
                insights.append('Contains task-related notes')
            if 'remember' in content_lower:
                insights.append('Contains reminder information')
            if 'idea' in content_lower:
                insights.append('Contains ideas or suggestions')
        
        # Generic insights
        if 'follow up' in content_lower:
            insights.append('Requires follow-up action')
        if 'review' in content_lower:
            insights.append('Involves review or feedback')
        
        return insights[:5]  # Limit to 5 insights
