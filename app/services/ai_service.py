"""AI service for OpenAI integration."""

import json
import logging
import time
from typing import List, Optional

from openai import AsyncOpenAI

from app.config import settings
from app.models.schemas import (
    BreakdownRequest,
    BreakdownResponse,
    PrioritizationRequest,
    PrioritizationResponse,
    SuggestionRequest,
    SuggestionResponse,
    Subtask,
)
from app.models.todo import Priority, Todo

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Exception raised when AI service fails."""

    pass


class AIService:
    """Service for AI-powered todo assistance."""

    def __init__(self) -> None:
        """Initialize AI service with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.cache: dict = {}
        logger.info("AI service initialized with model: %s", self.model)

    async def generate_suggestions(self, request: SuggestionRequest) -> SuggestionResponse:
        """Generate todo suggestions from natural language description.

        Args:
            request: Suggestion request with description

        Returns:
            Suggestion response with AI-generated suggestions

        Raises:
            AIServiceError: If AI generation fails
        """
        logger.info("Generating suggestions for: %s", request.description[:100])

        # Check cache
        cache_key = f"suggest:{request.description}"
        if cache_key in self.cache:
            logger.debug("Returning cached suggestions")
            return SuggestionResponse(**self.cache[cache_key])

        # Build prompt
        prompt = self._build_suggestion_prompt(request.description)

        try:
            response = await self._call_openai(prompt)
            suggestions = self._parse_suggestion_response(response)

            # Cache response
            self.cache[cache_key] = suggestions.model_dump()

            logger.info("Generated %d suggestions", len(suggestions.suggestions))
            return suggestions

        except Exception as e:
            logger.exception("Failed to generate suggestions: %s", e)
            # Return fallback suggestions
            return self._get_fallback_suggestions()

    async def prioritize_todos(self, request: PrioritizationRequest) -> PrioritizationResponse:
        """Prioritize existing todos using AI.

        Args:
            request: Prioritization request with todos list

        Returns:
            Prioritization response with ranked todos

        Raises:
            AIServiceError: If AI prioritization fails
        """
        logger.info("Prioritizing %d todos", len(request.todos))

        # Check cache
        cache_key = f"prioritize:{hash(str(request.todos))}"
        if cache_key in self.cache:
            logger.debug("Returning cached prioritization")
            return PrioritizationResponse(**self.cache[cache_key])

        # Build prompt
        todos_json = json.dumps([t.model_dump() for t in request.todos])
        prompt = self._build_prioritization_prompt(todos_json)

        try:
            response = await self._call_openai(prompt)
            prioritized = self._parse_prioritization_response(response)

            # Cache response
            self.cache[cache_key] = prioritized.model_dump()

            logger.info("Prioritized %d todos", len(prioritized.ranked_todos))
            return prioritized

        except Exception as e:
            logger.exception("Failed to prioritize todos: %s", e)
            # Return simple prioritization based on due dates and priority
            return self._get_fallback_prioritization(request.todos)

    async def breakdown_task(self, request: BreakdownRequest) -> BreakdownResponse:
        """Break down a complex task into subtasks.

        Args:
            request: Breakdown request with task description

        Returns:
            Breakdown response with subtasks

        Raises:
            AIServiceError: If AI breakdown fails
        """
        logger.info("Breaking down task: %s", request.task[:100])

        # Check cache
        cache_key = f"breakdown:{request.task}"
        if cache_key in self.cache:
            logger.debug("Returning cached breakdown")
            return BreakdownResponse(**self.cache[cache_key])

        # Build prompt
        prompt = self._build_breakdown_prompt(request.task)

        try:
            response = await self._call_openai(prompt)
            breakdown = self._parse_breakdown_response(response)

            # Cache response
            self.cache[cache_key] = breakdown.model_dump()

            logger.info("Generated %d subtasks", len(breakdown.subtasks))
            return breakdown

        except Exception as e:
            logger.exception("Failed to breakdown task: %s", e)
            # Return simple breakdown
            return self._get_fallback_breakdown(request.task)

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API with retry logic.

        Args:
            prompt: Prompt to send to OpenAI

        Returns:
            OpenAI response text

        Raises:
            AIServiceError: If all retries fail
        """
        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                start_time = time.time()

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=500,
                )

                response_text = response.choices[0].message.content
                duration = time.time() - start_time

                logger.debug("OpenAI call completed in %.2fs", duration)
                return response_text

            except Exception as e:
                logger.warning("OpenAI call failed (attempt %d/%d): %s", attempt + 1, max_retries, e)

                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    logger.info("Retrying in %.1fs...", delay)
                    await self._sleep(delay)
                else:
                    raise AIServiceError(f"Failed to call OpenAI after {max_retries} attempts: {e}")

    def _build_suggestion_prompt(self, description: str) -> str:
        """Build prompt for task suggestions.

        Args:
            description: Task description

        Returns:
            Prompt string
        """
        return f"""Given the following task description, suggest 3-5 structured todo items.

Description: {description}

