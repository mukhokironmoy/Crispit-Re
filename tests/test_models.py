from sqlalchemy import CheckConstraint, Table, UniqueConstraint, inspect
from sqlalchemy.orm import Mapper, configure_mappers

from crispit.db.base import Base
from crispit.models import (
    Source,
    SourceSubscription,
    SummaryMode,
    TelegramIdentity,
    User,
    Video,
)


def test_all_models_are_registered() -> None:
    expected_tables = {
        "users",
        "telegram_identities",
        "summary_modes",
        "sources",
        "source_subscriptions",
        "videos",
    }

    assert set(Base.metadata.tables) == expected_tables


def test_all_models_have_uuid_primary_keys() -> None:
    models = (
        User,
        TelegramIdentity,
        SummaryMode,
        Source,
        SourceSubscription,
        Video,
    )

    for model in models:
        table = model.__table__
        assert isinstance(table, Table)

        primary_keys = list(table.primary_key.columns)

        assert len(primary_keys) == 1
        assert primary_keys[0].name == "id"
        assert primary_keys[0].type.python_type.__name__ == "UUID"


def test_foreign_keys() -> None:
    expected = {
        "telegram_identities": {"user_id": "users.id"},
        "summary_modes": {"owner_user_id": "users.id"},
        "source_subscriptions": {
            "user_id": "users.id",
            "source_id": "sources.id",
        },
        "videos": {"source_id": "sources.id"},
    }

    for table_name, references in expected.items():
        table = Base.metadata.tables[table_name]
        assert isinstance(table, Table)

        actual = {
            fk.parent.name: fk.target_fullname
            for fk in table.foreign_keys
        }

        assert actual == references


def test_unique_constraints() -> None:
    expected = {
        "telegram_identities": {
            "uq_telegram_identities_telegram_user_id"
        },
        "sources": {
            "uq_sources_youtube_channel_id"
        },
        "source_subscriptions": {
            "uq_source_subscriptions_user_source"
        },
        "videos": {
            "uq_videos_youtube_video_id"
        },
    }

    for table_name, constraint_names in expected.items():
        table = Base.metadata.tables[table_name]

        actual = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }

        assert actual == constraint_names


def test_summary_mode_ownership_constraints() -> None:
    table = SummaryMode.__table__
    assert isinstance(table, Table)

    check_names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    unique_index_names = {
        index.name
        for index in table.indexes
        if index.unique
    }

    assert "ck_summary_modes_ownership" in check_names

    assert unique_index_names == {
        "uq_summary_modes_builtin_key",
        "uq_summary_modes_owner_key",
    }


def test_orm_relationships() -> None:
    configure_mappers()

    expected = (
        (User, "telegram_identities", "user"),
        (TelegramIdentity, "user", "telegram_identities"),
        (User, "summary_modes", "owner"),
        (SummaryMode, "owner", "summary_modes"),
        (User, "source_subscriptions", "user"),
        (SourceSubscription, "user", "source_subscriptions"),
        (Source, "subscriptions", "source"),
        (SourceSubscription, "source", "subscriptions"),
        (Source, "videos", "source"),
        (Video, "source", "videos"),
    )

    for model, attribute, reverse_attribute in expected:
        mapper = inspect(model)
        assert isinstance(mapper, Mapper)

        relationship = mapper.relationships[attribute]
        assert relationship.back_populates == reverse_attribute
