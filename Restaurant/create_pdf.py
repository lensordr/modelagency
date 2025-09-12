from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def create_implementation_pdf():
    # Create PDF
    doc = SimpleDocTemplate("Restaurant_SaaS_Implementation_Plan.pdf", pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12)
    
    # Title
    story.append(Paragraph("Restaurant Management System - SaaS Implementation Plan", title_style))
    story.append(Spacer(1, 20))
    
    # Phase 1: Production Ready
    story.append(Paragraph("Phase 1: Production Ready (1-2 Days)", heading_style))
    
    phase1_data = [
        ['Task', 'Time Required', 'Priority', 'Notes'],
        ['Environment Variables Setup', '2 hours', 'High', 'DATABASE_URL, STRIPE_KEY, SECRET_KEY'],
        ['PostgreSQL Migration', '2 hours', 'High', 'Replace SQLite with PostgreSQL'],
        ['SSL Certificate Setup', '30 minutes', 'High', "Let's Encrypt HTTPS"],
        ['Authentication System', '3 hours', 'High', 'Replace hardcoded passwords'],
        ['Input Validation', '2 hours', 'Medium', 'Sanitize all form inputs'],
        ['Error Handling & Logging', '1 hour', 'Medium', 'Comprehensive logging system'],
        ['Database Indexing', '1 hour', 'Low', 'Optimize query performance']
    ]
    
    table1 = Table(phase1_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 2.2*inch])
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(table1)
    story.append(Spacer(1, 20))
    
    # Phase 2: Customization
    story.append(Paragraph("Phase 2: Customization Features (1 Day)", heading_style))
    
    phase2_data = [
        ['Task', 'Time Required', 'Priority', 'Notes'],
        ['Logo Upload System', '2 hours', 'Medium', 'Restaurant branding capabilities'],
        ['Color Scheme Customization', '2 hours', 'Low', 'CSS theming system'],
        ['Restaurant Info Setup', '1 hour', 'Medium', 'Name, contact, business hours'],
        ['Dynamic Table Configuration', '2 hours', 'High', 'Admin sets table count'],
        ['QR Code Generation', '2 hours', 'High', 'Printable QR codes for tables'],
    ]
    
    table2 = Table(phase2_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 2.2*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(table2)
    story.append(Spacer(1, 20))
    
    # Phase 3: Subscription Management
    story.append(Paragraph("Phase 3: Subscription Management (2-3 Days)", heading_style))
    
    phase3_data = [
        ['Task', 'Time Required', 'Priority', 'Notes'],
        ['Stripe Integration', '4 hours', 'High', 'Payment processing system'],
        ['Billing System', '2 hours', 'High', 'Monthly recurring billing'],
        ['Trial Period Implementation', '2 hours', 'Medium', '14-day free trial'],
        ['Multi-tenant Architecture', '6 hours', 'High', 'restaurant_id data isolation'],
        ['Subdomain System', '2 hours', 'Medium', 'Dynamic subdomain routing'],
        ['Admin Panel', '4 hours', 'Medium', 'Restaurant management interface'],
    ]
    
    table3 = Table(phase3_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 2.2*inch])
    table3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(table3)
    story.append(Spacer(1, 20))
    
    # Deployment & Launch
    story.append(Paragraph("Deployment & Launch", heading_style))
    
    deployment_data = [
        ['Task', 'Time Required', 'Priority', 'Notes'],
        ['Cloud Server Setup', '2 hours', 'High', 'DigitalOcean/AWS deployment'],
        ['Domain & SSL Configuration', '1 hour', 'High', 'HTTPS setup'],
        ['Monitoring Setup', '1 hour', 'Medium', 'Performance monitoring'],
        ['Documentation Creation', '2 hours', 'High', 'User guides and tutorials'],
        ['Customer Onboarding Flow', '2 hours', 'High', 'Registration process'],
        ['QR Code Package Generation', '1 hour', 'High', 'Printable materials'],
    ]
    
    table4 = Table(deployment_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 2.2*inch])
    table4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(table4)
    story.append(Spacer(1, 20))
    
    # Pricing Strategy
    story.append(Paragraph("Pricing Strategy", heading_style))
    
    pricing_data = [
        ['Plan', 'Price/Month', 'Tables', 'Features'],
        ['Basic', '$29', 'Up to 20', 'Basic analytics, Email support'],
        ['Pro', '$49', 'Up to 50', 'Advanced analytics, Priority support, Custom branding'],
        ['Enterprise', '$99', 'Unlimited', 'Custom features, Phone support, API access'],
    ]
    
    table5 = Table(pricing_data, colWidths=[1.5*inch, 1*inch, 1*inch, 3*inch])
    table5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(table5)
    story.append(Spacer(1, 20))
    
    # Quick Launch Checklist
    story.append(Paragraph("Quick Launch Checklist (For Tomorrow)", heading_style))
    
    checklist_data = [
        ['Priority', 'Task', 'Time', 'Status'],
        ['1', 'Deploy to cloud platform', '2 hours', '☐'],
        ['2', 'Configure HTTPS and domain', '1 hour', '☐'],
        ['3', 'Test all core functionality', '1 hour', '☐'],
        ['4', 'Create basic documentation', '1 hour', '☐'],
        ['5', 'Set up payment processing', '1 hour', '☐'],
        ['6', 'Create onboarding process', '1 hour', '☐'],
    ]
    
    table6 = Table(checklist_data, colWidths=[0.8*inch, 3*inch, 1*inch, 0.8*inch])
    table6.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(table6)
    
    # Build PDF
    doc.build(story)
    print("PDF created successfully: Restaurant_SaaS_Implementation_Plan.pdf")

if __name__ == "__main__":
    create_implementation_pdf()