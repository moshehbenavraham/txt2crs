# SPDX-License-Identifier: MIT-0

"""Strict, versioned data contracts for every canonical txt2crs artifact.

These models form the boundary between model-generated data and trusted
application state. They reject unknown fields, impose practical size limits,
and validate internal identifiers before an artifact can be checkpointed.
"""

from datetime import date, datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SchemaVersion = Literal["1.0"]
Identifier = Annotated[
    str,
    Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"),
]
HashValue = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
NonEmptyText = Annotated[str, Field(min_length=1, max_length=200_000)]
ShortText = Annotated[str, Field(min_length=1, max_length=2_000)]


class StrictContract(BaseModel):
    """Shared configuration for externally stored contracts."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class InputLocation(StrictContract):
    """A displayable location within a source input."""

    label: ShortText
    page: Annotated[int, Field(ge=1)] | None = None
    timestamp_seconds: Annotated[float, Field(ge=0)] | None = None


class InputDocument(StrictContract):
    """Normalized text plus source boundaries produced by ingestion."""

    schema_version: SchemaVersion
    document_id: Identifier
    input_type: Literal[
        "prompt",
        "text",
        "url",
        "pdf",
        "document",
        "slides",
        "image",
        "audio",
        "video",
    ]
    media_type: Annotated[str, Field(min_length=1, max_length=255)]
    normalized_text: Annotated[str, Field(min_length=1, max_length=2_000_000)]
    language: Annotated[str, Field(min_length=2, max_length=35)]
    metadata: dict[str, Any]
    content_hash: HashValue
    warnings: list[ShortText] = Field(max_length=100)
    locations: list[InputLocation] = Field(max_length=10_000)


class ResearchQuestion(StrictContract):
    """One focused question that guides evidence collection."""

    question_id: Identifier
    question: ShortText
    preferred_source_types: list[ShortText] = Field(min_length=1, max_length=10)
    freshness_days: Annotated[int, Field(gt=0)] | None = None


class ResearchPlan(StrictContract):
    """A finite, schema-constrained plan generated before web research."""

    schema_version: SchemaVersion
    plan_id: Identifier
    questions: list[ResearchQuestion] = Field(min_length=1, max_length=50)
    maximum_sources: Annotated[int, Field(gt=0, le=100)]
    stop_criteria: list[ShortText] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def ensure_questions_are_unique(self) -> "ResearchPlan":
        """Reject duplicate identifiers and case-insensitive question text."""

        question_ids = [question.question_id for question in self.questions]
        normalized_questions = [
            " ".join(question.question.casefold().split())
            for question in self.questions
        ]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("duplicate research question_id")
        if len(normalized_questions) != len(set(normalized_questions)):
            raise ValueError("duplicate research question")
        return self


class SourceRecord(StrictContract):
    """Immutable metadata for one learner-displayable source."""

    schema_version: SchemaVersion
    source_id: Identifier
    canonical_url: Annotated[str, Field(min_length=8, max_length=2_048)]
    title: ShortText
    publisher_or_author: ShortText
    publication_date: date | None
    retrieved_at: datetime
    content_hash: HashValue
    source_type: Literal[
        "official_documentation",
        "government",
        "academic",
        "standards_body",
        "reputable_secondary",
        "community",
        "user_input",
    ]
    authority_tier: Literal["primary", "authoritative", "secondary", "community"]
    language: Annotated[str, Field(min_length=2, max_length=35)]


class EvidenceExcerpt(StrictContract):
    """A bounded evidence fragment preserved separately from trusted prompts."""

    schema_version: SchemaVersion
    evidence_id: Identifier
    source_id: Identifier
    excerpt: Annotated[str, Field(min_length=1, max_length=20_000)]
    location: InputLocation
    content_hash: HashValue
    retrieval_method: Literal[
        "user_input",
        "web_extract",
        "pdf_extract",
        "document_extract",
        "transcript",
    ]
    prompt_injection_warning: bool


class ClaimCitation(StrictContract):
    """Mechanical and semantic citation result for an artifact claim."""

    schema_version: SchemaVersion
    citation_id: Identifier
    artifact_location: Identifier
    claim_text: ShortText
    claim_hash: HashValue
    evidence_ids: list[Identifier] = Field(min_length=1, max_length=20)
    support_verdict: Literal["supported", "partial", "unsupported", "conflicting"]
    verifier_version: ShortText


class LearningObjective(StrictContract):
    """A stable learning outcome shared by every educational artifact."""

    objective_id: Identifier
    description: ShortText
    assessed: bool = True


class ContentBlock(StrictContract):
    """One renderable unit of lesson content."""

    block_id: Identifier
    kind: Literal["paragraph", "heading", "list", "code", "callout", "example"]
    text: NonEmptyText
    evidence_ids: list[Identifier] = Field(max_length=50)
    is_model_generated_example: bool


class CourseSection(StrictContract):
    """A lesson section aligned to objectives and evidence."""

    section_id: Identifier
    title: ShortText
    objective_ids: list[Identifier] = Field(min_length=1, max_length=50)
    content_blocks: list[ContentBlock] = Field(min_length=1, max_length=500)
    summary: NonEmptyText


class CourseModule(StrictContract):
    """A coherent group of course sections."""

    module_id: Identifier
    title: ShortText
    objective_ids: list[Identifier] = Field(min_length=1, max_length=50)
    sections: list[CourseSection] = Field(min_length=1, max_length=100)
    summary: NonEmptyText
    misconceptions: list[ShortText] = Field(max_length=100)
    examples: list[NonEmptyText] = Field(max_length=100)


class CoursePlanModule(StrictContract):
    """A module skeleton approved before expensive lesson writing."""

    module_id: Identifier
    title: ShortText
    objective_ids: list[Identifier] = Field(min_length=1, max_length=50)
    section_ids: list[Identifier] = Field(min_length=1, max_length=100)


class CoursePlan(StrictContract):
    """Versioned curriculum design shared with research and writing."""

    schema_version: SchemaVersion
    plan_id: Identifier
    course_id: Identifier
    title: ShortText
    language: Annotated[str, Field(min_length=2, max_length=35)]
    audience: ShortText
    level: Literal["beginner", "intermediate", "advanced", "mixed"]
    prerequisites: list[ShortText] = Field(max_length=100)
    duration_minutes: Annotated[int, Field(gt=0, le=100_000)]
    accessibility_requirements: list[ShortText] = Field(max_length=100)
    learning_objectives: list[LearningObjective] = Field(min_length=1, max_length=100)
    modules: list[CoursePlanModule] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_plan_references(self) -> "CoursePlan":
        """Require unique plan IDs and complete objective coverage."""

        objective_ids = [
            objective.objective_id for objective in self.learning_objectives
        ]
        module_ids = [module.module_id for module in self.modules]
        section_ids = [
            section_id for module in self.modules for section_id in module.section_ids
        ]
        _require_unique("course plan objective_id", objective_ids)
        _require_unique("course plan module_id", module_ids)
        _require_unique("course plan section_id", section_ids)
        known_objective_ids = set(objective_ids)
        covered_objective_ids: set[str] = set()
        for module in self.modules:
            _require_known_many(
                "course plan objective_id",
                module.objective_ids,
                known_objective_ids,
            )
            covered_objective_ids.update(module.objective_ids)
        missing_objective_ids = known_objective_ids - covered_objective_ids
        if missing_objective_ids:
            missing_objective_id = sorted(missing_objective_ids)[0]
            raise ValueError(
                f"course plan objective is not covered: {missing_objective_id}"
            )
        return self


class GlossaryTerm(StrictContract):
    """A course term with direct section references."""

    term: ShortText
    definition: NonEmptyText
    section_ids: list[Identifier] = Field(min_length=1, max_length=50)


class CourseModuleDraft(StrictContract):
    """One module-sized model result assembled into the canonical course."""

    schema_version: SchemaVersion
    course_id: Identifier
    module: CourseModule
    glossary: list[GlossaryTerm] = Field(max_length=500)
    unresolved_or_conflicting_claims: list[ShortText] = Field(max_length=100)
    citations: list[ClaimCitation] = Field(max_length=10_000)

    @model_validator(mode="after")
    def validate_module_local_references(self) -> "CourseModuleDraft":
        """Reject citations or glossary entries outside this module."""

        section_ids = {section.section_id for section in self.module.sections}
        block_ids = {
            block.block_id
            for section in self.module.sections
            for block in section.content_blocks
        }
        _require_unique(
            "module draft citation_id",
            [citation.citation_id for citation in self.citations],
        )
        for glossary_term in self.glossary:
            _require_known_many(
                "module draft glossary section_id",
                glossary_term.section_ids,
                section_ids,
            )
        for citation in self.citations:
            _require_known(
                "module draft citation artifact_location",
                citation.artifact_location,
                block_ids,
            )
        return self


class Course(StrictContract):
    """The canonical approved course used by all downstream stages."""

    schema_version: SchemaVersion
    course_id: Identifier
    title: ShortText
    language: Annotated[str, Field(min_length=2, max_length=35)]
    audience: ShortText
    level: Literal["beginner", "intermediate", "advanced", "mixed"]
    prerequisites: list[ShortText] = Field(max_length=100)
    learning_objectives: list[LearningObjective] = Field(min_length=1, max_length=100)
    sources: list[SourceRecord] = Field(max_length=100)
    modules: list[CourseModule] = Field(min_length=1, max_length=100)
    glossary: list[GlossaryTerm] = Field(max_length=500)
    unresolved_or_conflicting_claims: list[ShortText] = Field(max_length=100)
    evidence: list[EvidenceExcerpt] = Field(max_length=2_000)
    citations: list[ClaimCitation] = Field(max_length=10_000)

    @model_validator(mode="after")
    def validate_internal_references(self) -> "Course":
        """Prove IDs are unique and every course-local reference exists."""

        objective_ids = [
            objective.objective_id for objective in self.learning_objectives
        ]
        source_ids = [source.source_id for source in self.sources]
        evidence_ids = [evidence.evidence_id for evidence in self.evidence]
        module_ids = [module.module_id for module in self.modules]
        section_ids = [
            section.section_id for module in self.modules for section in module.sections
        ]
        block_ids = [
            block.block_id
            for module in self.modules
            for section in module.sections
            for block in section.content_blocks
        ]

        _require_unique("objective_id", objective_ids)
        _require_unique("source_id", source_ids)
        _require_unique("evidence_id", evidence_ids)
        _require_unique("module_id", module_ids)
        _require_unique("section_id", section_ids)
        _require_unique("block_id", block_ids)
        _require_unique(
            "citation_id",
            [citation.citation_id for citation in self.citations],
        )

        known_objectives = set(objective_ids)
        known_sources = set(source_ids)
        known_evidence = set(evidence_ids)
        known_sections = set(section_ids)
        for evidence in self.evidence:
            _require_known("source_id", evidence.source_id, known_sources)
        for module in self.modules:
            _require_known_many("objective_id", module.objective_ids, known_objectives)
            for section in module.sections:
                _require_known_many(
                    "objective_id",
                    section.objective_ids,
                    known_objectives,
                )
                for block in section.content_blocks:
                    _require_known_many(
                        "evidence_id",
                        block.evidence_ids,
                        known_evidence,
                    )
        for glossary_term in self.glossary:
            _require_known_many(
                "section_id",
                glossary_term.section_ids,
                known_sections,
            )
        known_block_ids = set(block_ids)
        for citation in self.citations:
            _require_known(
                "citation artifact_location",
                citation.artifact_location,
                known_block_ids,
            )
            _require_known_many(
                "citation evidence_id",
                citation.evidence_ids,
                known_evidence,
            )
        return self


class StudyGuideItem(StrictContract):
    """Review guidance for one learning objective."""

    objective_id: Identifier
    section_ids: list[Identifier] = Field(min_length=1, max_length=50)
    summary: NonEmptyText
    key_takeaways: list[ShortText] = Field(min_length=1, max_length=50)
    misconceptions: list[ShortText] = Field(max_length=50)
    source_ids: list[Identifier] = Field(max_length=50)


class Flashcard(StrictContract):
    """A stable prompt-and-answer review pair."""

    flashcard_id: Identifier
    objective_id: Identifier
    prompt: ShortText
    answer: NonEmptyText
    section_ids: list[Identifier] = Field(min_length=1, max_length=50)


class PracticeExercise(StrictContract):
    """A worked example or learner practice exercise."""

    exercise_id: Identifier
    objective_id: Identifier
    prompt: NonEmptyText
    solution: NonEmptyText
    section_ids: list[Identifier] = Field(min_length=1, max_length=50)


class ReviewPack(StrictContract):
    """Comprehensive review material derived from one approved course."""

    schema_version: SchemaVersion
    review_pack_id: Identifier
    course_id: Identifier
    study_guide: list[StudyGuideItem] = Field(min_length=1, max_length=100)
    glossary: list[GlossaryTerm] = Field(max_length=500)
    flashcards: list[Flashcard] = Field(min_length=1, max_length=1_000)
    worked_examples: list[PracticeExercise] = Field(max_length=500)
    practice_exercises: list[PracticeExercise] = Field(min_length=1, max_length=500)
    section_summaries: dict[Identifier, NonEmptyText]
    cumulative_summary: NonEmptyText
    review_sequence: list[ShortText] = Field(min_length=1, max_length=100)


class AssessmentBlueprintEntry(StrictContract):
    """Planned assessment coverage before individual items are authored."""

    objective_id: Identifier
    section_ids: list[Identifier] = Field(min_length=1, max_length=50)
    item_count: Annotated[int, Field(gt=0, le=100)]
    total_points: Annotated[int, Field(gt=0, le=1_000)]
    difficulty: Literal["beginner", "intermediate", "advanced"]
    cognitive_skill: Literal[
        "recall",
        "understanding",
        "application",
        "analysis",
        "evaluation",
        "creation",
    ]


class AssessmentBlueprint(StrictContract):
    """Approved objective/skill/point plan created before question writing."""

    schema_version: SchemaVersion
    blueprint_id: Identifier
    course_id: Identifier
    passing_percentage: Annotated[int, Field(ge=0, le=100)]
    entries: list[AssessmentBlueprintEntry] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def ensure_objectives_are_unique(self) -> "AssessmentBlueprint":
        """Give each objective one unambiguous assessment allocation."""

        _require_unique(
            "assessment blueprint objective_id",
            [entry.objective_id for entry in self.entries],
        )
        return self


class AssessmentItem(StrictContract):
    """One student-facing item without answer leakage."""

    item_id: Identifier
    item_type: Literal[
        "multiple_choice",
        "multiple_select",
        "short_answer",
        "application",
        "analysis",
        "practical",
    ]
    prompt: NonEmptyText
    objective_id: Identifier
    section_ids: list[Identifier] = Field(min_length=1, max_length=50)
    evidence_ids: list[Identifier] = Field(min_length=1, max_length=50)
    difficulty: Literal["beginner", "intermediate", "advanced"]
    cognitive_skill: Literal[
        "recall",
        "understanding",
        "application",
        "analysis",
        "evaluation",
        "creation",
    ]
    points: Annotated[int, Field(gt=0, le=1_000)]
    options: list[ShortText] = Field(max_length=20)

    @model_validator(mode="after")
    def validate_options_for_item_type(self) -> "AssessmentItem":
        """Require choices only for choice-based item types."""

        is_choice_item = self.item_type in {"multiple_choice", "multiple_select"}
        if is_choice_item and len(self.options) < 2:
            raise ValueError("choice items require at least two options")
        if not is_choice_item and self.options:
            raise ValueError("non-choice items cannot include answer options")
        return self


class Assessment(StrictContract):
    """A student-facing assessment and its objective-level blueprint."""

    schema_version: SchemaVersion
    assessment_id: Identifier
    course_id: Identifier
    title: ShortText
    passing_percentage: Annotated[int, Field(ge=0, le=100)]
    blueprint: list[AssessmentBlueprintEntry] = Field(max_length=100)
    items: list[AssessmentItem] = Field(max_length=1_000)
    instructions: NonEmptyText

    @model_validator(mode="after")
    def validate_item_identifiers_and_blueprint_totals(self) -> "Assessment":
        """Make blueprint counts and points mechanically truthful."""

        _require_unique("assessment item_id", [item.item_id for item in self.items])
        _require_unique(
            "assessment blueprint objective_id",
            [entry.objective_id for entry in self.blueprint],
        )
        for entry in self.blueprint:
            matching_items = [
                item for item in self.items if item.objective_id == entry.objective_id
            ]
            if len(matching_items) != entry.item_count:
                raise ValueError(
                    f"blueprint item_count does not match {entry.objective_id}"
                )
            if sum(item.points for item in matching_items) != entry.total_points:
                raise ValueError(
                    f"blueprint total_points does not match {entry.objective_id}"
                )
        return self


class RubricCriterion(StrictContract):
    """One transparent grading criterion for an assessment answer."""

    criterion: ShortText
    points: Annotated[int, Field(gt=0, le=1_000)]
    description: NonEmptyText


class AnswerEntry(StrictContract):
    """Instructor-only answer, explanation, and grading rules."""

    item_id: Identifier
    section_ids: list[Identifier] = Field(min_length=1, max_length=50)
    evidence_ids: list[Identifier] = Field(min_length=1, max_length=50)
    correct_answers: list[NonEmptyText] = Field(min_length=1, max_length=50)
    explanation: NonEmptyText
    grading_criteria: list[ShortText] = Field(min_length=1, max_length=50)
    rubric: list[RubricCriterion] = Field(min_length=1, max_length=50)


class AnswerKey(StrictContract):
    """Instructor artifact kept separate from the student assessment."""

    schema_version: SchemaVersion
    answer_key_id: Identifier
    assessment_id: Identifier
    answers: list[AnswerEntry] = Field(max_length=1_000)

    @model_validator(mode="after")
    def ensure_answer_item_ids_are_unique(self) -> "AnswerKey":
        """Prevent two competing answers for one student item."""

        _require_unique(
            "answer key item_id",
            [answer.item_id for answer in self.answers],
        )
        return self


class AssessmentPackage(StrictContract):
    """One schema-constrained stage result with separate student/instructor forms."""

    schema_version: SchemaVersion
    assessment: Assessment
    answer_key: AnswerKey

    @model_validator(mode="after")
    def require_matching_assessment(self) -> "AssessmentPackage":
        """Prevent an answer sheet from drifting to another assessment."""

        if self.answer_key.assessment_id != self.assessment.assessment_id:
            raise ValueError("answer key assessment_id does not match assessment")
        return self


def _require_unique(identifier_name: str, identifiers: list[str]) -> None:
    """Raise a readable error when an identifier appears more than once."""

    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"duplicate {identifier_name}")


def _require_known(identifier_name: str, identifier: str, known_ids: set[str]) -> None:
    """Raise when one reference cannot be resolved."""

    if identifier not in known_ids:
        raise ValueError(f"unknown {identifier_name}: {identifier}")


def _require_known_many(
    identifier_name: str,
    identifiers: list[str],
    known_ids: set[str],
) -> None:
    """Resolve a list of references against one authoritative identifier set."""

    for identifier in identifiers:
        _require_known(identifier_name, identifier, known_ids)
