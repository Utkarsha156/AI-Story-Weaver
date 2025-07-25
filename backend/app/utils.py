import os
from fpdf import FPDF
from io import BytesIO

def create_story_pdf(story):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)  

    
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', size=24)
    
   
    title = story.title or "Untitled Story"
    pdf.cell(0, 60, title, ln=True, align='C')

    pdf.set_font("Helvetica", size=14)
    if hasattr(story, 'author'):
        pdf.cell(0, 20, f"By {story.author.username}", ln=True, align='C')
    pdf.cell(0, 20, f"Theme: {story.country_theme}", ln=True, align='C')
    
    
    if hasattr(story, '_pdf_pages'):
        pages_source = story._pdf_pages
        print(f"DEBUG: Using provided PDF pages: {len(pages_source)} pages")
    else:
        pages_source = story.pages
        print(f"DEBUG: Using story.pages: {len(pages_source)} pages")

    
    unique_pages = {}
    for page in pages_source:
        if page.page_no not in unique_pages:
            unique_pages[page.page_no] = page
        else:
            print(f"DEBUG: Found duplicate page {page.page_no}, keeping first one")
    
    
    sorted_pages = sorted(unique_pages.values(), key=lambda x: x.page_no)
    pages_to_process = sorted_pages[:10] 
    
    print(f"DEBUG: PDF Processing Summary:")
    print(f"  - Total pages in story: {len(pages_source)}")
    print(f"  - Unique pages found: {len(unique_pages)}")
    print(f"  - Pages to process in PDF: {len(pages_to_process)}")
    print(f"  - Page numbers: {[p.page_no for p in pages_to_process]}")


    if len(pages_to_process) > 10:
        print(f"WARNING: Attempted to process {len(pages_to_process)} pages, forcing to 10")
        pages_to_process = pages_to_process[:10]

    
    for i, page in enumerate(pages_to_process):
        pdf.add_page() 
        
        print(f"DEBUG: Adding PDF page {i+1} for story page {page.page_no}")
        
       
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, f"Page {page.page_no}", ln=True, align='C')
        pdf.ln(5)  

        current_y = pdf.get_y()  
        
       
        if page.image_url:
            try:
                
                if page.image_url.startswith('/static/'):
                    file_path = page.image_url.lstrip('/')
                else:
                    file_path = page.image_url
                
                if os.path.exists(file_path):
                    
                    image_width = 140  
                    image_height = 70  
                    x_position = (210 - image_width) / 2  

                    pdf.image(file_path, x=x_position, y=current_y, w=image_width, h=image_height)
                    current_y += image_height + 10  
                else:
                    pdf.set_font("Helvetica", 'I', 10)
                    pdf.cell(0, 10, "[Image file not found]", ln=True, align='C')
                    current_y += 15
            except Exception as e:
                print(f"DEBUG: Error loading image {page.image_url}: {e}")
                pdf.set_font("Helvetica", 'I', 10)
                pdf.cell(0, 10, "[Error loading image]", ln=True, align='C')
                current_y += 15

        
        pdf.set_xy(15, current_y) 
        pdf.set_font("Helvetica", '', 12)  
        
        
        clean_text = page.text.replace('\\n', '\n').strip()
       
        try:
            safe_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
        except:
            safe_text = clean_text
        
        
        pdf.multi_cell(180, 6, safe_text, align='L')
        
        print(f"DEBUG: Added PDF page for story page {page.page_no}")

    final_pdf_pages = pdf.page_no()
    expected_pages = len(pages_to_process) + 1 

    print(f"DEBUG: PDF generation complete:")
    print(f"  - Story pages processed: {len(pages_to_process)}")
    print(f"  - Total PDF pages: {final_pdf_pages}")
    print(f"  - Expected PDF pages: {expected_pages}")
    
    
    if final_pdf_pages != expected_pages:
        print(f"WARNING: PDF page count mismatch! Expected {expected_pages}, got {final_pdf_pages}")

    
    try:
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            
            return BytesIO(pdf_output.encode('latin-1'))
        else:
            
            return BytesIO(pdf_output)
    except Exception as e:
        print(f"DEBUG: Error generating PDF: {e}")
        
        return BytesIO(pdf.output(dest='S').encode('latin-1'))