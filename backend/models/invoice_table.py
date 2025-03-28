# Copyright (c) TaKo AI Sp. z o.o.

from datetime import date, datetime
from typing import Any, List, Tuple

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from backend.models.base import Base
from backend.models.business_table import BusinessTable
from backend.models.client_table import ClientTable
from backend.models.product_table import ProductTable


class InvoiceTable(Base):
    __tablename__ = "invoice"

    invoiceID = Column(
        "invoiceID", String, primary_key=True, default=Base.generate_uuid
    )
    invoiceNo = Column("invoiceNo", String)
    currency = Column("currency", String)
    vatPercent = Column("vatPercent", Integer)
    issuedAt = Column("issuedAt", String)
    dueTo = Column("dueTo", String)
    note = Column("note", String)
    business_id = Column(String, ForeignKey("business.businessID"))
    client_id = Column(String, ForeignKey("client.clientID"))

    business = relationship("BusinessTable")
    client = relationship("ClientTable")

    language = Column("language", String)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.invoiceNo = kwargs["invoiceNo"]
        self.currency = kwargs["currency"]
        self.vatPercent = kwargs["vatPercent"]
        self.issuedAt = kwargs["issuedAt"]
        self.dueTo = kwargs["dueTo"]
        self.note = kwargs["note"]
        self.business_id = kwargs["business_id"]
        self.client_id = kwargs["client_id"]
        self.language = kwargs["language"]

    def to_json(
        self, business: BusinessTable, client: ClientTable, products: List[ProductTable]
    ) -> dict:
        def parse_date(date_str: str) -> date:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return datetime.strptime(date_str, "%d/%m/%Y").date()

        return {
            "invoiceID": self.invoiceID,
            "invoiceNo": self.invoiceNo,
            "currency": self.currency,
            "vatPercent": self.vatPercent,
            "issuedAt": str(parse_date(str(self.issuedAt))) if self.issuedAt else None,
            "dueTo": str(parse_date(str(self.dueTo))) if self.dueTo else None,
            "note": self.note,
            "business": business.to_json(),
            "client": client.to_json(),
            "products": [product.to_json() for product in products],
            "language": self.language,
        }

    @staticmethod
    def from_json(
        data: dict, business_id: str, client_id: str
    ) -> Tuple["InvoiceTable", List[ProductTable]]:
        # Use existing invoice ID if provided, otherwise generate new one
        invoice_id = data.get("invoiceID", Base.generate_uuid())

        issued_at = data.get("issuedAt")
        due_to = data.get("dueTo")

        if isinstance(issued_at, date):
            issued_at = issued_at.strftime("%d/%m/%Y")
        if isinstance(due_to, date):
            due_to = due_to.strftime("%d/%m/%Y")

        invoice = InvoiceTable(
            invoiceID=invoice_id,
            invoiceNo=data.get("invoiceNo"),
            currency=data.get("currency"),
            vatPercent=data.get("vatPercent"),
            issuedAt=issued_at,
            dueTo=due_to,
            note=data.get("note"),
            language=data.get("language"),
            business_id=business_id,
            client_id=client_id,
        )

        products_data = data["products"]
        products = []
        for product_data in products_data:
            products.append(
                ProductTable.from_json(product_data, str(invoice.invoiceID))
            )

        return invoice, products
