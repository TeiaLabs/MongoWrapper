from typing import Any, Optional

from ..instance import database as client


class CountDocumentsMixin:
    __collection__ = "base"

    @classmethod
    async def count(
        cls, attribute_path: str, filters: Optional[dict[str, Any]] = None
    ) -> Any:
        """
        Count root-level array attributes.
        
        TODO: count arbitrarily nested arrays.
        """
        col = client.database[cls.__collection__]
        unwinds, project = build_aggregate(cls, attribute_path)
        c = col.aggregate(
            [
                {"$match": filters if filters else {}},
                *unwinds,
                project
            ]
        )
        docs = await c.to_list()
        return docs


def build_aggregate(model: BaseModel, attribute_path: str, parent: str = "") -> tuple:
    splitted_fields = attribute_path.split(".")
    current_field = attribute_path.split(".")[0]
    unwind = [{
        "$unwind": f"${parent}{current_field}" if parent else f"${current_field}"
    }]
    project = {field: f"${parent}{field}" for field in model.__annotations__.keys()}

    if "." not in attribute_path:
        project[current_field] = {
            "$size": f"${parent}{current_field}"
        }
        return unwind, project
    
    sub_type = model.__fields__[current_field].type_
    sub_field = ".".join(splitted_fields[1:])
    sub_parent = parent + current_field if parent else current_field

    sub_unwind, sub_project = build_aggregate(sub_type, sub_field, sub_parent + ".")

    unwind.extend(sub_unwind)
    project[current_field] = sub_project

    return unwind, project