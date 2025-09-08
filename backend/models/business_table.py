# Copyright (c) TaKo AI Sp. z o.o.

import base64
from typing import Any

from sqlalchemy import Column, LargeBinary, String, TypeDecorator

from backend.models.base import Base


class BinaryString(TypeDecorator):
    impl = LargeBinary
    process_bind_param = lambda self, value, dialect: (
        value.encode("utf-8") if isinstance(value, str) else value
    )
    process_result_value = lambda self, value, dialect: value


class BusinessTable(Base):
    __tablename__ = "business"
    businessID = Column(
        "businessID", String, primary_key=True, default=Base.generate_uuid
    )
    name = Column("name", String, unique=True)
    street = Column("street", String)
    postCode = Column("postCode", String)
    town = Column("town", String)
    country = Column("country", String)
    vatNo = Column("vatNo", String, unique=True)
    bic = Column("bic", String, unique=True)
    iban = Column("iban", String)
    phone = Column("phone", String)
    email = Column("email", String)
    logo = Column("logo", BinaryString, nullable=True)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.name = kwargs["name"]
        self.street = kwargs["street"]
        self.postCode = kwargs["postCode"]
        self.town = kwargs["town"]
        self.country = kwargs["country"]
        self.vatNo = kwargs["vatNo"]
        self.bic = kwargs.get("bic", "")
        self.iban = kwargs.get("iban", "")
        self.phone = kwargs.get("phone", "")
        self.email = kwargs.get("email", "")
        self.logo = kwargs.get("logo")

    def to_json(self) -> dict:
        # Handle logo encoding safely
        logo_encoded = None
        if self.logo:
            if isinstance(self.logo, str):
                # Already a base64 string
                logo_encoded = self.logo
            else:
                # Binary data that needs encoding
                logo_encoded = base64.b64encode(self.logo).decode()

        return {
            "businessID": self.businessID,
            "name": self.name,
            "street": self.street,
            "postCode": self.postCode,
            "town": self.town,
            "country": self.country,
            "vatNo": self.vatNo,
            "bic": self.bic,
            "iban": self.iban,
            "phone": self.phone,
            "email": self.email,
            "logo": logo_encoded,
        }

    @staticmethod
    def from_json(data: dict) -> "BusinessTable":
        logo_data = None
        if data.get("logo"):
            try:
                # Check if it's already binary data
                if isinstance(data["logo"], bytes):
                    logo_data = data["logo"]
                else:
                    # Assume it's a base64 string
                    logo_data = base64.b64decode(data["logo"])
            except Exception:
                logo_data = None

        return BusinessTable(
            businessID=data.get("businessID", Base.generate_uuid()),
            name=data["name"],
            street=data["street"],
            postCode=data["postCode"],
            town=data["town"],
            country=data["country"],
            vatNo=data["vatNo"],
            bic=data.get("bic", ""),
            iban=data.get("iban", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            logo=logo_data,
        )
