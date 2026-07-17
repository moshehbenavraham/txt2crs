# SPDX-License-Identifier: MIT-0

"""Tests for deterministic, accessible, active-content-free rendering."""

from io import BytesIO

import fitz  # type: ignore[import-untyped]
import pytest
from docx import Document

from tests.factories import (
    valid_answer_key_data,
    valid_assessment_data,
    valid_course_data,
    valid_review_pack_data,
)
from txt2crs.domain.models import AnswerKey, Assessment, Course, ReviewPack
from txt2crs.domain.validation import ArtifactBundle, validate_artifact_bundle
from txt2crs.rendering.artifacts import (
    ArtifactRenderer,
    RenderedOutputQaError,
    derive_safe_filename,
    validate_rendered_html,
)


def valid_bundle() -> ArtifactBundle:
    """Return the cross-validated artifact bundle used by render tests."""

    return validate_artifact_bundle(
        course=Course.model_validate(valid_course_data()),
        review_pack=ReviewPack.model_validate(valid_review_pack_data()),
        assessment=Assessment.model_validate(valid_assessment_data()),
        answer_key=AnswerKey.model_validate(valid_answer_key_data()),
    )


def test_filename_is_deterministic_ascii_and_path_safe() -> None:
    """Filename generation never needs a model and cannot traverse paths."""

    assert derive_safe_filename("../../Python: Variables?!") == "python-variables"
    assert derive_safe_filename("  קורס Python  ") == "python"
    assert derive_safe_filename("...") == "course"


def test_course_html_escapes_untrusted_content_and_is_semantic() -> None:
    """Model text is data: scripts render as text, not active markup."""

    bundle = valid_bundle()
    bundle.course.modules[0].sections[0].content_blocks[
        0
    ].text = "<script>alert('unsafe')</script> A variable."
    renderer = ArtifactRenderer()

    rendered = renderer.render_bundle(bundle)
    course_html = rendered["course_html"].content.decode("utf-8")

    assert '<html lang="en" dir="ltr">' in course_html
    assert '<main id="course-content">' in course_html
    assert "<h1>Python Basics</h1>" in course_html
    assert "&lt;script&gt;" in course_html
    assert "<script>" not in course_html
    assert 'id="bibliography"' in course_html
    validate_rendered_html(
        course_html,
        required_element_ids={"course-content", "bibliography"},
    )


def test_student_assessment_never_contains_instructor_answers() -> None:
    """Answers, explanations, and rubrics stay in the instructor artifact."""

    rendered = ArtifactRenderer().render_bundle(valid_bundle())
    student_html = rendered["assessment_html"].content.decode("utf-8")
    instructor_html = rendered["answer_key_html"].content.decode("utf-8")

    assert "class_size = 24" not in student_html
    assert "class_size = 24" in instructor_html
    assert "Correct assignment" in instructor_html


def test_every_deliverable_has_html_markdown_searchable_pdf_and_docx() -> None:
    """Learners and instructors receive portable formats for every artifact."""

    rendered = ArtifactRenderer().render_bundle(valid_bundle())

    assert set(rendered) == {
        "course_html",
        "course_markdown",
        "course_pdf",
        "course_docx",
        "review_pack_html",
        "review_pack_markdown",
        "review_pack_pdf",
        "review_pack_docx",
        "assessment_html",
        "assessment_markdown",
        "assessment_pdf",
        "assessment_docx",
        "answer_key_html",
        "answer_key_markdown",
        "answer_key_pdf",
        "answer_key_docx",
    }
    for artifact_name in (
        "course_pdf",
        "review_pack_pdf",
        "assessment_pdf",
        "answer_key_pdf",
    ):
        pdf_document = fitz.open(
            stream=rendered[artifact_name].content,
            filetype="pdf",
        )
        try:
            extracted_text = "\n".join(
                page.get_text("text") for page in pdf_document
            )
        finally:
            pdf_document.close()
        assert extracted_text.strip()

    for artifact_name in (
        "course_docx",
        "review_pack_docx",
        "assessment_docx",
        "answer_key_docx",
    ):
        document = Document(BytesIO(rendered[artifact_name].content))
        extracted_text = "\n".join(
            paragraph.text for paragraph in document.paragraphs
        )
        assert extracted_text.strip()


def test_renderers_include_every_canonical_course_and_review_section() -> None:
    """A validated field cannot disappear merely because rendering succeeded."""

    rendered = ArtifactRenderer().render_bundle(valid_bundle())
    course_html = rendered["course_html"].content.decode("utf-8")
    review_html = rendered["review_pack_html"].content.decode("utf-8")

    for expected_course_text in (
        "Basic computer literacy",
        "This module introduces Python variables.",
        "A variable is not a permanent storage location.",
        "student_count = 24",
        "A name bound to a value.",
    ):
        assert expected_course_text in course_html
    for expected_review_text in (
        "The equals sign is assignment",
        "A name bound to a value.",
        "Store the class size.",
        "Variables name values.",
        "Read the guide",
        "The Python Tutorial",
    ):
        assert expected_review_text in review_html


def test_rtl_course_uses_document_direction_and_searchable_pdf() -> None:
    """RTL metadata reaches HTML and the deterministic PDF contains real text."""

    bundle = valid_bundle()
    bundle.course.language = "he"
    bundle.course.title = "מבוא למשתנים"
    rendered = ArtifactRenderer().render_bundle(bundle)

    course_html = rendered["course_html"].content.decode("utf-8")
    course_pdf = rendered["course_pdf"].content
    pdf_document = fitz.open(stream=course_pdf, filetype="pdf")
    try:
        extracted_pdf_text = "\n".join(page.get_text("text") for page in pdf_document)
    finally:
        pdf_document.close()

    assert '<html lang="he" dir="rtl">' in course_html
    assert course_pdf.startswith(b"%PDF")
    assert "Variables" in extracted_pdf_text


@pytest.mark.parametrize(
    "unsafe_html",
    [
        '<main id="course-content"><script>alert(1)</script></main>',
        '<main id="course-content"><iframe src="https://evil.test"></iframe></main>',
        '<main id="course-content"><img src="https://evil.test/pixel"></main>',
        '<main id="course-content"><p onclick="steal()">Click</p></main>',
        '<main id="course-content">Bearer secret-token /home/ada/private</main>',
    ],
)
def test_rendered_output_qa_rejects_active_or_private_content(
    unsafe_html: str,
) -> None:
    """Post-render QA catches structure-independent safety/privacy failures."""

    with pytest.raises(RenderedOutputQaError):
        validate_rendered_html(
            unsafe_html,
            required_element_ids={"course-content"},
        )


def test_rendered_output_qa_rejects_missing_required_sections() -> None:
    """A visually plausible but incomplete document cannot be delivered."""

    with pytest.raises(RenderedOutputQaError, match="bibliography"):
        validate_rendered_html(
            '<main id="course-content">Course</main>',
            required_element_ids={"course-content", "bibliography"},
        )
