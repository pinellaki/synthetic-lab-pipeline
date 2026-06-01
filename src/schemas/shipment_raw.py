"""Raw shipment schema.

This module defines the ShipmentRaw model.

The model represents one raw shipment record before standardization,
validation, and database loading.
"""

from pydantic import BaseModel

from src.schemas.ingestion_metadata import IngestionMetadata


class ShipmentRaw(BaseModel):
    """Represent one raw shipment record.

    This schema stores shipment values as they are read from a source file or
    API response. Most fields are optional because shipment data can be missing,
    delayed, incomplete, or updated later.

    The model stores shipment identifiers, sample identifiers, courier
    information, shipped and received datetime values, shipment temperature,
    status, API update time, and ingestion metadata.
    """

    shipment_id: str | None = None
    sample_id: str | None = None
    courier: str | None = None
    shipped_at_raw: str | None = None
    received_at_raw: str | None = None
    condition_temp_c_raw: str | None = None
    status: str | None = None
    api_updated_at_raw: str | None = None

    metadata: IngestionMetadata