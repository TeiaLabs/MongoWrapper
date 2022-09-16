from typing import Any, Optional

from ..instance import database as client


class CountDocumentsMixin:
    __collection__: str
    @classmethod
    async def count(cls, filters: Optional[dict[str, Any]] = None) -> int:
        """Count documents filtered by root-level attrs."""
        col = client.database[cls.__collection__]
        c = await col.count_documents(filters if filters else {})
        return c

    @classmethod
    async def count_nested(
        cls, attribute_path: str, filters: Optional[dict[str, Any]] = None
    ) -> Any:
        """
        Count size of arbitrarily nested lists.
        """
        col = client.database[cls.__collection__]
        unwinds, project = build_aggregate(cls, attribute_path)
        c = col.aggregate(
            [
                {"$match": filters if filters else {}},
                *unwinds,
                {"$project": project}
            ]
        )
        docs = await c.to_list(None)
        return docs


def build_aggregate(model: CountDocumentsMixin, attribute_path: str, parent: str = "") -> tuple:
    splitted_fields = attribute_path.split(".")
    current_field = attribute_path.split(".")[0]
    project = {field: f"${parent}{field}" for field in model.__fields__}

    if "." not in attribute_path:
        project[current_field] = {
            "$size": f"${parent}{current_field}"
        }
        return [], project

    sub_type = model.__fields__[current_field].type_
    sub_field = ".".join(splitted_fields[1:])
    sub_parent = parent + current_field if parent else current_field

    sub_unwind, sub_project = build_aggregate(sub_type, sub_field, sub_parent + ".")

    unwind = [{
        "$unwind": f"${parent}{current_field}" if parent else f"${current_field}"
    }]
    unwind.extend(sub_unwind)
    project[current_field] = sub_project

    return unwind, project
