from __future__ import annotations

from dataclasses import dataclass

from .utils import PyObjectId


@dataclass(frozen=True, slots=True)
class CreateResult:
    inserted_id: PyObjectId


@dataclass(frozen=True, slots=True)
class BatchCreateResult:
    inserted_ids: list[PyObjectId]


@dataclass(frozen=True, slots=True)
class UpdateResult:
    matched_count: int
    modified_count: int


@dataclass(frozen=True, slots=True)
class UpsertResult(UpdateResult):
    upserted_id: PyObjectId


@dataclass(frozen=True, slots=True)
class DeleteResult:
    deleted_count: int
