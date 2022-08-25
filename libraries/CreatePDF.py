
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def gen(sourceFile, outputfile, data):
    existing_pdf = PdfFileReader(open(sourceFile, "rb"))
    output = PdfFileWriter()

    for i in range(existing_pdf.numPages):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont('Helvetica', 12)

        if i in data:
            for j in data[i]:
                can.drawString(j[0], j[1], j[2])
        
        can.save()
        packet.seek(0)
        new_pdf = PdfFileReader(packet)

        page = existing_pdf.getPage(i)
        page.mergePage(new_pdf.getPage(0))# index out of range if not set to 0.
        output.addPage(page)    

    # Finally, write "output" to a real file
    outputStream = open(outputfile, "wb")
    output.write(outputStream)
    outputStream.close()
    return outputfile

def modify():
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(10, 100, "Hello world")
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(1)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open("files/esign/contract_template.pdf", "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = open("files/esign/contract_template_final.pdf", "wb")
    output.write(outputStream)
    outputStream.close()

def multi():
    inputpdf = PdfFileReader(open("files/esign/contract_template.pdf", "rb"))

    packet = io.BytesIO()
    # Create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Helvetica', 13)
    can.drawString(5, 730, "hello")
    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # Read your existing PDF
    existing_pdf = PdfFileReader(open("files/esign/contract_template.pdf", "rb"))
    output = PdfFileWriter()
    # Add the "watermark" (which is the new pdf) on the existing page

    for i in range(existing_pdf.numPages):
        can.drawString(5, 730, "haha")
        page = existing_pdf.getPage(i)
        page.mergePage(new_pdf.getPage(0))# index out of range if not set to 0.
        output.addPage(page)    

    # Finally, write "output" to a real file
    outputStream = open("files/esign/contract_template_tung.pdf", "wb")
    output.write(outputStream)
    outputStream.close()
