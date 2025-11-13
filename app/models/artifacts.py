from typing_extensions import Self
from typing import Optional

from pydantic import (
    BaseModel, 
    model_validator, 
    field_validator,
    computed_field,
)


class CubeDimensions(BaseModel):
    horizontal: str
    vertical: str
    positive_in_i: Optional[bool] = None
    positive_in_j: Optional[bool] = None
    positive_in_k: Optional[bool] = None

    @model_validator(mode='after')
    def check_if_only_two_dimensions(self) -> Self:
        if self.positive_in_i is not None and self.positive_in_j is not None and self.positive_in_k is not None:
            raise ValueError("The cube can only represent 2 dimensions, but 3 were given.")
        
        elif (
            self.positive_in_i is not None and self.positive_in_j is not None or
            self.positive_in_i is not None and self.positive_in_k is not None or
            self.positive_in_j is not None and self.positive_in_k is not None
        ):
            return self

        else:
            raise ValueError("The cube can only represent 2 dimensions, but only 1 was given.")

    @model_validator(mode='after')
    def check_vertical_dimension_alias(self) -> Self:
        if self.vertical not in ['i', 'j', 'k']:
            raise ValueError("The vertical dimention must either: 'i', 'j' or 'k'.")
        if getattr(self, f'positive_in_{self.vertical}') is not None:
            return self
        raise ValueError("The vertical position value is empty, even though it is used.")

    @model_validator(mode='after')
    def check_horizontal_dimension_alias(self) -> Self:
        if self.horizontal not in ['i', 'j', 'k']:
            raise ValueError("The horizontal dimention must either: 'i', 'j' or 'k'.")
        if getattr(self, f'positive_in_{self.horizontal}') is not None:
            return self
        raise ValueError("The horizontal position value is empty, even though it is used.")

    @model_validator(mode='after')
    def check_dimension_conflict(self) -> Self:
        if self.horizontal != self.vertical:
            return self
        raise ValueError("The horizontal dimension must be differente from the vertical dimension.")



class GridPositions(BaseModel):
    vertical_position: int
    horizontal_position: int

    @field_validator("vertical_position", "horizontal_position", mode="plain")
    @classmethod
    def position_adjustment(cls, position: int) -> int:
        if position > 0:
            return 1
        elif position < 0:
            return -1
        else:
            return 0



class Vector(BaseModel):
    cube: CubeDimensions
    grid: GridPositions

    @computed_field
    @property
    def reading(self) -> list[int,int,int]:
        vector = [0,0,0]
        for i, d in enumerate(['i','j','k']):
            if self.cube.horizontal == d:
                vector[i] = self.grid.horizontal_position
                if not getattr(self.cube, f'positive_in_{d}'):
                    vector[i] *= -1 

            if self.cube.vertical == d:
                vector[i] = self.grid.vertical_position
                if not getattr(self.cube, f'positive_in_{d}'):
                    vector[i] *= -1

        return vector
