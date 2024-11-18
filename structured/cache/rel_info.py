
class RelInfo:
    """
    A class that represents the relationship information of a model field.
    There are four types of relationships:
    - ForeignKey (FKField)
    - QuerySet (QSField)
    - Related Instance (RIField) -> A child model instance with caching capability
    - Related List (RLField) -> A list of child model instances with caching capability
    """

    FKField: str = "fk"
    QSField: str = "qs"
    RIField: str = "rel"
    RLField: str = "rel_l"

    def __init__(self, model, type, field) -> None:
        self.model = model
        self.type = type
        self.field = field
