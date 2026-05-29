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

    Fields:
        shipment_id: Raw unique identifier for the shipment.
        sample_id: Raw sample identifier connected to the shipment.
        courier: Raw courier or carrier name.
        shipped_at_raw: Raw datetime when the shipment was sent.
        received_at_raw: Raw datetime when the shipment was received.
        condition_temp_c_raw: Raw shipment temperature value before numeric
            validation.
        status: Raw shipment status, such as delivered, delayed, pending, or
            cancelled.
        api_updated_at_raw: Raw datetime when the API record was last updated.
        metadata: Ingestion metadata describing where the record came from.
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