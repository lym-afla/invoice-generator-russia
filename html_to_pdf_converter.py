#!/usr/bin/env python3
"""
HTML to PDF converter using alternative methods for Windows
"""

import os
import subprocess
import tempfile
from pathlib import Path


class HTMLToPDFConverter:
    """Convert HTML to PDF using various methods"""
    
    def __init__(self):
        self.available_methods = self._check_available_methods()
    
    def _check_available_methods(self):
        """Check which conversion methods are available"""
        methods = []
        
        # Check for wkhtmltopdf (standalone executable)
        try:
            subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, check=True)
            methods.append('wkhtmltopdf')
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Chrome/Chromium headless (if available)
        chrome_paths = [
            'chrome',
            'chromium',
            'google-chrome',
            'google-chrome-stable',
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ]
        
        for chrome_path in chrome_paths:
            try:
                result = subprocess.run([chrome_path, '--version'], capture_output=True, check=True)
                if b'Google Chrome' in result.stdout or b'Chromium' in result.stdout:
                    methods.append(('chrome', chrome_path))
                    break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        return methods
    
    def convert_html_to_pdf(self, html_content, output_path):
        """
        Convert HTML content to PDF
        
        Args:
            html_content (str): HTML content
            output_path (str): Output PDF path
            
        Returns:
            bool: Success status
        """
        if not self.available_methods:
            print("❌ No PDF conversion methods available!")
            print("💡 Options:")
            print("   1. Download wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
            print("   2. Install Google Chrome")
            print("   3. Use the generated HTML file and print to PDF manually")
            return False
        
        # Try methods in order of preference
        for method in self.available_methods:
            try:
                if method == 'wkhtmltopdf':
                    return self._convert_with_wkhtmltopdf(html_content, output_path)
                elif isinstance(method, tuple) and method[0] == 'chrome':
                    return self._convert_with_chrome(html_content, output_path, method[1])
            except Exception as e:
                print(f"⚠️  Method {method} failed: {e}")
                continue
        
        print("❌ All PDF conversion methods failed")
        return False
    
    def _convert_with_wkhtmltopdf(self, html_content, output_path):
        """Convert using wkhtmltopdf"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name
        
        try:
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '0.75in',
                '--margin-right', '0.75in',
                '--margin-bottom', '0.75in',
                '--margin-left', '0.75in',
                '--encoding', 'UTF-8',
                '--disable-smart-shrinking',
                temp_html_path,
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, check=True)
            print(f"✅ PDF created with wkhtmltopdf: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ wkhtmltopdf error: {e}")
            return False
        finally:
            os.unlink(temp_html_path)
    
    def _convert_with_chrome(self, html_content, output_path, chrome_path):
        """Convert using Chrome/Chromium headless"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name
        
        try:
            file_url = f'file:///{temp_html_path.replace(os.sep, "/")}'
            
            cmd = [
                chrome_path,
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--print-to-pdf=' + output_path,
                '--print-to-pdf-no-header',
                file_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, check=True)
            print(f"✅ PDF created with Chrome: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Chrome headless error: {e}")
            return False
        finally:
            os.unlink(temp_html_path)
    
    def get_status(self):
        """Get status of available conversion methods"""
        if not self.available_methods:
            return "❌ No PDF conversion methods available"
        
        status = "✅ Available PDF conversion methods:\n"
        for method in self.available_methods:
            if isinstance(method, tuple):
                status += f"   - {method[0]} ({method[1]})\n"
            else:
                status += f"   - {method}\n"
        
        return status.strip()


def main():
    """Test the converter"""
    converter = HTMLToPDFConverter()
    print(converter.get_status())
    
    # Test with a simple HTML
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test</title>
    </head>
    <body>
        <h1>Тест PDF генерации</h1>
        <p>Проверка русского текста</p>
    </body>
    </html>
    """
    
    if converter.available_methods:
        print("\n🔄 Testing PDF conversion...")
        success = converter.convert_html_to_pdf(test_html, "test_output.pdf")
        if success:
            print("✅ Test successful!")
        else:
            print("❌ Test failed!")


if __name__ == "__main__":
    main()
