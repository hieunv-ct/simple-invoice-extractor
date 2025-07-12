import streamlit as st
import os
from src.processor import InvoiceProcessor
from src.utils import display_extracted_data, convert_to_downloadable_formats

# Configuration
st.set_page_config(
    page_title="Simple Vietnamese Invoice Extractor",
    page_icon="🧾",
    layout="wide"
)

def main():
    st.title("🧾 Simple Vietnamese Invoice Data Extractor")
    st.markdown("** Demo: AI-Powered Invoice Processing**")
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About This Demo")
        st.markdown("""
        This is a simple demonstration of how to extract structured data 
        from Vietnamese invoices using OpenAI's GPT-4 Vision API.
        
        **Features:**
        - Image & PDF processing
        - Structured data extraction
        - JSON/CSV export
        - Vietnamese text handling
        """)
        
        st.header("🔧 Requirements")
        st.markdown("""
        - OpenAI API Key
        - Internet connection
        - Vietnamese invoice files
        """)
    
    # Main content
    processor = InvoiceProcessor()
    
    if not processor.is_configured():
        st.error("⚠️ OpenAI API not configured. Please check your environment variables.")
        st.info("Set OPENAI_API_KEY in your environment or .env file")
        return
    
    # File upload section
    st.header("📤 Upload Vietnamese Invoice")
    uploaded_file = st.file_uploader(
        "Choose an invoice file",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        help="Supported: PDF, PNG, JPG, JPEG"
    )
    
    if uploaded_file:
        # Display file info
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info(f"📄 **File:** {uploaded_file.name}")
            st.info(f"📊 **Size:** {len(uploaded_file.getvalue()) / 1024:.1f} KB")
            st.info(f"📝 **Type:** {uploaded_file.type}")
        
        with col2:
            # Show preview for images
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="Invoice Preview", use_container_width=True)
            else:
                st.info("📄 PDF uploaded - Preview not available")
        
        # Extract button
        if st.button("🚀 Extract Data with AI", type="primary", use_container_width=True):
            with st.spinner("🧠 Processing invoice... This may take 30-60 seconds"):
                try:
                    # Process the invoice
                    extracted_data = processor.process_invoice(uploaded_file)
                    
                    if extracted_data:
                        st.success("✅ Data extracted successfully!")
                        
                        # Display results
                        display_extracted_data(extracted_data)
                        
                        # Download options
                        st.header("💾 Download Extracted Data")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            json_data, csv_data = convert_to_downloadable_formats(extracted_data)
                            st.download_button(
                                "📄 Download JSON",
                                json_data,
                                f"{uploaded_file.name}_extracted.json",
                                "application/json"
                            )
                        
                        with col2:
                            st.download_button(
                                "📊 Download CSV",
                                csv_data,
                                f"{uploaded_file.name}_extracted.csv",
                                "text/csv"
                            )
                    else:
                        st.error("❌ Could not extract data from the invoice")
                        
                except Exception as e:
                    st.error(f"❌ Error processing invoice: {str(e)}")

if __name__ == "__main__":
    main()