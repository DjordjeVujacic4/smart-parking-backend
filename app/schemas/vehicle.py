from pydantic import BaseModel, ConfigDict, Field, field_validator


class VehicleCreate(BaseModel):
    license_plate: str = Field(min_length=1, max_length=20)
    make: str | None = Field(default=None, max_length=50)
    model: str | None = Field(default=None, max_length=50)

    @field_validator("license_plate")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        return value.strip().upper()


class VehicleUpdate(BaseModel):
    license_plate: str | None = Field(default=None, min_length=1, max_length=20)
    make: str | None = Field(default=None, max_length=50)
    model: str | None = Field(default=None, max_length=50)

    @field_validator("license_plate")
    @classmethod
    def normalize_plate(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else value


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    license_plate: str
    make: str | None
    model: str | None
