"""Unit tests for AI service."""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage

from app.models.schemas import (
    BreakdownRequest,
    BreakdownResponse,
    PrioritizationRequest,
    PrioritizationResponse,
    SuggestionRequest,
    SuggestionResponse,
    TodoSummary,
)
from app.models.todo import Priority
from app.services.ai_service import AIService, AIServiceError


# Test fixtures
@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    with patch("app.services.ai_service.AsyncOpenAI") as mock_client:
        client = AsyncMock()
        mock_client.return_value = client
        yield client


@pytest.fixture
def ai_service():
    """Create AI service instance."""
    with patch("app.services.ai_service.AsyncOpenAI"):
        service = AIService()
        return service


@pytest.fixture
def mock_chat_completion():
    """Create mock chat completion response."""
    response = Mock(spec=ChatCompletion)
    response.choices = [
        Mock(
            message=Mock(
                spec=ChatCompletionMessage,
                content=json.dumps(
                    {
                        "suggestions": [
                            {
                                "title": "Test Suggestion",
                                "description": "Test Description",
                                "priority": "high",
                            }
                        ]
                    }
                ),
            )
        )
    ]
    return response


# ==================== AI Service Tests ====================


class TestAIService:
    """Tests for AIService."""

    @pytest.mark.asyncio
    async def test_generate_suggestions_success(self, ai_service, mock_chat_completion):
        """Test successful suggestion generation."""
        ai_service.client.chat.completions.create = AsyncMock(return_value=mock_chat_completion)

        request = SuggestionRequest(description="I need to organize my project files")

        result = await ai_service.generate_suggestions(request)

        assert isinstance(result, SuggestionResponse)
        assert len(result.suggestions) == 1
        assert result.suggestions[0].title == "Test Suggestion"

        ai_service.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_suggestions_caching(self, ai_service, mock_chat_completion):
        """Test that suggestions are cached."""
        ai_service.client.chat.completions.create = AsyncMock(return_value=mock_chat_completion)

        request = SuggestionRequest(description="Test task")

        # First call
        await ai_service.generate_suggestions(request)
        assert ai_service.client.chat.completions.create.call_count == 1

        # Second call should use cache
        await ai_service.generate_suggestions(request)
        assert ai_service.client.chat.completions.create.call_count == 1  # Still 1

    @pytest.mark.asyncio
    async def test_generate_suggestions_fallback(self, ai_service):
        """Test fallback suggestions when AI fails."""
        ai_service.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))

        request = SuggestionRequest(description="Test task")

        result = await ai_service.generate_suggestions(request)

        assert isinstance(result, SuggestionResponse)
        assert len(result.suggestions) >= 1

    @pytest.mark.asyncio
    async def test_generate_suggestions_retry_logic(self, ai_service, mock_chat_completion):
        """Test retry logic on transient failures."""
        # Fail twice, then succeed
        ai_service.client.chat.completions.create = AsyncMock(
            side_effect=[
                Exception("Transient error"),
                Exception("Another transient error"),
                mock_chat_completion,
            ]
        )

        request = SuggestionRequest(description="Test task")

        result = await ai_service.generate_suggestions(request)

        assert isinstance(result, SuggestionResponse)
        assert ai_service.client.chat.completions.create.call_count == 3

    @pytest.mark.asyncio
    async def test_prioritize_todos_success(self, ai_service):
        """Test successful todo prioritization."""
        mock_response = Mock(spec=ChatCompletion)
        mock_response.choices = [
            Mock(
                message=Mock(
                    spec=ChatCompletionMessage,
                    content=json.dumps(
                        {
                            "ranked_todos": [
                                {
                                    "todo_id": 1,
                                    "title": "High Priority Task",
                                    "recommended_priority": "urgent",
                                    "reasoning": "Due tomorrow",
                                }
                            ]
                        }
                    ),
                )
            )
        ]

        ai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        request = PrioritizationRequest(
            todos=[TodoSummary(id=1, title="Task", due_date=None, priority=Priority.HIGH)]
        )

        result = await ai_service.prioritize_todos(request)

        assert isinstance(result, PrioritizationResponse)
        assert len(result.ranked_todos) == 1
        assert result.ranked_todos[0].todo_id == 1
        assert result.ranked_todos[0].recommended_priority == Priority.URGENT

    @pytest.mark.asyncio
    async def test_prioritize_todos_fallback(self, ai_service):
        """Test fallback prioritization when AI fails."""
        ai_service.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))

        request = PrioritizationRequest(
            todos=[
                TodoSummary(id=1, title="Task 1", due_date=None, priority=Priority.HIGH),
                TodoSummary(id=2, title="Task 2", due_date=None, priority=Priority.LOW),
            ]
        )

        result = await ai_service.prioritize_todos(request)

        assert isinstance(result, PrioritizationResponse)
        assert len(result.ranked_todos) == 2
        # Should be sorted by priority (high before low)
        assert result.ranked_todos[0].todo_id == 1

    @pytest.mark.asyncio
    async def test_breakdown_task_success(self, ai_service):
        """Test successful task breakdown."""
        mock_response = Mock(spec=ChatCompletion)
        mock_response.choices = [
            Mock(
                message=Mock(
                    spec=ChatCompletionMessage,
                    content=json.dumps(
                        {
                            "subtasks": [
                                {"title": "First step", "estimated_order": 1, "dependencies": []},
                                {
                                    "title": "Second step",
                                    "estimated_order": 2,
                                    "dependencies": [0],
                                },
                            ]
                        }
                    ),
                )
            )
        ]

        ai_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        request = BreakdownRequest(task="Build a REST API")

        result = await ai_service.breakdown_task(request)

        assert isinstance(result, BreakdownResponse)
        assert len(result.subtasks) == 2
        assert result.subtasks[0].title == "First step"
        assert result.subtasks[1].dependencies == [0]

    @pytest.mark.asyncio
    async def test_breakdown_task_fallback(self, ai_service):
        """Test fallback breakdown when AI fails."""
        ai_service.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))

        request = BreakdownRequest(task="Complex task")

        result = await ai_service.breakdown_task(request)

        assert isinstance(result, BreakdownResponse)
        assert len(result.subtasks) >= 1
        # Should have basic steps
        assert any("requirements" in subtask.title.lower() for subtask in result.subtasks)

    def test_build_suggestion_prompt(self, ai_service):
        """Test suggestion prompt building."""
        prompt = ai_service._build_suggestion_prompt("Test task")

        assert "Test task" in prompt
        assert "suggestions" in prompt.lower()
        assert "title" in prompt
        assert "priority" in prompt

    def test_build_prioritization_prompt(self, ai_service):
        """Test prioritization prompt building."""
        todos_json = json.dumps([{"id": 1, "title": "Test"}])
        prompt = ai_service._build_prioritization_prompt(todos_json)

        assert todos_json in prompt
        assert "prioritiz" in prompt.lower()
        assert "ranked" in prompt.lower()

    def test_build_breakdown_prompt(self, ai_service):
        """Test breakdown prompt building."""
        prompt = ai_service._build_breakdown_prompt("Build API")

        assert "Build API" in prompt
        assert "subtask" in prompt.lower()
        assert "dependencies" in prompt.lower()

    def test_parse_suggestion_response_valid(self, ai_service):
        """Test parsing valid suggestion response."""
        response = json.dumps(
            {
                "suggestions": [
                    {"title": "Test", "description": "Desc", "priority": "high"}
                ]
            }
        )

        result = ai_service._parse_suggestion_response(response)

        assert isinstance(result, SuggestionResponse)
        assert len(result.suggestions) == 1

    def test_parse_suggestion_response_invalid(self, ai_service):
        """Test parsing invalid suggestion response."""
        with pytest.raises(AIServiceError):
            ai_service._parse_suggestion_response("invalid json")

    def test_get_fallback_suggestions(self, ai_service):
        """Test getting fallback suggestions."""
        result = ai_service._get_fallback_suggestions()

        assert isinstance(result, SuggestionResponse)
        assert len(result.suggestions) >= 1

    def test_get_fallback_prioritization(self, ai_service):
        """Test getting fallback prioritization."""
        todos = [
            TodoSummary(id=1, title="High", due_date=None, priority=Priority.HIGH),
            TodoSummary(id=2, title="Low", due_date=None, priority=Priority.LOW),
        ]

        result = ai_service._get_fallback_prioritization(todos)

        assert isinstance(result, PrioritizationResponse)
        assert len(result.ranked_todos) == 2
        # Should sort high before low
        assert result.ranked_todos[0].todo_id == 1

    def test_get_fallback_breakdown(self, ai_service):
        """Test getting fallback breakdown."""
        result = ai_service._get_fallback_breakdown("Test task")

        assert isinstance(result, BreakdownResponse)
        assert len(result.subtasks) >= 1

    @pytest.mark.asyncio
    async def test_sleep(self, ai_service):
        """Test async sleep helper."""
        import time

        start = time.time()
        await ai_service._sleep(0.1)
        end = time.time()

        assert end - start >= 0.1
