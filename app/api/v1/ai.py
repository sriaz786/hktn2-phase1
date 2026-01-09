"""AI API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    BreakdownRequest,
    BreakdownResponse,
    PrioritizationRequest,
    PrioritizationResponse,
    SuggestionRequest,
    SuggestionResponse,
)
from app.services.ai_service import AIService, AIServiceError

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global AI service instance
_ai_service: AIService = None


def get_ai_service() -> AIService:
    """Get AIService instance.

    Returns:
        AIService instance
    """
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


@router.post(
    "/suggest",
    response_model=SuggestionResponse,
    summary="AI Suggestions",
    description="Generate todo suggestions from natural language description",
)
async def generate_suggestions(
    request: SuggestionRequest,
    ai_service: AIService = Depends(get_ai_service),
) -> SuggestionResponse:
    """Generate AI-powered todo suggestions.

    Args:
        request: Suggestion request with task description
        ai_service: AI service instance

    Returns:
        Suggestion response with AI-generated suggestions

    Raises:
        HTTPException: If AI generation fails
    """
    logger.info("Generating suggestions for: %s", request.description[:100])

    try:
        response = await ai_service.generate_suggestions(request)
        return response
    except AIServiceError as e:
        logger.error("AI service error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable",
        ) from e
    except Exception as e:
        logger.exception("Failed to generate suggestions: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate suggestions",
        ) from e


@router.post(
    "/prioritize",
    response_model=PrioritizationResponse,
    summary="AI Prioritization",
    description="Get AI recommendations for prioritizing existing todos",
)
async def prioritize_todos(
    request: PrioritizationRequest,
    ai_service: AIService = Depends(get_ai_service),
) -> PrioritizationResponse:
    """Get AI-powered prioritization recommendations.

    Args:
        request: Prioritization request with todos list
        ai_service: AI service instance

    Returns:
        Prioritization response with ranked todos

    Raises:
        HTTPException: If AI prioritization fails
    """
    logger.info("Prioritizing %d todos", len(request.todos))

    try:
        response = await ai_service.prioritize_todos(request)
        return response
    except AIServiceError as e:
        logger.error("AI service error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable",
        ) from e
    except Exception as e:
        logger.exception("Failed to prioritize todos: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to prioritize todos",
        ) from e


@router.post(
    "/breakdown",
    response_model=BreakdownResponse,
    summary="AI Task Breakdown",
    description="Break down a complex task into subtasks",
)
async def breakdown_task(
    request: BreakdownRequest,
    ai_service: AIService = Depends(get_ai_service),
) -> BreakdownResponse:
    """Break down a complex task into subtasks using AI.

    Args:
        request: Breakdown request with task description
        ai_service: AI service instance

    Returns:
        Breakdown response with subtasks

    Raises:
        HTTPException: If AI breakdown fails
    """
    logger.info("Breaking down task: %s", request.task[:100])

    try:
        response = await ai_service.breakdown_task(request)
        return response
    except AIServiceError as e:
        logger.error("AI service error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable",
        ) from e
    except Exception as e:
        logger.exception("Failed to breakdown task: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to breakdown task",
        ) from e
