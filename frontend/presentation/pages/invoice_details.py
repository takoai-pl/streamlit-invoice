# Copyright (c) TaKo AI Sp. z o.o.
import requests.exceptions
import streamlit as st

from frontend.domain.entities.invoice_entity import InvoiceEntity
from frontend.presentation.handler import handler
from frontend.utils.const import currencies
from frontend.utils.language import i18n as _


def _on_change_product(key: str, attribute: str, product_index: int) -> None:
    current_value = st.session_state[key]
    try:
        st.session_state.invoice.edit_product(
            product_index, **{attribute: current_value}
        )
    except requests.exceptions.HTTPError as e:
        st.error(str(e))
    except Exception as e:
        st.warning(str(e))


def _on_change_details(key: str) -> None:
    current_value = st.session_state[key]
    try:
        if key == "invoiceNo":
            InvoiceEntity.validate_invoice_no(current_value)
        elif key == "issuedAt" or key == "dueTo":
            InvoiceEntity.validate_dates(current_value)

        st.session_state.invoice.edit_field(key, current_value)
    except requests.exceptions.HTTPError as e:
        st.error(str(e))
    except Exception as e:
        st.warning(str(e))


def _on_change_business(key: str) -> None:
    current_value = st.session_state[key]
    if current_value == "" or current_value is None:
        return
    try:
        business_entity = handler.get_business_details(current_value)
        st.session_state.invoice.edit_business(**business_entity.__dict__)
    except requests.exceptions.HTTPError as e:
        st.error(str(e))
    except Exception as e:
        st.warning(str(e))


def _on_change_client(key: str) -> None:
    current_value = st.session_state[key]
    if current_value == "" or current_value is None:
        return
    try:
        client_entity = handler.get_client_details(current_value)
        st.session_state.invoice.edit_client(**client_entity.__dict__)
    except requests.exceptions.HTTPError as e:
        st.error(str(e))
    except Exception as e:
        st.warning(str(e))


def build_invoice_fields() -> None:
    client, business = st.columns(2)

    key_client = "client"

    with client:
        st.subheader(_("shared_details") + " " + _("client_details"))
        try:
            st.selectbox(
                _("client"),
                handler.get_all_clients_names(),
                index=None,
                placeholder=_("select_client"),
                on_change=_on_change_client,
                key=key_client,
                args=(key_client,),
            )
        except requests.exceptions.HTTPError as e:
            st.error(str(e))
            return

    key_business = "business"

    with business:
        st.subheader(_("shared_details") + " " + _("business_details"))
        try:
            st.selectbox(
                _("business"),
                handler.get_all_businesses_names(),
                index=None,
                placeholder=_("select_business"),
                on_change=_on_change_business,
                key=key_business,
                args=(key_business,),
            )
        except requests.exceptions.HTTPError as e:
            st.error(str(e))
            return

    st.subheader(_("invoice_details"))

    column1, column2, column3 = st.columns([1, 1, 2])

    with column1:
        key_invoice_no = "invoiceNo"
        st.text_input(
            _("invoice_no"),
            value=st.session_state.invoice.invoiceNo,
            key=key_invoice_no,
            on_change=_on_change_details,
            args=(key_invoice_no,),
        )
    with column2:
        key_currency = "currency"
        currency = currencies.index(st.session_state.invoice.currency)
        st.selectbox(
            _("currency"),
            currencies,
            key=key_currency,
            index=currency if currency != "" else None,
            placeholder=_("select_currency"),
            on_change=_on_change_details,
            args=(key_currency,),
        )

    with column3:
        key_vat_percent = "vatPercent"

        vat_percent_options = [0, 4, 5, 7, 8, 9, 21, 23]

        st.select_slider(
            _("vat_percent"),
            vat_percent_options,
            value=st.session_state.invoice.vatPercent,
            key=key_vat_percent,
            on_change=_on_change_details,
            args=(key_vat_percent,),
        )

    key_issued_at = "issuedAt"
    key_due_to = "dueTo"
    c1, c2 = st.columns([1, 1])

    with c1:
        st.date_input(
            _("issued_date"),
            value=st.session_state.invoice.issuedAt,
            key=key_issued_at,
            format="DD/MM/YYYY",
            on_change=_on_change_details,
            args=(key_issued_at,),
        )

        st.date_input(
            _("due_date"),
            value=st.session_state[key_issued_at],
            key=key_due_to,
            format="DD/MM/YYYY",
            on_change=_on_change_details,
            args=(key_due_to,),
            min_value=st.session_state[key_issued_at],
        )

    with c2:
        key_note = "note"
        st.text_area(
            _("note"),
            value=st.session_state.invoice.note,
            key=key_note,
            height=122,
            on_change=_on_change_details,
            args=(key_note,),
        )

    st.subheader(_("products"))

    product_display_values = [_("description"), _("quantity"), _("unit"), _("price")]

    unit_options = [_("piece"), _("hour"), _("day"), "kg", "m2", "m3", "m", "km", ""]

    for i, product in enumerate(st.session_state.invoice.products):
        c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
        with c1:
            key_description = f"product_{i}_description"
            label = product_display_values[0] if i <= 1 else "hidden_label"
            st.text_input(
                label,
                label_visibility="collapsed" if i > 0 else "visible",
                value=product.description,
                key=key_description,
                on_change=_on_change_product,
                args=(key_description, "description", i),
            )
        with c2:
            key_quantity = f"product_{i}_quantity"
            label = "_" if i > 1 else product_display_values[1]
            st.number_input(
                label,
                label_visibility="collapsed" if i > 0 else "visible",
                value=product.quantity,
                key=key_quantity,
                on_change=_on_change_product,
                args=(key_quantity, "quantity", i),
            )
        with c3:
            key_unit = f"product_{i}_unit"
            label = "_" if i > 1 else product_display_values[2]
            unit = unit_options.index(product.unit)
            st.selectbox(
                label,
                unit_options,
                label_visibility="collapsed" if i > 0 else "visible",
                key=key_unit,
                index=unit if unit != "" else None,
                on_change=_on_change_product,
                args=(key_unit, "unit", i),
            )
        with c4:
            key_price = f"product_{i}_price"
            label = "_" if i > 1 else product_display_values[3]
            st.number_input(
                label,
                label_visibility="collapsed" if i > 0 else "visible",
                value=product.price,
                key=key_price,
                on_change=_on_change_product,
                args=(key_price, "price", i),
            )
        with c5:
            if i == 0:
                st.container(height=13, border=False)

            st.button(
                _("x"),
                key=f"delete_{i}",
                use_container_width=True,
                type="primary",
                on_click=st.session_state.invoice.delete_product,
                args=(i,),
            )

    c1, c2, c3, c4 = st.columns([6.3, 2.1, 2, 1])

    with c1:
        st.button(
            _("add_product"),
            on_click=st.session_state.invoice.add_product,
            args=("", 0, "", 0.0),
        )

    if len(st.session_state.invoice.products) > 0:
        with c2:
            st.text(f'{_("subtotal")}:')
            st.text(f'{_("vat_value")}:')
            st.text(f'{_("total")}:')

        with c3:
            st.text(f"{st.session_state.invoice.subtotal}")
            st.text(f"{st.session_state.invoice.vat_value}")
            st.text(
                f"{st.session_state.invoice.subtotal + st.session_state.invoice.vat_value}"
            )
