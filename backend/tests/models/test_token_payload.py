from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.models import TokenPayload


def test_token_payload_parses_the_subject_as_a_uuid() -> None:
    """Database lookup receives the UUID type required by every dialect."""

    user_id = uuid4()

    payload = TokenPayload(sub=str(user_id))

    assert payload.sub == user_id
    assert isinstance(payload.sub, UUID)


def test_token_payload_rejects_a_non_uuid_subject() -> None:
    """A signed token with a malformed subject is still invalid."""

    with pytest.raises(ValidationError):
        TokenPayload(sub="not-a-user-uuid")
