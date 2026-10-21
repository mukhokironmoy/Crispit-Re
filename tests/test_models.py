from sqlalchemy import CheckConstraint, Table, UniqueConstraint, inspect
from sqlalchemy.orm import Mapper, configure_mappers

from crispit.db.base import Base
from crispit.models import (
    Delivery,
    DeliveryAttempt,
    DeliveryItem,
    DeliveryPreference,
    ProcessingJob,
    Source,
    SourceSubscription,
    Summary,
    SummaryMode,
    TelegramIdentity,
    User,
    Video,
)


def test_all_models_are_registered() -> None:
    # Every model must be registered before we create migrations.
    expected_tables = {
        "users",
        "telegram_identities",
        "summary_modes",
        "sources",
        "source_subscriptions",
        "videos",
        "processing_jobs",
        "summaries",
        "delivery_preferences",
        "deliveries",
        "delivery_items",
        "delivery_attempts",
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
        ProcessingJob,
        Summary,
        DeliveryPreference,
        Delivery,
        DeliveryItem,
        DeliveryAttempt,
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
        "telegram_identities": {
            "user_id": "users.id",
        },
        "summary_modes": {
            "owner_user_id": "users.id",
        },
        "source_subscriptions": {
            "user_id": "users.id",
            "source_id": "sources.id",
        },
        "videos": {
            "source_id": "sources.id",
        },
        "processing_jobs": {
            "video_id": "videos.id",
            "summary_mode_id": "summary_modes.id",
            "requested_by_user_id": "users.id",
        },
        "summaries": {
            "processing_job_id": "processing_jobs.id",
            "video_id": "videos.id",
            "summary_mode_id": "summary_modes.id",
        },
        "delivery_preferences": {
            "user_id": "users.id",
        },
        "deliveries": {
            "user_id": "users.id",
        },
        "delivery_items": {
            "delivery_id": "deliveries.id",
            "summary_id": "summaries.id",
        },
        "delivery_attempts": {
            "delivery_id": "deliveries.id",
        },
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
            "uq_telegram_identities_telegram_user_id",
        },
        "sources": {
            "uq_sources_youtube_channel_id",
        },
        "source_subscriptions": {
            "uq_source_subscriptions_user_source",
        },
        "videos": {
            "uq_videos_youtube_video_id",
        },
        "summaries": {
            "uq_summaries_processing_job_id",
        },
        "delivery_preferences": {
            "uq_delivery_preferences_user_id",
        },
        "deliveries": {
            "uq_deliveries_delivery_key",
        },
        "delivery_items": {
            "uq_delivery_items_delivery_summary",
            "uq_delivery_items_delivery_position",
        },
        "delivery_attempts": {
            "uq_delivery_attempts_delivery_number",
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


def test_summary_uses_versioned_jsonb() -> None:
    # Summaries store structured content rather than rendered text.
    table = Summary.__table__
    assert isinstance(table, Table)

    assert table.c.content.type.__class__.__name__ == "JSONB"
    assert table.c.content.nullable is False

    # Every saved summary must identify its content format version.
    assert table.c.schema_version.nullable is False

    check_names = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert "ck_summaries_schema_version" in check_names


def test_processing_and_delivery_constraints() -> None:
    # Verify the database rules used to protect jobs and deliveries.
    expected = {
        "processing_jobs": {
            "ck_processing_jobs_status",
            "ck_processing_jobs_attempts",
        },
        "delivery_preferences": {
            "ck_delivery_preferences_policy",
            "ck_delivery_preferences_output_format",
            "ck_delivery_preferences_time",
        },
        "deliveries": {
            "ck_deliveries_policy",
            "ck_deliveries_output_format",
            "ck_deliveries_status",
        },
        "delivery_items": {
            "ck_delivery_items_position",
        },
        "delivery_attempts": {
            "ck_delivery_attempts_status",
            "ck_delivery_attempts_attempt_number",
        },
    }

    for table_name, expected_names in expected.items():
        table = Base.metadata.tables[table_name]

        # Check that each model declares its expected database rules.
        actual_names = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        }

        assert actual_names == expected_names


def test_delivery_relationships() -> None:
    # Make sure deliveries can contain summaries and record retries.
    configure_mappers()

    expected = (
        (User, "deliveries", "user"),
        (Delivery, "user", "deliveries"),
        (User, "delivery_preference", "user"),
        (DeliveryPreference, "user", "delivery_preference"),
        (Delivery, "items", "delivery"),
        (DeliveryItem, "delivery", "items"),
        (Summary, "delivery_items", "summary"),
        (DeliveryItem, "summary", "delivery_items"),
        (Delivery, "attempts", "delivery"),
        (DeliveryAttempt, "delivery", "attempts"),
    )

    for model, attribute, reverse_attribute in expected:
        mapper = inspect(model)
        assert isinstance(mapper, Mapper)

        relationship = mapper.relationships[attribute]
        assert relationship.back_populates == reverse_attribute


def test_processing_relationships() -> None:
    # Verify links between jobs, summaries, videos, modes and users.
    configure_mappers()

    expected = (
        (Video, "processing_jobs", "video"),
        (ProcessingJob, "video", "processing_jobs"),
        (SummaryMode, "processing_jobs", "summary_mode"),
        (ProcessingJob, "summary_mode", "processing_jobs"),
        (User, "processing_jobs", "requested_by_user"),
        (ProcessingJob, "requested_by_user", "processing_jobs"),
        (ProcessingJob, "summary", "processing_job"),
        (Summary, "processing_job", "summary"),
        (Video, "summaries", "video"),
        (Summary, "video", "summaries"),
        (SummaryMode, "summaries", "summary_mode"),
        (Summary, "summary_mode", "summaries"),
    )

    for model, attribute, reverse_attribute in expected:
        mapper = inspect(model)
        assert isinstance(mapper, Mapper)

        relationship = mapper.relationships[attribute]
        assert relationship.back_populates == reverse_attribute

    # One processing job produces at most one summary.
    job_mapper = inspect(ProcessingJob)
    assert isinstance(job_mapper, Mapper)
    assert job_mapper.relationships["summary"].uselist is False
