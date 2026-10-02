from io import BytesIO
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def summary_rows(company,tender,result):
    return [("Company",company.get("company_name","")),("Tender",tender.get("title","")),("Agency",tender.get("agency","")),("Deadline",tender.get("deadline","")),("Bid readiness",f"{result['eligibility']['readiness']}%"),("Opportunity fit",f"{result['eligibility']['fit']}%"),("Risk",result["risk"]["risk_level"]),("Open compliance items",result["compliance"]["open_items"])]

def build_docx(company,tender,result):
    d=Document(); p=d.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("TenderPulse AI\nBid Intelligence Report"); r.bold=True;r.font.size=Pt(22)
    d.add_paragraph("Evidence-alignment decision support • Human verification required").alignment=WD_ALIGN_PARAGRAPH.CENTER
    t=d.add_table(rows=0,cols=2);t.style="Light Shading Accent 1"
    for k,v in summary_rows(company,tender,result): c=t.add_row().cells;c[0].text=k;c[1].text=str(v)
    d.add_heading("Compliance Matrix",1);m=d.add_table(rows=1,cols=4);m.style="Table Grid"
    for i,h in enumerate(["Requirement","Status","Evidence","Action"]):m.rows[0].cells[i].text=h
    for x in result["compliance"]["matrix"]:
        c=m.add_row().cells
        for i,k in enumerate(["requirement","status","evidence","action"]):c[i].text=str(x.get(k,""))
    d.add_heading("Risk Review",1)
    for x in result["risk"]["risks"] or ["No risks detected by simplified rule set."]:d.add_paragraph(str(x),style="List Bullet")
    d.add_heading("AI Analysis",1);d.add_paragraph(result["document"]["ai"].get("summary",""))
    d.add_paragraph("This report does not predict contract awards. Verify all requirements against official documents.")
    b=BytesIO();d.save(b);return b.getvalue()

def build_pdf(company,tender,result):
    b=BytesIO();styles=getSampleStyleSheet();story=[Paragraph("TenderPulse AI — Bid Intelligence Report",styles["Title"]),Spacer(1,12)]
    data=[["Field","Value"]]+[[k,str(v)] for k,v in summary_rows(company,tender,result)]
    story.append(Table(data,colWidths=[130,380],style=[("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey)]))
    story += [Spacer(1,14),Paragraph("Compliance Matrix",styles["Heading2"])]
    cm=[["Requirement","Status","Evidence"]]+[[str(x["requirement"]),str(x["status"]),str(x["evidence"])] for x in result["compliance"]["matrix"]]
    story.append(Table(cm,colWidths=[170,60,280],repeatRows=1,style=[("GRID",(0,0),(-1,-1),.3,colors.grey),("FONTSIZE",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story += [Spacer(1,12),Paragraph("This report is decision support, not an award prediction. Human verification is required.",styles["Italic"])]
    SimpleDocTemplate(b,pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36).build(story);return b.getvalue()
