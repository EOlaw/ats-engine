"""FastAPI dependency functions for constructing service instances."""

import anthropic
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.services.ai.extraction_service import ExtractionService
from app.services.ai.optimization_service import OptimizationService
from app.services.ai.prompt_chain import PromptChainOrchestrator
from app.services.ai.scoring_service import ATSScoringService
from app.services.ai.tailoring_service import TailoringService
from app.services.ai.validation_service import ValidationService
from app.services.exporters.export_factory import ExportFactory
from app.services.parsers.document_factory import DocumentParserFactory
from app.services.resume_service import ResumeService
from app.services.templates.template_engine import TemplateEngine
from app.services.templates.template_registry import TemplateRegistry
from app.services.user_service import UserService


def get_anthropic_client(
    settings: Settings = Depends(get_settings),
) -> anthropic.AsyncAnthropic:
    """Construct and return an async Anthropic client.

    Args:
        settings: Application settings (injected).

    Returns:
        Configured AsyncAnthropic client.
    """
    return anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


def get_template_registry() -> TemplateRegistry:
    """Return a TemplateRegistry with all built-in templates registered.

    Returns:
        Initialized TemplateRegistry instance.
    """
    return TemplateRegistry()


def get_template_engine(
    registry: TemplateRegistry = Depends(get_template_registry),
) -> TemplateEngine:
    """Return a TemplateEngine backed by the template registry.

    Args:
        registry: Template registry (injected).

    Returns:
        Initialized TemplateEngine instance.
    """
    return TemplateEngine(registry)


def get_parser_factory() -> DocumentParserFactory:
    """Return a DocumentParserFactory with PDF and DOCX parsers registered.

    Returns:
        Initialized DocumentParserFactory instance.
    """
    return DocumentParserFactory()


def get_export_factory(
    template_engine: TemplateEngine = Depends(get_template_engine),
) -> ExportFactory:
    """Return an ExportFactory with PDF and DOCX exporters registered.

    Args:
        template_engine: Template engine for PDF rendering (injected).

    Returns:
        Initialized ExportFactory instance.
    """
    return ExportFactory(template_engine)


def get_prompt_chain(
    client: anthropic.AsyncAnthropic = Depends(get_anthropic_client),
    settings: Settings = Depends(get_settings),
) -> PromptChainOrchestrator:
    """Construct and return the full AI prompt chain orchestrator.

    Instantiates all five AI service components and wires them into
    a PromptChainOrchestrator.

    Args:
        client: Async Anthropic client (injected).
        settings: Application settings (injected).

    Returns:
        Fully configured PromptChainOrchestrator.
    """
    model = settings.CLAUDE_MODEL
    extraction = ExtractionService(client, model, settings)
    validation = ValidationService(client, model, settings)
    scoring = ATSScoringService(client, model, settings)
    optimization = OptimizationService(client, model, settings)
    tailoring = TailoringService(client, model, settings)

    return PromptChainOrchestrator(
        extraction=extraction,
        validation=validation,
        scoring=scoring,
        optimization=optimization,
        tailoring=tailoring,
    )


def get_resume_service(
    db: AsyncSession = Depends(get_db),
    parser_factory: DocumentParserFactory = Depends(get_parser_factory),
    prompt_chain: PromptChainOrchestrator = Depends(get_prompt_chain),
    export_factory: ExportFactory = Depends(get_export_factory),
    template_engine: TemplateEngine = Depends(get_template_engine),
    settings: Settings = Depends(get_settings),
) -> ResumeService:
    """Construct and return the top-level ResumeService.

    Args:
        db: Async database session (injected).
        parser_factory: Document parser factory (injected).
        prompt_chain: AI pipeline orchestrator (injected).
        export_factory: Document export factory (injected).
        template_engine: Template rendering engine (injected).
        settings: Application settings (injected).

    Returns:
        Fully configured ResumeService instance.
    """
    return ResumeService(
        db=db,
        parser_factory=parser_factory,
        prompt_chain=prompt_chain,
        export_factory=export_factory,
        template_engine=template_engine,
        settings=settings,
    )


def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> UserService:
    """Construct and return a UserService.

    Args:
        db: Async database session (injected).

    Returns:
        Initialized UserService instance.
    """
    return UserService(db)
