from pydantic import BaseModel, Field, validator
from typing import Optional

# ============================
# MODELO PRINCIPAL DE CARGA
# ============================
class CargoItem(BaseModel):
    # INFORMACIÓN GENERAL
    role: str = Field(..., description="Rol del usuario que ingresa la carga")
    lang: str = Field(..., description="Idioma del formulario")
    cargoType: str = Field(..., description="Tipo de carga: Perishable, DG, Mixed")

    # BLOQUE LEGAL
    sli: Optional[str] = Field(None, description="SLI / Factura completa: Yes / No")
    embargo: Optional[str] = Field(None, description="Embargo / restricción: None / Restricted")

    # BLOQUE SEGURIDAD
    knownShipper: Optional[str] = Field(None, description="Known Shipper: Yes / No")

    # BLOQUE FÍSICO / EMBALAJE
    material: Optional[str] = Field(None, description="Material del embalaje: Wood / Plastic")
    height: Optional[float] = Field(None, description="Altura de la carga en cm")
    weightDiff: Optional[float] = Field(None, description="Diferencia Peso Báscula vs Guía en %")

    # BLOQUE PERECEDEROS
    tempRange: Optional[str] = Field(None, description="Rango de temperatura para perecederos")
    iceType: Optional[str] = Field(None, description="Tipo de hielo: DryIce / Regular")

    # BLOQUE DG (Dangerous Goods)
    dgd: Optional[str] = Field(None, description="DGD firmada: Yes / No")
    unNumber: Optional[str] = Field(None, description="Número UN de la carga peligrosa")

    # VALIDACIONES INTELIGENTES
    @validator("height")
    def validate_height(cls, v):
        if v is not None and v <= 0:
            raise ValueError("La altura debe ser mayor que 0 cm")
        return v

    @validator("weightDiff")
    def validate_weight(cls, v):
        if v is not None and v < 0:
            raise ValueError("La diferencia de peso no puede ser negativa")
        return v

    @validator("cargoType")
    def validate_cargo_type(cls, v):
        allowed = ["Perishable", "DG", "Mixed"]
        if v not in allowed:
            raise ValueError(f"Tipo de carga inválido. Debe ser uno de {allowed}")
        return v

# ============================
# MODELO DE RESPUESTA DEL SISTEMA
# ============================
class ValidationResponse(BaseModel):
    status: str = Field(..., description="Semáforo de la validación: GREEN, YELLOW, RED")
    analysis: str = Field(..., description="Análisis detallado de las validaciones")
    disclaimer: str = Field(..., description="Aviso legal y recomendaciones de acción")
