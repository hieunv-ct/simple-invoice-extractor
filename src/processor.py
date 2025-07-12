import os
import base64
import json
from io import BytesIO
from PIL import Image
import pdfplumber
from openai import OpenAI
from .prompts import VIETNAMESE_INVOICE_PROCESSOR_PROMPT
from dotenv import load_dotenv

load_dotenv()

class InvoiceProcessor:
    def __init__(self):
        self.client = self._initialize_openai_client()
    
    def _initialize_openai_client(self):
        """Initialize OpenAI client with API key"""
        base_url = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("OpenAI API key not found. Please set OPENAI_API_KEY in your environment or .env file.")
            return None
        return OpenAI(api_key=api_key, base_url=base_url)

    def is_configured(self):
        """Check if the processor is properly configured"""
        return self.client is not None
    
    def process_invoice(self, uploaded_file):
        """
        Main method to process an invoice file and extract structured data
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            dict: Extracted invoice data or None if failed
        """
        # Reset file pointer
        uploaded_file.seek(0)
        file_content = uploaded_file.read()
        file_type = uploaded_file.type
        
        try:
            if file_type.startswith('image/'):
                return self._process_image(file_content, file_type)
            elif file_type == 'application/pdf':
                return self._process_pdf(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            print(f"Error processing invoice: {e}")
            return None
    
    def _process_image(self, image_content, file_type):
        """Process image files using GPT-4 Vision"""
        try:
            # Convert image to supported format if needed
            processed_image, mime_type = self._convert_image_format(image_content, file_type)
            
            # Encode to base64
            base64_image = base64.b64encode(processed_image).decode('utf-8')
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": VIETNAMESE_INVOICE_PROCESSOR_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all information from this Vietnamese invoice image. Return only valid JSON:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            return self._parse_ai_response(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def _process_pdf(self, pdf_content):
        """Process PDF files by extracting text first"""
        try:
            # Extract text from PDF
            text_content = self._extract_pdf_text(pdf_content)
            
            if not text_content.strip():
                return None
            
            # Process with GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": VIETNAMESE_INVOICE_PROCESSOR_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"Extract information from this Vietnamese invoice text. Return only valid JSON:\n\n{text_content}"
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            return self._parse_ai_response(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return None
    
    def _convert_image_format(self, image_bytes, original_type):
        """Convert image to supported format (PNG/JPEG)"""
        try:
            image = Image.open(BytesIO(image_bytes))
            
            # Convert RGBA to RGB for JPEG compatibility
            if image.mode in ('RGBA', 'LA', 'P'):
                if original_type.lower() in ['jpg', 'jpeg']:
                    image = image.convert('RGB')
            
            # Save to BytesIO
            output_buffer = BytesIO()
            
            if original_type.lower() in ['jpg', 'jpeg']:
                image.save(output_buffer, format='JPEG', quality=95)
                return output_buffer.getvalue(), 'image/jpeg'
            else:
                image.save(output_buffer, format='PNG')
                return output_buffer.getvalue(), 'image/png'
                
        except Exception as e:
            print(f"Error converting image: {e}")
            return None, None
    
    def _extract_pdf_text(self, pdf_content):
        """Extract text from PDF using pdfplumber"""
        try:
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def _parse_ai_response(self, response_content):
        """Parse and clean AI response to extract JSON"""
        try:
            # Remove markdown formatting
            content = response_content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            content = content.strip()
            
            # Parse JSON
            parsed_data = json.loads(content)
            
            if not isinstance(parsed_data, dict):
                raise ValueError("Response is not a valid JSON object")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response_content}")
            return None
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return None