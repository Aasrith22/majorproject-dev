"""
Preprocessing Service
Handles multimodal input conversion and validation
"""

from typing import Optional, Dict, Any
from loguru import logger
import base64
import io


class PreprocessingService:
    """Service for preprocessing multimodal inputs"""
    
    async def process_input(
        self,
        input_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process input based on modality type
        
        Args:
            input_type: Type of input (text, voice, diagram)
            content: Raw input content (text or base64 encoded)
            metadata: Additional metadata
            
        Returns:
            Processed text content
        """
        
        if input_type == "text":
            return await self._process_text(content)
        elif input_type == "voice":
            return await self._process_voice(content, metadata)
        elif input_type == "diagram":
            return await self._process_diagram(content, metadata)
        else:
            logger.warning(f"Unknown input type: {input_type}, treating as text")
            return await self._process_text(content)
    
    async def _process_text(self, content: str) -> str:
        """Process text input"""
        # Clean and normalize text
        processed = content.strip()
        
        # Remove excessive whitespace
        processed = " ".join(processed.split())
        
        # Validate length
        if len(processed) > 10000:
            processed = processed[:10000]
            logger.warning("Text input truncated to 10000 characters")
        
        return processed
    
    async def _process_voice(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process voice input - convert to text
        
        Args:
            content: Base64 encoded audio data
            metadata: Audio metadata (format, sample_rate, etc.)
            
        Returns:
            Transcribed text
        """
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(content)
            
            # Get audio format from metadata
            audio_format = metadata.get("format", "wav") if metadata else "wav"
            
            # Use speech recognition
            # Note: In production, you might want to use a cloud service
            # like Google Speech-to-Text or OpenAI Whisper
            transcribed_text = await self._transcribe_audio(audio_data, audio_format)
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            # Return placeholder if transcription fails
            return "[Voice input - transcription failed]"
    
    async def _transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: str
    ) -> str:
        """
        Transcribe audio to text
        
        This is a placeholder implementation.
        In production, integrate with:
        - OpenAI Whisper API
        - Google Speech-to-Text
        - Azure Speech Services
        """
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Convert bytes to AudioFile
            audio_file = io.BytesIO(audio_data)
            
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
            
            # Use Google Speech Recognition (free tier)
            # Replace with Whisper or other service for production
            text = recognizer.recognize_google(audio)
            
            return text
            
        except ImportError:
            logger.warning("speech_recognition not installed, returning placeholder")
            return "[Voice transcription requires speech_recognition package]"
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return "[Transcription failed]"
    
    async def _process_diagram(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process diagram/image input - extract text using OCR
        
        Args:
            content: Base64 encoded image data
            metadata: Image metadata
            
        Returns:
            Extracted text description
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(content)
            
            # Extract text using OCR
            extracted_text = await self._extract_text_from_image(image_data)
            
            # If OCR returns minimal text, try image description
            if len(extracted_text.strip()) < 10:
                # Use LLM for image description
                extracted_text = await self._describe_image(image_data, metadata)
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Diagram processing error: {e}")
            return "[Diagram input - extraction failed]"
    
    async def _extract_text_from_image(self, image_data: bytes) -> str:
        """
        Extract text from image using OCR
        
        This is a placeholder implementation.
        In production, integrate with:
        - Tesseract OCR
        - Google Vision API
        - Azure Computer Vision
        """
        try:
            from PIL import Image
            import pytesseract
            
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_data))
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            return text.strip()
            
        except ImportError:
            logger.warning("PIL or pytesseract not installed")
            return "[OCR requires PIL and pytesseract packages]"
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""
    
    async def _describe_image(
        self,
        image_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate description of image using LLM
        
        This would use GPT-4 Vision or Gemini Pro Vision
        Placeholder implementation for now
        """
        # In production, send image to vision-capable LLM
        # Example with OpenAI:
        # response = openai.chat.completions.create(
        #     model="gpt-4-vision-preview",
        #     messages=[{
        #         "role": "user",
        #         "content": [
        #             {"type": "text", "text": "Describe this educational diagram"},
        #             {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(image_data).decode()}"}}
        #         ]
        #     }]
        # )
        
        return "[Image description - requires vision-capable LLM integration]"
    
    def validate_input(
        self,
        input_type: str,
        content: str,
        max_size_mb: float = 5.0
    ) -> tuple[bool, str]:
        """
        Validate input before processing
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content:
            return False, "Empty content"
        
        if input_type not in ["text", "voice", "diagram"]:
            return False, f"Invalid input type: {input_type}"
        
        # Check size for binary content
        if input_type in ["voice", "diagram"]:
            try:
                decoded = base64.b64decode(content)
                size_mb = len(decoded) / (1024 * 1024)
                if size_mb > max_size_mb:
                    return False, f"File too large: {size_mb:.2f}MB (max {max_size_mb}MB)"
            except Exception:
                return False, "Invalid base64 encoding"
        
        # Check text length
        if input_type == "text" and len(content) > 50000:
            return False, "Text too long (max 50000 characters)"
        
        return True, ""