For each suggestion, provide:
- title (concise, action-oriented)
- description (brief explanation)
- priority (low/medium/high/urgent)

Respond in JSON format:
{{
  "suggestions": [
    {{"title": "...", "description": "...", "priority": "..."}}
  ]
}}"""

    def _build_prioritization_prompt(self, todos_json: str) -> str:
        """Build prompt for todo prioritization.

        Args:
            todos_json: JSON string of todos

        Returns:
            Prompt string
        """
        return f"""Analyze and prioritize these todo items based on due dates, current priorities, and content importance.

Todos: {todos_json}

Provide:
- Ranked list of todos
- Recommended priority adjustment if needed
- Brief reasoning for ranking

Respond in JSON format:
{{
  "ranked_todos": [
    {{"todo_id": 1, "title": "...", "recommended_priority": "...", "reasoning": "..."}}
  ]
}}"""

    def _build_breakdown_prompt(self, task: str) -> str:
        """Build prompt for task breakdown.

        Args:
            task: Task description

        Returns:
            Prompt string
        """
        return f"""Break down the following complex task into manageable subtasks with dependencies.

Task: {task}

Provide:
- Subtasks in logical order
- Dependencies between subtasks (indices of dependent subtasks)
- Estimated execution order

Respond in JSON format:
{{
  "subtasks": [
    {{"title": "...", "estimated_order": 1, "dependencies": []}}
  ]
}}"""

    def _parse_suggestion_response(self, response: str) -> SuggestionResponse:
        """Parse OpenAI suggestion response.

        Args:
            response: OpenAI response text

        Returns:
            SuggestionResponse

        Raises:
            AIServiceError: If parsing fails
        """
        try:
            data = json.loads(response)
            return SuggestionResponse(**data)
        except Exception as e:
            logger.exception("Failed to parse suggestion response: %s", e)
            raise AIServiceError(f"Failed to parse AI response: {e}")

    def _parse_prioritization_response(self, response: str) -> PrioritizationResponse:
        """Parse OpenAI prioritization response.

        Args:
            response: OpenAI response text

        Returns:
            PrioritizationResponse

        Raises:
            AIServiceError: If parsing fails
        """
        try:
            data = json.loads(response)
            return PrioritizationResponse(**data)
        except Exception as e:
            logger.exception("Failed to parse prioritization response: %s", e)
            raise AIServiceError(f"Failed to parse AI response: {e}")

    def _parse_breakdown_response(self, response: str) -> BreakdownResponse:
        """Parse OpenAI breakdown response.

        Args:
            response: OpenAI response text

        Returns:
            BreakdownResponse

        Raises:
            AIServiceError: If parsing fails
        """
        try:
            data = json.loads(response)
            return BreakdownResponse(**data)
        except Exception as e:
            logger.exception("Failed to parse breakdown response: %s", e)
            raise AIServiceError(f"Failed to parse AI response: {e}")

    def _get_fallback_suggestions(self) -> SuggestionResponse:
        """Get fallback suggestions when AI is unavailable.

        Returns:
            SuggestionResponse with predefined suggestions
        """
        return SuggestionResponse(
            suggestions=[
                {
                    "title": "Review your task description",
                    "description": "Break down what you need to accomplish",
                    "priority": "high",
                },
                {
                    "title": "Set clear goals",
                    "description": "Define specific, measurable objectives",
                    "priority": "medium",
                },
                {
                    "title": "Create an action plan",
                    "description": "Outline steps needed to complete the task",
                    "priority": "medium",
                },
            ]
        )

    def _get_fallback_prioritization(self, todos: List) -> PrioritizationResponse:
        """Get fallback prioritization when AI is unavailable.

        Args:
            todos: List of todos

        Returns:
            PrioritizationResponse with simple prioritization
        """
        # Simple prioritization: sort by priority and due date
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

        sorted_todos = sorted(
            todos,
            key=lambda t: (priority_order.get(t.priority, 2), t.due_date or "9999-12-31"),
        )

        return PrioritizationResponse(
            ranked_todos=[
                {
                    "todo_id": t.id,
                    "title": t.title,
                    "recommended_priority": t.priority,
                    "reasoning": f"Based on priority ({t.priority}) and due date",
                }
                for t in sorted_todos
            ]
        )

    def _get_fallback_breakdown(self, task: str) -> BreakdownResponse:
        """Get fallback breakdown when AI is unavailable.

        Args:
            task: Task description

        Returns:
            BreakdownResponse with simple breakdown
        """
        return BreakdownResponse(
            subtasks=[
                {
                    "title": "Define requirements",
                    "estimated_order": 1,
                    "dependencies": [],
                },
                {
                    "title": "Plan implementation",
                    "estimated_order": 2,
                    "dependencies": [0],
                },
                {
                    "title": "Execute the plan",
                    "estimated_order": 3,
                    "dependencies": [1],
                },
            ]
        )

    async def _sleep(self, seconds: float) -> None:
        """Async sleep helper.

        Args:
            seconds: Seconds to sleep
        """
        import asyncio

        await asyncio.sleep(seconds)
