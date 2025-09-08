# Copyright (c) TaKo AI Sp. z o.o.

import base64
import os
import subprocess
import tempfile

from frontend.domain.entities.invoice_entity import InvoiceEntity
from frontend.domain.entities.product_entity import ProductEntity
from frontend.utils.const import assets_path, product_latex_template
from frontend.utils.translations import TRANSLATIONS


class Generator:
    def __init__(self) -> None:
        layout_path = os.path.join(assets_path, "layout.tex")
        with open(layout_path, "r") as f:
            self.layout = f.read()

    def substitute(self, key: str, value: str | None) -> None:
        self.layout = self.layout.replace(key, str(value))

    def append_products(
        self, products: list[ProductEntity], invoice: InvoiceEntity, translations: dict
    ) -> None:
        product_latex = ""
        for product in products:
            product_price = product.price
            product_vat_percent = invoice.vatPercent
            product_vat_amount = product_price * (product_vat_percent / 100)
            product_sum = (product_price + product_vat_amount) * product.quantity

            formatted_price = f"{product_price:.2f}"
            formatted_vat = (
                f"{product_vat_percent * product_price / 100:.2f}"  # noqa: W605
            )
            formatted_sum = f"{product_sum:.2f}"

            product_line = product_latex_template.format(
                description=product.description,
                quantity=str(product.quantity),
                unit=product.unit,
                price=formatted_price,
                vat=formatted_vat,
                sum=formatted_sum,
            )
            product_latex += product_line

        self.substitute("% PRODUCTS %", product_latex)

    def substitute_table(self, invoice: InvoiceEntity, translations: dict) -> None:
        self.substitute("TABLE1", translations["description"])
        self.substitute("TABLE2", translations["quantity"])
        self.substitute("TABLE3", translations["unit"])
        self.substitute("TABLE4", translations["price"])
        self.substitute(
            "TABLE5", f"{translations['vat']} ({str(invoice.vatPercent)}\%)"  # noqa: W605
        )
        self.substitute("TABLE6", translations["total"])

    def substitute_invoice_details(
        self, invoice: InvoiceEntity, translations: dict
    ) -> None:
        print(invoice)
        try:
            invoice.are_all_fields_filled()
        except ValueError as e:
            raise e

        details = {
            "LINE10": "IBAN",
            "LINE11": invoice.business.iban,
            "INVOICE": translations["invoice"],
            "INO": invoice.invoiceNo,
            "ISSUEDATTEXT": translations["issued_at"],
            "ISSUEDDATE": (
                invoice.issuedAt.strftime("%Y-%m-%d") if invoice.issuedAt else ""
            ),
            "DUETOTEXT": translations["due_to"],
            "DUETODATE": (invoice.dueTo.strftime("%Y-%m-%d") if invoice.dueTo else ""),
            "CLIENTLINE1": invoice.client.name,
            "CLIENTLINE2": invoice.client.street,
            "CLIENTLINE3": f"{invoice.client.town}, {invoice.client.country}",
            "CLIENTLINE4": f"{translations['vat_no']} {invoice.client.vatNo}",
            "CLIENTLINE6": translations["notes"],
            "CLIENTLINE7": invoice.note,
            "LINE1": invoice.business.name,
            "LINE2": invoice.business.street,
            "LINE3": invoice.business.town,
            "LINE4": invoice.business.phone,
            "LINE5": invoice.business.email,
            "LINE6": translations["vat"],
            "LINE7": invoice.business.vatNo,
            "LINE8": translations["bic"],
            "LINE9": invoice.business.bic,
        }
        for key, value in details.items():
            self.substitute(key, value)

    def generate(self, invoice: InvoiceEntity, language: str = "en") -> bytes | None:
        translations = TRANSLATIONS.get(language, TRANSLATIONS["en"])

        self.substitute_invoice_details(invoice, translations)
        self.substitute_table(invoice, translations)
        self.append_products(invoice.products, invoice, translations)

        net_sum = sum(product.price * product.quantity for product in invoice.products)
        total_vat = sum(
            product.price
            * product.quantity
            * (invoice.vatPercent / 100 if invoice.vatPercent else 0)
            for product in invoice.products
        )
        total_sum = net_sum + total_vat

        currency_code = translations.get(
            f"currency_{invoice.currency.lower()}", invoice.currency
        )

        self.substitute("TOTAL1", translations["subtotal"])
        self.substitute("TOTAL2", f"{net_sum:.2f}")
        self.substitute("TOTAL3", f"{total_vat:.2f}")
        self.substitute("TOTAL4", translations["total_sum"] + f" {currency_code}")
        self.substitute("TOTAL5", f"{total_sum:.2f}")

        # Calculate days between issue date and due date
        days = 14  # Default value
        if invoice.issuedAt and invoice.dueTo:
            days = (invoice.dueTo - invoice.issuedAt).days

        # Add payment instructions as footer
        payment_instructions = translations["payment_instructions"].format(
            days=days,
            account_number=invoice.business.iban,
            invoice_no=invoice.invoiceNo,
        )
        self.substitute("FOOTERTEXT", payment_instructions)

        if invoice.business.logo:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_file.write(base64.b64decode(invoice.business.logo))
                self.substitute("logo.png", temp_file.name)
        else:
            self.substitute("logo.png", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            font_dir = os.path.join(temp_dir, "FontFiles")
            os.makedirs(font_dir, exist_ok=True)

            # Copy font files
            source_font_dir = os.path.join(assets_path, "FontFiles")
            if os.path.exists(source_font_dir):
                for font_file in os.listdir(source_font_dir):
                    if font_file.endswith(".ttf"):
                        import shutil

                        shutil.copy2(
                            os.path.join(source_font_dir, font_file),
                            os.path.join(font_dir, font_file),
                        )

            tex_file = os.path.join(temp_dir, "invoice.tex")
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(self.layout)

            try:
                subprocess.run(
                    ["xelatex", "-interaction=nonstopmode", "invoice.tex"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                )

                subprocess.run(
                    ["xelatex", "-interaction=nonstopmode", "invoice.tex"],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                )

                pdf_file = os.path.join(temp_dir, "invoice.pdf")

                if os.path.exists(pdf_file):
                    with open(pdf_file, "rb") as f:
                        return f.read()
                return None
            except Exception as e:
                print(f"Error compiling LaTeX: {e}")
                return None
