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


def test_answer_key_discloses_evidence_sources_without_leaking_them_to_student() -> (
    None
):
    """Instructor answers retain usable evidence links from canonical course data."""

    rendered = ArtifactRenderer().render_bundle(valid_bundle())
    student_html = rendered["assessment_html"].content.decode("utf-8")
    instructor_html = rendered["answer_key_html"].content.decode("utf-8")
    instructor_markdown = rendered["answer_key_markdown"].content.decode("utf-8")

    assert "Evidence sources" not in student_html
    assert "The Python Tutorial" not in student_html
    for instructor_text in (instructor_html, instructor_markdown):
        assert "Evidence sources" in instructor_text
        assert "The Python Tutorial" in instructor_text
        assert "https://docs.python.org/3/tutorial/" in instructor_text


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
            extracted_text = "\n".join(page.get_text("text") for page in pdf_document)
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
        extracted_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
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


def test_review_renderers_replace_internal_identifiers_with_reader_labels() -> None:
    """Canonical IDs support validation but must not become learner-facing prose."""

    bundle = valid_bundle()
    bundle.review_pack.review_sequence = [
        (
            "Review `sec-variables`, use the `obj-variables` flashcards, "
            "check `card-variable`, then complete `worked-variable` and "
            "`practice-variable`."
        )
    ]

    rendered = ArtifactRenderer().render_bundle(bundle)
    review_html = rendered["review_pack_html"].content.decode("utf-8")
    review_markdown = rendered["review_pack_markdown"].content.decode("utf-8")

    for internal_identifier in (
        "obj-variables",
        "sec-variables",
        "card-variable",
        "worked-variable",
        "practice-variable",
    ):
        assert internal_identifier not in review_html
        assert internal_identifier not in review_markdown
    for reader_label in (
        "Objective 1: Explain and use Python variables.",
        "Variables",
        "Flashcard 1",
        "Worked example 1",
        "Practice exercise 1",
    ):
        assert reader_label in review_html
        assert reader_label in review_markdown


def test_review_headings_survive_valid_cross_namespace_identifier_collisions() -> None:
    """Exercise IDs must not replace objective or section labels in headings."""

    bundle = valid_bundle()
    objective_id = bundle.course.learning_objectives[0].objective_id
    section = bundle.course.modules[0].sections[0]
    bundle.review_pack.worked_examples[0].exercise_id = objective_id
    bundle.review_pack.practice_exercises[0].exercise_id = section.section_id

    rendered = ArtifactRenderer().render_bundle(bundle)
    review_html = rendered["review_pack_html"].content.decode("utf-8")
    review_markdown = rendered["review_pack_markdown"].content.decode("utf-8")

    expected_objective_heading = "Objective 1: Explain and use Python variables."
    assert expected_objective_heading in review_html
    assert expected_objective_heading in review_markdown
    assert "<dt>Variables</dt>" in review_html
    assert "- **Variables:**" in review_markdown


def test_review_renderers_humanize_unresolved_identifier_shaped_prose() -> None:
    """Free-form review steps must not expose stale IDs or schema field names."""

    bundle = valid_bundle()
    bundle.review_pack.review_sequence = [
        (
            "Review objective `obj-variables` instead of stale lo9, complete "
            "`practice-missing-reference` in section-9-stale-title, then "
            "revisit sec9 and the referenced `section_id` before pe9."
        )
    ]

    rendered = ArtifactRenderer().render_bundle(bundle)
    review_text_by_format = {
        "html": rendered["review_pack_html"].content.decode("utf-8"),
        "markdown": rendered["review_pack_markdown"].content.decode("utf-8"),
    }
    pdf_document = fitz.open(
        stream=rendered["review_pack_pdf"].content,
        filetype="pdf",
    )
    try:
        review_text_by_format["pdf"] = "\n".join(
            page.get_text("text") for page in pdf_document
        )
    finally:
        pdf_document.close()
    review_document = Document(BytesIO(rendered["review_pack_docx"].content))
    review_text_by_format["docx"] = "\n".join(
        paragraph.text for paragraph in review_document.paragraphs
    )

    for review_text in review_text_by_format.values():
        assert "Review Objective 1" in review_text
        assert "Review objective Objective 1" not in review_text
        assert "Practice exercise" in review_text
        assert "practice-missing-reference" not in review_text
        assert "the related section" in review_text
        assert "section-9-stale-title" not in review_text
        assert "section_id" not in review_text
        assert "lo9" not in review_text
        assert "sec9" not in review_text
        assert "pe9" not in review_text


