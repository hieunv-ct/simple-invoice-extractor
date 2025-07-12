import streamlit as st
import pandas as pd
import json
from io import StringIO

def display_extracted_data(data):
    """Display extracted invoice data in a formatted way"""
    if not data:
        st.error("No data to display")
        return
    
    st.header("📊 Extracted Invoice Data")
    
    # Company Information
    st.subheader("🏢 Company Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**👤 Seller (Người bán)**")
        company_info = data.get("company_info", {})
        st.write(f"**Name:** {company_info.get('seller_name', 'N/A')}")
        st.write(f"**Tax Code:** {company_info.get('seller_tax_code', 'N/A')}")
        st.write(f"**Address:** {company_info.get('seller_address', 'N/A')}")
    
    with col2:
        st.markdown("**🏪 Buyer (Người mua)**")
        st.write(f"**Name:** {company_info.get('buyer_name', 'N/A')}")
        st.write(f"**Tax Code:** {company_info.get('buyer_tax_code', 'N/A')}")
        st.write(f"**Address:** {company_info.get('buyer_address', 'N/A')}")
    
    # Invoice Details
    st.subheader("🧾 Invoice Details")
    invoice_details = data.get("invoice_details", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Invoice Number", invoice_details.get('invoice_number', 'N/A'))
    with col2:
        st.metric("Date", invoice_details.get('invoice_date', 'N/A'))
    with col3:
        st.metric("Serial", invoice_details.get('serial', 'N/A'))
    with col4:
        st.metric("Form", invoice_details.get('form_number', 'N/A'))
    
    # Financial Summary
    st.subheader("💰 Financial Summary")
    financial_info = data.get("financial_info", {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        amount_before = financial_info.get('total_amount_before_tax', 0)
        st.metric("Amount Before Tax", f"{amount_before:,.0f}" if amount_before else "N/A")
    
    with col2:
        vat_rate = financial_info.get('vat_rate', 0)
        st.metric("VAT Rate", f"{vat_rate}%" if vat_rate else "N/A")
    
    with col3:
        vat_amount = financial_info.get('vat_amount', 0)
        st.metric("VAT Amount", f"{vat_amount:,.0f}" if vat_amount else "N/A")
    
    with col4:
        total_amount = financial_info.get('total_amount_after_tax', 0)
        st.metric("**Total Amount**", f"**{total_amount:,.0f}**" if total_amount else "N/A")
    
    # Items Table
    st.subheader("📋 Invoice Items")
    items = data.get("items", [])
    
    if items and any(item for item in items if item):
        # Clean and prepare items for display
        cleaned_items = []
        for item in items:
            if item and isinstance(item, dict):
                cleaned_item = {k: v for k, v in item.items() if v is not None}
                if cleaned_item:
                    cleaned_items.append(cleaned_item)
        
        if cleaned_items:
            df = pd.DataFrame(cleaned_items)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No valid items found")
    else:
        st.info("No items found in the invoice")
    
    # Raw JSON (expandable)
    with st.expander("🔍 View Raw JSON Data"):
        st.json(data)

def convert_to_downloadable_formats(data):
    """Convert extracted data to downloadable JSON and CSV formats"""
    
    # JSON format
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    
    # CSV format - flatten the data
    csv_data = []
    
    # Add company info
    company_info = data.get("company_info", {})
    invoice_details = data.get("invoice_details", {})
    financial_info = data.get("financial_info", {})
    
    # Create a summary row
    summary_row = {
        "Type": "Invoice Summary",
        "Seller Name": company_info.get("seller_name", ""),
        "Seller Tax Code": company_info.get("seller_tax_code", ""),
        "Buyer Name": company_info.get("buyer_name", ""),
        "Buyer Tax Code": company_info.get("buyer_tax_code", ""),
        "Invoice Number": invoice_details.get("invoice_number", ""),
        "Invoice Date": invoice_details.get("invoice_date", ""),
        "Total Before Tax": financial_info.get("total_amount_before_tax", 0),
        "VAT Rate": financial_info.get("vat_rate", 0),
        "VAT Amount": financial_info.get("vat_amount", 0),
        "Total After Tax": financial_info.get("total_amount_after_tax", 0)
    }
    csv_data.append(summary_row)
    
    # Add items
    items = data.get("items", [])
    for i, item in enumerate(items):
        if item:
            item_row = {
                "Type": f"Item {i+1}",
                "Description": item.get("description", ""),
                "Quantity": item.get("quantity", 0),
                "Unit": item.get("unit", ""),
                "Unit Price": item.get("unit_price", 0),
                "Amount": item.get("amount", 0)
            }
            csv_data.append(item_row)
    
    # Convert to CSV string
    if csv_data:
        df = pd.DataFrame(csv_data)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_str = csv_buffer.getvalue()
    else:
        csv_str = "No data available"
    
    return json_str, csv_str

def format_currency(amount, currency="VND"):
    """Format currency with proper thousand separators"""
    if amount is None or amount == 0:
        return "N/A"
    return f"{amount:,.0f} {currency}"

def validate_extracted_data(data):
    """Validate the structure of extracted data"""
    required_keys = ["company_info", "invoice_details", "financial_info", "items"]
    
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"
    
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        return False, f"Missing required keys: {missing_keys}"
    
    return True, "Data structure is valid"