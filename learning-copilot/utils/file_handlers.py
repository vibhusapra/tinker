import os
import json
import PyPDF2
from typing import Optional, Dict, Any
import tempfile
import markdown
from bs4 import BeautifulSoup

class FileHandler:
    def __init__(self):
        self.supported_formats = {
            '.txt': self.read_text,
            '.md': self.read_markdown,
            '.pdf': self.read_pdf,
            '.json': self.read_json,
            '.py': self.read_text,
            '.js': self.read_text,
            '.html': self.read_html,
            '.csv': self.read_text
        }
    
    def process_uploaded_file(self, uploaded_file) -> Dict[str, Any]:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension not in self.supported_formats:
            return {
                "success": False,
                "error": f"Unsupported file format: {file_extension}",
                "supported": list(self.supported_formats.keys())
            }
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_file_path = tmp_file.name
            
            handler = self.supported_formats[file_extension]
            content = handler(tmp_file_path)
            
            os.unlink(tmp_file_path)
            
            return {
                "success": True,
                "filename": uploaded_file.name,
                "format": file_extension,
                "content": content,
                "size": len(content)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing file: {str(e)}"
            }
    
    def read_text(self, filepath: str) -> str:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    
    def read_markdown(self, filepath: str) -> str:
        content = self.read_text(filepath)
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()
    
    def read_pdf(self, filepath: str) -> str:
        content = []
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content.append(page.extract_text())
        return '\n'.join(content)
    
    def read_json(self, filepath: str) -> str:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return json.dumps(data, indent=2)
    
    def read_html(self, filepath: str) -> str:
        with open(filepath, 'r', encoding='utf-8') as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
    
    def extract_syllabus_content(self, file_result: Dict) -> str:
        if not file_result["success"]:
            return ""
        
        content = file_result["content"]
        
        structured_content = f"""# Uploaded Syllabus: {file_result['filename']}

## Content
{content}

## Analysis
- File Type: {file_result['format']}
- Content Length: {file_result['size']} characters
"""
        
        return structured_content
    
    def parse_syllabus_structure(self, content: str) -> Dict[str, Any]:
        lines = content.split('\n')
        structure = {
            "topics": [],
            "prerequisites": [],
            "learning_outcomes": [],
            "schedule": [],
            "raw_content": content[:2000]
        }
        
        current_section = None
        
        keywords = {
            "topics": ["topics", "outline", "content", "syllabus", "curriculum"],
            "prerequisites": ["prerequisites", "requirements", "required"],
            "learning_outcomes": ["outcomes", "objectives", "goals", "learning"],
            "schedule": ["schedule", "timeline", "week", "module", "unit"]
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            
            for section, keys in keywords.items():
                if any(key in line_lower for key in keys):
                    current_section = section
                    break
            
            if current_section and line.strip():
                if line.strip() not in structure[current_section]:
                    structure[current_section].append(line.strip())
        
        for section in structure:
            if section != "raw_content":
                structure[section] = structure[section][:20]
        
        return structure