def test_empty_optional_course_collections_do_not_render_empty_sections() -> None:
    """An optional empty list must not leave a misleading blank publication section."""

    bundle = valid_bundle()
    bundle.course.modules[0].misconceptions = []
    bundle.course.modules[0].examples = []

    rendered = ArtifactRenderer().render_bundle(bundle)
    course_html = rendered["course_html"].content.decode("utf-8")
    course_markdown = rendered["course_markdown"].content.decode("utf-8")

    assert "Common misconceptions" not in course_html
    assert "Common misconceptions" not in course_markdown
    assert ">Examples<" not in course_html
    assert "### Examples" not in course_markdown


def test_pdf_and_docx_convert_inline_markdown_to_readable_text() -> None:
    """Portable binary formats must not expose backticks or Markdown link syntax."""

    bundle = valid_bundle()
    bundle.review_pack.review_sequence = ["Run `python --version` before review."]
    rendered = ArtifactRenderer().render_bundle(bundle)

    pdf_document = fitz.open(
        stream=rendered["review_pack_pdf"].content,
        filetype="pdf",
    )
    try:
        review_pdf_text = "\n".join(page.get_text("text") for page in pdf_document)
    finally:
        pdf_document.close()
    course_document = Document(BytesIO(rendered["course_docx"].content))
    course_docx_text = "\n".join(
        paragraph.text for paragraph in course_document.paragraphs
    )

    assert "`python --version`" not in review_pdf_text
    assert "python --version" in review_pdf_text
    assert "[The Python Tutorial](" not in course_docx_text
    assert "The Python Tutorial" in course_docx_text
    assert "https://docs.python.org/3/tutorial/" in course_docx_text


def test_pdf_normalizes_common_typographic_punctuation() -> None:
    """English smart punctuation must remain readable with the built-in PDF font."""

    bundle = valid_bundle()
    bundle.course.modules[0].sections[0].content_blocks[
        0
    ].text = "A client\u2019s resolver\u2014when ready\u2014answers \u201csafely\u201d."

    rendered = ArtifactRenderer().render_bundle(bundle)
    pdf_document = fitz.open(
        stream=rendered["course_pdf"].content,
        filetype="pdf",
    )
    try:
        course_pdf_text = "\n".join(page.get_text("text") for page in pdf_document)
    finally:
        pdf_document.close()

    assert "client's resolver-when ready-answers" in course_pdf_text
    assert '"safely"' in course_pdf_text
    assert "client-s" not in course_pdf_text


def test_summary_label_removes_one_model_supplied_leading_colon() -> None:
    """The deterministic Summary label must not produce a visible double colon."""

    bundle = valid_bundle()
    bundle.course.modules[0].sections[
        0
    ].summary = ": Variables give useful names to values."

    rendered = ArtifactRenderer().render_bundle(bundle)
    course_html = rendered["course_html"].content.decode("utf-8")
    course_markdown = rendered["course_markdown"].content.decode("utf-8")

    assert "Summary:</strong> Variables give" in course_html
    assert "Summary:</strong> :" not in course_html
    assert "**Summary:** Variables give" in course_markdown
    assert "**Summary:** :" not in course_markdown


def test_assessment_renderers_use_singular_point_grammar() -> None:
    """A one-point item should read naturally in every student format."""

    bundle = valid_bundle()
    bundle.assessment.blueprint[0].total_points = 1
    bundle.assessment.items[0].points = 1
    bundle.answer_key.answers[0].rubric[0].points = 1

    rendered = ArtifactRenderer().render_bundle(bundle)
    assessment_html = rendered["assessment_html"].content.decode("utf-8")
    assessment_markdown = rendered["assessment_markdown"].content.decode("utf-8")
    pdf_document = fitz.open(
        stream=rendered["assessment_pdf"].content,
        filetype="pdf",
    )
    try:
        assessment_pdf_text = "\n".join(page.get_text("text") for page in pdf_document)
    finally:
        pdf_document.close()

    for assessment_text in (
        assessment_html,
        assessment_markdown,
        assessment_pdf_text,
    ):
        assert "(1 point)" in assessment_text
        assert "(1 points)" not in assessment_text


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
