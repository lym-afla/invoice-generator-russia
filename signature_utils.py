#!/usr/bin/env python3
"""
Digital signature utilities for Invoice Generator
Supports both image signatures and digital certificates
"""

import os
from pathlib import Path
from PIL import Image
import base64
from io import BytesIO


class SignatureManager:
    def __init__(self, signatures_dir="signatures"):
        """
        Initialize signature manager
        
        Args:
            signatures_dir (str): Directory containing signature files
        """
        self.signatures_dir = Path(signatures_dir)
        self.signatures_dir.mkdir(exist_ok=True)
    
    def load_signature_image(self, signature_file):
        """
        Load signature image and convert to base64 for embedding
        
        Args:
            signature_file (str): Path to signature image file
            
        Returns:
            str: Base64 encoded image data URL
        """
        signature_path = self.signatures_dir / signature_file
        
        if not signature_path.exists():
            print(f"Warning: Signature file not found: {signature_path}")
            return None
        
        try:
            with Image.open(signature_path) as img:
                # Ensure signature has transparent background
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Resize if too large (max width 200px)
                if img.width > 200:
                    ratio = 200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((200, new_height), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                return f"data:image/png;base64,{img_base64}"
                
        except Exception as e:
            print(f"Error loading signature: {e}")
            return None
    
    def create_signature_placeholder(self, width=200, height=50):
        """
        Create a placeholder signature image
        
        Args:
            width (int): Width in pixels
            height (int): Height in pixels
            
        Returns:
            str: Base64 encoded placeholder image
        """
        try:
            # Create transparent image
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            print(f"Error creating placeholder: {e}")
            return None
    
    def get_available_signatures(self):
        """
        Get list of available signature files
        
        Returns:
            list: List of signature filenames
        """
        signature_files = []
        
        for file_path in self.signatures_dir.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                signature_files.append(file_path.name)
        
        return signature_files
    
    def setup_sample_signatures(self):
        """
        Create sample signature files for testing
        """
        # Create sample director signature
        director_sig = Image.new('RGBA', (150, 40), (255, 255, 255, 0))
        director_path = self.signatures_dir / "director_signature.png"
        director_sig.save(director_path)
        
        # Create sample accountant signature
        accountant_sig = Image.new('RGBA', (150, 40), (255, 255, 255, 0))
        accountant_path = self.signatures_dir / "accountant_signature.png"
        accountant_sig.save(accountant_path)
        
        print(f"Sample signature files created in {self.signatures_dir}")
        print("Replace these with actual signature images:")
        print(f"- {director_path}")
        print(f"- {accountant_path}")


def add_signature_to_invoice_data(invoice_data, signature_manager, director_sig=None, accountant_sig=None):
    """
    Add signature data to invoice data structure
    
    Args:
        invoice_data (dict): Invoice data
        signature_manager (SignatureManager): Signature manager instance
        director_sig (str, optional): Director signature filename
        accountant_sig (str, optional): Accountant signature filename
        
    Returns:
        dict: Updated invoice data with signatures
    """
    signatures = {}
    
    if director_sig:
        signatures['director'] = signature_manager.load_signature_image(director_sig)
    
    if accountant_sig:
        signatures['accountant'] = signature_manager.load_signature_image(accountant_sig)
    
    # Add to invoice data
    invoice_data['signatures'] = signatures
    return invoice_data


if __name__ == "__main__":
    # Example usage
    sig_manager = SignatureManager()
    
    # Setup sample signatures
    sig_manager.setup_sample_signatures()
    
    # List available signatures
    available = sig_manager.get_available_signatures()
    print(f"Available signatures: {available}")
    
    # Test loading
    if available:
        test_sig = sig_manager.load_signature_image(available[0])
        if test_sig:
            print("✓ Signature loading works")
        else:
            print("✗ Signature loading failed")
