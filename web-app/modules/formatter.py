import markdown
from xhtml2pdf import pisa 
import tempfile
import copy

def convert_pdf(text):
    # Create a html rendering using the markdown library
    text_html = markdown.markdown(text)

    # convert HTML to PDF
    temp_file = tempfile.TemporaryFile()
    pisa_status = pisa.CreatePDF(text_html, dest=temp_file)  

    # Go back to the start of the file, and return read bytes
    temp_file.seek(0)
    return temp_file.read()