#!/usr/bin/env python3
"""
Generator Specs - Medical Imaging Electrical Specifications Tool
Redesigned UI matching web interface

Features:
- Clean top navigation
- Horizontal phase/power selection
- Tab-based content
- Modern card-based specs display
- PDF reports with wiring diagrams
- Auto-install dependencies

Author: Maven Imaging
Version: 5.0
"""

import subprocess
import sys

def install_dependencies():
    """Check and install required dependencies."""
    required_packages = {
        'customtkinter': 'customtkinter',
        'reportlab': 'reportlab',
        'PIL': 'Pillow',
    }
    
    missing_packages = []
    for import_name, pip_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
                print(f"  ✓ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Failed to install {package}: {e}")
                sys.exit(1)
        print("All dependencies installed successfully!\n")

install_dependencies()

import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import sqlite3
import hashlib
import os
from pathlib import Path
import tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PIL import Image as PILImage, ImageDraw, ImageFont
import base64
import io


# =============================================================================
# LOGO DATA
# =============================================================================

LOGO_BASE64 = "data:image/png;base64,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"


# =============================================================================
# APP DATA DIRECTORY
# =============================================================================

def get_app_data_dir() -> Path:
    """Get the application data directory, creating it if needed."""
    if sys.platform == 'win32':
        app_dir = Path("C:/ProgramData/Maven")
    else:
        # Fallback for non-Windows systems
        app_dir = Path.home() / ".maven"
    
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


APP_DATA_DIR = get_app_data_dir()


# =============================================================================
# THEME - Matching web design
# =============================================================================

class Theme:
    # Backgrounds
    BG_PRIMARY = "#0f172a"      # slate-900
    BG_SECONDARY = "#1e293b"    # slate-800
    BG_CARD = "#1e293b"         # slate-800 with opacity
    BG_CARD_HOVER = "#334155"   # slate-700
    
    # Accent colors
    BLUE = "#3b82f6"            # blue-500
    BLUE_DARK = "#2563eb"       # blue-600
    BLUE_LIGHT = "#60a5fa"      # blue-400
    BLUE_BG = "#1e3a5f"         # blue tinted bg
    
    GREEN = "#22c55e"
    GREEN_DARK = "#16a34a"
    PURPLE = "#a855f7"
    PURPLE_DARK = "#9333ea"
    YELLOW = "#eab308"
    ORANGE = "#f97316"
    CYAN = "#06b6d4"
    PINK = "#ec4899"
    EMERALD = "#10b981"
    AMBER = "#f59e0b"
    
    # Text
    TEXT_PRIMARY = "#f8fafc"    # slate-50
    TEXT_SECONDARY = "#94a3b8"  # slate-400
    TEXT_MUTED = "#64748b"      # slate-500
    
    # Borders
    BORDER = "#334155"          # slate-700
    BORDER_LIGHT = "#475569"    # slate-600


# =============================================================================
# DATA
# =============================================================================

@dataclass
class WiringSpecs:
    voltage: str
    amperage: str
    wire_gauge: str
    conduit_size: str
    breaker_size: str
    ground_wire: str
    neutral_wire: str
    receptacle: str
    notes: str


@dataclass
class SavedReport:
    id: str
    project_name: str
    phase_type: str
    power_rating: int
    status: str
    created_at: str
    updated_at: str
    project_address: str = ""
    contractor: str = ""
    electrician: str = ""
    license_number: str = ""
    custom_notes: str = ""
    checklist_data: str = "{}"
    load_data: str = "[]"
    pdf_path: str = ""


SINGLE_PHASE_SPECS = {
    30: WiringSpecs("240V", "125A", "1/0 AWG Copper", '1.5" (1-1/2 inch)', "150A",
                   "6 AWG Copper", "1/0 AWG", "Hardwired dedicated circuit",
                   "Requires isolated ground. Dedicated circuit mandatory per NFPA 99. Must be on emergency power system per healthcare facility code."),
    32: WiringSpecs("240V", "133A", "1/0 AWG Copper", '1.5" (1-1/2 inch)', "150A",
                   "6 AWG Copper", "1/0 AWG", "Hardwired dedicated circuit",
                   "Isolated ground required. Room requires RF shielding. Emergency power backup mandatory."),
    40: WiringSpecs("240V", "167A", "2/0 AWG Copper", '2" (2 inch)', "200A",
                   "4 AWG Copper", "2/0 AWG", "Hardwired dedicated circuit",
                   "High-power imaging. Requires 200A+ service. Isolated ground and RF shielding mandatory."),
    50: WiringSpecs("240V", "208A", "4/0 AWG Copper", '2.5" (2-1/2 inch)', "250A",
                   "4 AWG Copper", "4/0 AWG", "Hardwired dedicated circuit",
                   "CT/MRI class system. Requires dedicated transformer. Harmonic filtering recommended."),
    60: WiringSpecs("240V", "250A", "250 MCM Copper", '3" (3 inch)', "300A",
                   "2 AWG Copper", "250 MCM", "Hardwired dedicated circuit",
                   "High-field MRI or advanced CT. Requires dedicated service entrance. Power quality monitoring essential."),
}

THREE_PHASE_SPECS = {
    30: WiringSpecs("208V/480V", "83A @ 208V / 36A @ 480V",
                   "4 AWG Copper (208V) / 8 AWG Copper (480V)", '1.25" (1-1/4 inch)',
                   "100A (208V) / 50A (480V)", "8 AWG Copper", "4 AWG (if required)",
                   "Hardwired 4-wire connection",
                   "Three-phase medical imaging. Isolated ground required. Phase balance critical for image quality."),
    32: WiringSpecs("208V/480V", "89A @ 208V / 39A @ 480V",
                   "3 AWG Copper (208V) / 8 AWG Copper (480V)", '1.25" (1-1/4 inch)',
                   "100A (208V) / 50A (480V)", "8 AWG Copper", "3 AWG (if required)",
                   "Hardwired 4-wire connection",
                   "Advanced imaging equipment. Voltage regulation ±5% required. RF shielding mandatory."),
    40: WiringSpecs("208V/480V", "111A @ 208V / 48A @ 480V",
                   "1 AWG Copper (208V) / 6 AWG Copper (480V)", '1.5" (1-1/2 inch)',
                   "125A (208V) / 60A (480V)", "6 AWG Copper", "1 AWG (if required)",
                   "Hardwired 4-wire connection",
                   "CT scanner class equipment. Power quality monitoring required. THD must be <5%."),
    50: WiringSpecs("208V/480V", "139A @ 208V / 60A @ 480V",
                   "1/0 AWG Copper (208V) / 4 AWG Copper (480V)", '2" (2 inch)',
                   "175A (208V) / 80A (480V)", "6 AWG Copper", "1/0 AWG (if required)",
                   "Hardwired 4-wire connection",
                   "High-power CT/MRI system. Dedicated transformer recommended. Active harmonic filter may be required."),
    60: WiringSpecs("208V/480V", "167A @ 208V / 72A @ 480V",
                   "2/0 AWG Copper (208V) / 3 AWG Copper (480V)", '2" (2 inch)',
                   "200A (208V) / 100A (480V)", "4 AWG Copper", "2/0 AWG (if required)",
                   "Hardwired 4-wire connection",
                   "Premium imaging suite. Dedicated electrical room required. K-rated transformer mandatory."),
}

POWER_RATINGS = [30, 32, 40, 50, 60]

DEFAULT_LOADS = [
    {"id": 1, "name": "X-Ray Tube", "watts": 15000, "quantity": 1},
    {"id": 2, "name": "Image Processor", "watts": 3000, "quantity": 1},
    {"id": 3, "name": "Room HVAC", "watts": 2000, "quantity": 1},
]

SAFETY_CHECKLIST = {
    "Pre-Installation": [
        "Verify all permits obtained",
        "Review local codes",
        "Confirm specs with manufacturer",
        "Schedule inspections"
    ],
    "Electrical System": [
        "Dedicated circuit installed",
        "Proper wire gauge verified",
        "Breaker size matches specs",
        "Connections properly torqued"
    ],
    "Grounding": [
        "Ground rod depth (8ft min)",
        "Ground resistance (<1Ω)",
        "Isolated ground installed",
        "No ground loops"
    ],
    "Power Quality": [
        "Voltage within ±5%",
        "THD within limits (<5%)",
        "Power quality monitor installed"
    ],
}

FAQ_DATABASE = [
    {"category": "Electrical", "question": "What is isolated ground?",
     "answer": "Isolated ground is a dedicated grounding conductor that runs separately from equipment ground back to service entrance. Required by NFPA 99 for medical imaging."},
    {"category": "Electrical", "question": "Why three-phase power?",
     "answer": "High-power medical imaging (>40kW) requires three-phase for efficient power delivery, reduced harmonics, and better voltage stability."},
    {"category": "Installation", "question": "Ground rod depth?",
     "answer": "At least 8 feet deep, <1 ohm resistance. Multiple rods may be required, spaced 6+ feet apart."},
    {"category": "Safety", "question": "RF shielding requirements?",
     "answer": "Required for all MRI systems (>100dB attenuation). Not typically required for standard X-ray or ultrasound."},
]


# =============================================================================
# DATABASE
# =============================================================================

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(APP_DATA_DIR / "generator_specs.db")
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    project_name TEXT NOT NULL,
                    phase_type TEXT NOT NULL,
                    power_rating INTEGER NOT NULL,
                    status TEXT DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    project_address TEXT DEFAULT '',
                    contractor TEXT DEFAULT '',
                    electrician TEXT DEFAULT '',
                    license_number TEXT DEFAULT '',
                    custom_notes TEXT DEFAULT '',
                    checklist_data TEXT DEFAULT '{}',
                    load_data TEXT DEFAULT '[]',
                    pdf_path TEXT DEFAULT ''
                )
            ''')
            conn.commit()
    
    def save_report(self, report: SavedReport) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT OR REPLACE INTO reports VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (report.id, report.project_name, report.phase_type, report.power_rating,
                     report.status, report.created_at, report.updated_at, report.project_address,
                     report.contractor, report.electrician, report.license_number, report.custom_notes,
                     report.checklist_data, report.load_data, report.pdf_path)
                )
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def get_reports(self, limit: int = 50) -> List[SavedReport]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports ORDER BY updated_at DESC LIMIT ?", (limit,))
                return [SavedReport(*row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def delete_report(self, report_id: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
                conn.commit()
                return True
        except sqlite3.Error:
            return False


# =============================================================================
# PDF GENERATOR
# =============================================================================

class PDFReportGenerator:
    def __init__(self):
        self.COLORS = {
            'primary': colors.HexColor('#1e40af'),
            'primary_light': colors.HexColor('#3b82f6'),
            'success': colors.HexColor('#15803d'),
            'warning': colors.HexColor('#a16207'),
            'danger': colors.HexColor('#b91c1c'),
            'text': colors.HexColor('#1f2937'),
            'text_light': colors.HexColor('#6b7280'),
            'bg_light': colors.HexColor('#f1f5f9'),
            'border': colors.HexColor('#cbd5e1'),
        }
        self.styles = self._create_styles()
    
    def _create_styles(self):
        base = getSampleStyleSheet()
        return {
            'title': ParagraphStyle('Title', parent=base['Heading1'], fontSize=24,
                                   textColor=self.COLORS['primary'], alignment=TA_CENTER),
            'subtitle': ParagraphStyle('Subtitle', parent=base['Normal'], fontSize=12,
                                       textColor=self.COLORS['text_light'], alignment=TA_CENTER),
            'section': ParagraphStyle('Section', parent=base['Heading2'], fontSize=14,
                                     textColor=self.COLORS['primary'], spaceBefore=15, spaceAfter=10),
            'body': ParagraphStyle('Body', parent=base['Normal'], fontSize=10,
                                  textColor=self.COLORS['text'], spaceAfter=6),
            'body_bold': ParagraphStyle('BodyBold', parent=base['Normal'], fontSize=10,
                                       textColor=self.COLORS['text'], fontName='Helvetica-Bold'),
        }
    
    def generate(self, filename: str, data: dict) -> bool:
        temp_diagram = None
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch,
                                   bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
            story = []
            
            # Header
            story.append(Paragraph("MAVEN IMAGING", self.styles['subtitle']))
            story.append(Paragraph("X-Ray Medical Imaging System Specifications", self.styles['title']))
            story.append(Spacer(1, 10))
            
            # Config banner
            phase = "Single Phase" if data.get('phase_type') == 'single' else "Three Phase"
            config = [[Paragraph(f"<b>Configuration:</b> {phase} • {data.get('power_rating', 30)} kW", 
                                self.styles['body_bold'])]]
            t = Table(config, colWidths=[7*inch])
            t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), self.COLORS['bg_light']),
                                   ('BOX', (0,0), (-1,-1), 1, self.COLORS['primary']),
                                   ('TOPPADDING', (0,0), (-1,-1), 10),
                                   ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                                   ('LEFTPADDING', (0,0), (-1,-1), 15)]))
            story.append(t)
            story.append(Spacer(1, 15))
            
            # Project info
            story.append(Paragraph("PROJECT INFORMATION", self.styles['section']))
            info = [
                ['Project:', data.get('project_name', 'N/A')],
                ['Address:', data.get('project_address', 'N/A') or 'N/A'],
                ['Contractor:', data.get('contractor', 'N/A') or 'N/A'],
                ['Electrician:', data.get('electrician', 'N/A') or 'N/A'],
                ['Date:', datetime.now().strftime('%B %d, %Y')],
            ]
            t = Table(info, colWidths=[1.2*inch, 5.8*inch])
            t.setStyle(TableStyle([('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                                   ('FONTSIZE', (0,0), (-1,-1), 10),
                                   ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
            story.append(t)
            story.append(Spacer(1, 15))
            
            # Specs table
            story.append(Paragraph("ELECTRICAL SPECIFICATIONS", self.styles['section']))
            specs = data.get('specs', {})
            spec_rows = [
                [Paragraph('<b>Parameter</b>', self.styles['body_bold']),
                 Paragraph('<b>Value</b>', self.styles['body_bold'])],
                ['Voltage', specs.get('voltage', 'N/A')],
                ['Amperage', specs.get('amperage', 'N/A')],
                ['Wire Gauge (Hot)', specs.get('wire_gauge', 'N/A')],
                ['Neutral Wire', specs.get('neutral_wire', 'N/A')],
                ['Ground Wire', specs.get('ground_wire', 'N/A')],
                ['Conduit Size', specs.get('conduit_size', 'N/A')],
                ['Breaker Size', specs.get('breaker_size', 'N/A')],
                ['Connection', specs.get('receptacle', 'N/A')],
            ]
            t = Table(spec_rows, colWidths=[2*inch, 5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), self.COLORS['primary']),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, self.COLORS['border']),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, self.COLORS['bg_light']]),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
            
            # Wiring diagram
            temp_diagram = self._generate_diagram(data)
            if temp_diagram:
                story.append(Paragraph("WIRING DIAGRAM", self.styles['section']))
                story.append(Image(temp_diagram, width=7*inch, height=4*inch))
                story.append(Spacer(1, 15))
            
            # Loads
            if data.get('loads'):
                story.append(Paragraph("LOAD ANALYSIS", self.styles['section']))
                load_rows = [[Paragraph('<b>Equipment</b>', self.styles['body_bold']),
                             Paragraph('<b>Watts</b>', self.styles['body_bold']),
                             Paragraph('<b>Qty</b>', self.styles['body_bold']),
                             Paragraph('<b>Total</b>', self.styles['body_bold'])]]
                total = 0
                for load in data['loads']:
                    t = load['watts'] * load['quantity']
                    total += t
                    load_rows.append([load['name'], f"{load['watts']:,}", str(load['quantity']), f"{t:,} W"])
                load_rows.append(['', '', 'Total:', f"{total:,} W"])
                t = Table(load_rows, colWidths=[3*inch, 1.5*inch, 0.75*inch, 1.75*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), self.COLORS['primary']),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('GRID', (0,0), (-1,-1), 0.5, self.COLORS['border']),
                    ('FONTNAME', (2,-1), (-1,-1), 'Helvetica-Bold'),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(t)
                story.append(Spacer(1, 15))
            
            # Notes
            if data.get('specs_notes'):
                story.append(Paragraph("IMPORTANT NOTES", self.styles['section']))
                story.append(Paragraph(data['specs_notes'], self.styles['body']))
            
            doc.build(story)
            return True
        except Exception as e:
            print(f"PDF Error: {e}")
            return False
        finally:
            if temp_diagram and os.path.exists(temp_diagram):
                try:
                    os.remove(temp_diagram)
                except:
                    pass
    
    def _generate_diagram(self, data: dict) -> Optional[str]:
        try:
            width, height = 800, 450
            img = PILImage.new('RGB', (width, height), '#FFFFFF')
            draw = ImageDraw.Draw(img)
            
            phase = data.get('phase_type', 'single')
            power = data.get('power_rating', 30)
            specs = data.get('specs', {})
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 18)
                label_font = ImageFont.truetype("arial.ttf", 12)
                small_font = ImageFont.truetype("arial.ttf", 10)
            except:
                title_font = label_font = small_font = ImageFont.load_default()
            
            # Colors
            red, green, blue, yellow = '#ef4444', '#22c55e', '#3b82f6', '#eab308'
            gray, text_color = '#e2e8f0', '#1e293b'
            box_bg, box_border = '#f1f5f9', '#64748b'
            
            title = f"{'SINGLE' if phase == 'single' else 'THREE'} PHASE - {power} kW"
            draw.text((width//2, 20), title, fill=text_color, font=title_font, anchor='mm')
            
            # Draw boxes
            boxes = [
                (50, 80, 170, 180, "POWER\nSOURCE", specs.get('voltage', '240V'), box_border),
                (230, 80, 350, 180, "MAIN\nBREAKER", specs.get('breaker_size', '150A'), '#a855f7'),
                (410, 80, 530, 180, "DISCONNECT", "Fused", yellow),
                (410, 250, 530, 370, "IMAGING\nEQUIPMENT", f"{power} kW", blue),
                (230, 270, 350, 370, "GROUND\nROD", "<1Ω", green),
            ]
            
            for x1, y1, x2, y2, label, value, color in boxes:
                draw.rectangle([x1, y1, x2, y2], fill=box_bg, outline=color, width=2)
                lines = label.split('\n')
                y_offset = y1 + 25
                for line in lines:
                    draw.text(((x1+x2)//2, y_offset), line, fill=text_color, font=label_font, anchor='mm')
                    y_offset += 18
                draw.text(((x1+x2)//2, y2-25), value, fill=color, font=label_font, anchor='mm')
            
            # Wires
            if phase == 'single':
                # Hot (red)
                draw.line([(170, 110), (230, 110)], fill=red, width=3)
                draw.line([(350, 110), (410, 110)], fill=red, width=3)
                draw.line([(470, 180), (470, 250)], fill=red, width=3)
                # Neutral (gray)
                draw.line([(170, 130), (230, 130)], fill=gray, width=3)
                draw.line([(350, 130), (410, 130)], fill=gray, width=3)
                draw.line([(450, 180), (450, 250)], fill=gray, width=3)
                # Ground (green)
                draw.line([(170, 150), (230, 150)], fill=green, width=3)
                draw.line([(350, 150), (380, 150)], fill=green, width=3)
                draw.line([(380, 150), (380, 310)], fill=green, width=3)
                draw.line([(350, 310), (380, 310)], fill=green, width=3)
                draw.line([(380, 310), (410, 310)], fill=green, width=3)
            else:
                # Phase A (red)
                draw.line([(170, 100), (230, 100)], fill=red, width=3)
                draw.line([(350, 100), (410, 100)], fill=red, width=3)
                draw.line([(480, 180), (480, 250)], fill=red, width=3)
                # Phase B (yellow)
                draw.line([(170, 120), (230, 120)], fill=yellow, width=3)
                draw.line([(350, 120), (410, 120)], fill=yellow, width=3)
                draw.line([(465, 180), (465, 250)], fill=yellow, width=3)
                # Phase C (blue)
                draw.line([(170, 140), (230, 140)], fill=blue, width=3)
                draw.line([(350, 140), (410, 140)], fill=blue, width=3)
                draw.line([(450, 180), (450, 250)], fill=blue, width=3)
                # Ground (green)
                draw.line([(170, 160), (230, 160)], fill=green, width=3)
                draw.line([(350, 160), (380, 160)], fill=green, width=3)
                draw.line([(380, 160), (380, 310)], fill=green, width=3)
                draw.line([(350, 310), (410, 310)], fill=green, width=3)
            
            # Legend
            y = 410
            if phase == 'single':
                legend = [("Hot", red), ("Neutral", gray), ("Ground", green)]
            else:
                legend = [("Phase A", red), ("Phase B", yellow), ("Phase C", blue), ("Ground", green)]
            
            x = 100
            for label, color in legend:
                draw.line([(x, y), (x+30, y)], fill=color, width=4)
                draw.text((x+40, y), label, fill=text_color, font=small_font, anchor='lm')
                x += 120
            
            temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            img.save(temp.name, 'PNG')
            return temp.name
        except Exception as e:
            print(f"Diagram error: {e}")
            return None


# =============================================================================
# TOAST NOTIFICATION
# =============================================================================

class Toast(ctk.CTkFrame):
    def __init__(self, parent, message: str, type_: str = "info"):
        super().__init__(parent, corner_radius=8, height=45)
        
        colors_map = {
            "success": (Theme.GREEN, "#14532d"),
            "error": ("#ef4444", "#7f1d1d"),
            "warning": (Theme.YELLOW, "#713f12"),
            "info": (Theme.BLUE, Theme.BLUE_BG),
        }
        accent, bg = colors_map.get(type_, colors_map["info"])
        self.configure(fg_color=bg, border_width=1, border_color=accent)
        
        ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=12),
                    text_color=Theme.TEXT_PRIMARY).pack(side="left", padx=15, pady=8)
        ctk.CTkButton(self, text="×", width=28, height=28, fg_color="transparent",
                     hover_color=Theme.BG_CARD_HOVER, command=self.destroy).pack(side="right", padx=5)
        
        self.place(relx=0.5, y=-50, anchor="n")
        self._animate_in()
        self.after(3000, self._animate_out)
    
    def _animate_in(self):
        def step(y):
            if y < 15:
                self.place(relx=0.5, y=y, anchor="n")
                self.after(8, lambda: step(y + 4))
        step(-50)
    
    def _animate_out(self):
        def step(y):
            if y > -50:
                self.place(relx=0.5, y=y, anchor="n")
                self.after(8, lambda: step(y - 6))
            else:
                self.destroy()
        step(15)


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class GeneratorSpecsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Generator Specs - Maven Imaging")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=Theme.BG_PRIMARY)
        
        self.db = DatabaseManager()
        self.pdf = PDFReportGenerator()
        self.reports_dir = APP_DATA_DIR / "Reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # State
        self.selected_phase: Optional[str] = None
        self.selected_power: Optional[int] = None
        self.current_specs: Optional[WiringSpecs] = None
        self.current_tab = "specs"
        self.loads = [dict(d) for d in DEFAULT_LOADS]
        self.load_id = 4
        self.checklist_vars: Dict[str, ctk.BooleanVar] = {}
        self.project_info = {k: ctk.StringVar() for k in 
                           ["project_name", "project_address", "contractor", "electrician", "license_number"]}
        
        self._build_ui()
        self.bind("<Control-s>", lambda e: self._save_report())
    
    def _toast(self, msg: str, type_: str = "info"):
        Toast(self, msg, type_)
    
    def _build_ui(self):
        # Top nav
        nav = ctk.CTkFrame(self, fg_color=Theme.BG_SECONDARY, height=60, corner_radius=0)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        
        nav_inner = ctk.CTkFrame(nav, fg_color="transparent")
        nav_inner.pack(fill="both", expand=True, padx=30)
        
        # Logo (base64 image)
        logo_frame = ctk.CTkFrame(nav_inner, fg_color="transparent")
        logo_frame.pack(side="left", pady=10)
        
        # Load logo from base64
        try:
            logo_data = LOGO_BASE64.split(",")[1] if "," in LOGO_BASE64 else LOGO_BASE64
            # Pad base64 string if needed
            padding = 4 - len(logo_data) % 4
            if padding != 4:
                logo_data += "=" * padding
            logo_bytes = base64.b64decode(logo_data)
            logo_pil = PILImage.open(io.BytesIO(logo_bytes))
            # Resize to fit nicely in the header (height ~40px)
            aspect = logo_pil.width / logo_pil.height
            new_height = 40
            new_width = int(new_height * aspect)
            logo_pil = logo_pil.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
            self.logo_image = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, 
                                           size=(new_width, new_height))
            logo_label = ctk.CTkLabel(logo_frame, image=self.logo_image, text="")
            logo_label.pack(side="left")
        except Exception as e:
            # Fallback to text if image fails
            ctk.CTkLabel(logo_frame, text="Maven Imaging", font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=Theme.TEXT_PRIMARY).pack(side="left")
        
        # Nav buttons
        nav_btns = ctk.CTkFrame(nav_inner, fg_color="transparent")
        nav_btns.pack(side="right", pady=10)
        
        self.nav_buttons = {}
        for page, label in [("specs", "📋 Specifications"), ("support", "💬 Support"), ("reports", "📄 Reports")]:
            btn = ctk.CTkButton(nav_btns, text=label, font=ctk.CTkFont(size=12),
                               fg_color=Theme.BLUE if page == "specs" else "transparent",
                               hover_color=Theme.BG_CARD_HOVER, height=36, corner_radius=8,
                               command=lambda p=page: self._nav_to(p))
            btn.pack(side="left", padx=4)
            self.nav_buttons[page] = btn
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        
        self.pages = {}
        self._build_specs_page()
        self._build_support_page()
        self._build_reports_page()
        
        self._nav_to("specs")
    
    def _nav_to(self, page: str):
        for p in self.pages.values():
            p.pack_forget()
        
        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color=Theme.BLUE if name == page else "transparent")
        
        self.pages[page].pack(fill="both", expand=True)
        
        if page == "reports":
            self._refresh_reports()
    
    # =========================================================================
    # SPECS PAGE
    # =========================================================================
    
    def _build_specs_page(self):
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent",
                                      scrollbar_button_color=Theme.BORDER)
        self.pages["specs"] = page
        
        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Header
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        icon_frame = ctk.CTkFrame(header, width=50, height=50, fg_color=Theme.BLUE_BG, corner_radius=12)
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="⚡", font=ctk.CTkFont(size=24),
                    text_color=Theme.BLUE_LIGHT).place(relx=0.5, rely=0.5, anchor="center")
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=(15, 0))
        ctk.CTkLabel(title_frame, text="X-Ray Medical Imaging Systems",
                    font=ctk.CTkFont(size=22, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Electrical specifications for medical imaging equipment",
                    font=ctk.CTkFont(size=12), text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
        
        # Phase Selection
        ctk.CTkLabel(content, text="Select Phase Type", font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(20, 5))
        ctk.CTkLabel(content, text="Choose the electrical system for your imaging equipment",
                    font=ctk.CTkFont(size=12), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 12))
        
        phase_frame = ctk.CTkFrame(content, fg_color="transparent")
        phase_frame.pack(fill="x", pady=(0, 25))
        
        self.phase_buttons = {}
        for i, (phase, title, subtitle, voltage) in enumerate([
            ("single", "Single Phase", "Small Clinic", "240V for small imaging systems"),
            ("three", "Three Phase", "Hospital/Imaging Center", "208V/480V for CT, MRI systems")
        ]):
            card = ctk.CTkFrame(phase_frame, fg_color=Theme.BG_CARD, corner_radius=16,
                               border_width=2, border_color=Theme.BORDER)
            card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 8, 8 if i == 0 else 0))
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=20, pady=18)
            
            # Phase indicator
            indicator_frame = ctk.CTkFrame(inner, fg_color="transparent")
            indicator_frame.pack(anchor="w")
            
            if phase == "single":
                dot = ctk.CTkFrame(indicator_frame, width=12, height=12, fg_color=Theme.BLUE, corner_radius=6)
                dot.pack(side="left")
            else:
                for _ in range(3):
                    dot = ctk.CTkFrame(indicator_frame, width=8, height=12, fg_color=Theme.TEXT_MUTED, corner_radius=2)
                    dot.pack(side="left", padx=1)
            
            ctk.CTkLabel(indicator_frame, text=subtitle.upper(), font=ctk.CTkFont(size=10),
                        text_color=Theme.TEXT_MUTED).pack(side="left", padx=(8, 0))
            
            ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=18, weight="bold"),
                        text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(10, 2))
            ctk.CTkLabel(inner, text=voltage, font=ctk.CTkFont(size=12),
                        text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
            
            # Make clickable
            for widget in [card, inner] + list(inner.winfo_children()):
                widget.bind("<Button-1>", lambda e, p=phase: self._select_phase(p))
                widget.bind("<Enter>", lambda e, c=card: c.configure(border_color=Theme.BORDER_LIGHT))
                widget.bind("<Leave>", lambda e, c=card, p=phase: c.configure(
                    border_color=Theme.BLUE if self.selected_phase == p else Theme.BORDER))
            
            self.phase_buttons[phase] = card
        
        # Power Rating Selection
        ctk.CTkLabel(content, text="Select System Power Rating", font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(content, text="Choose the power requirement in kilowatts",
                    font=ctk.CTkFont(size=12), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 12))
        
        power_frame = ctk.CTkFrame(content, fg_color="transparent")
        power_frame.pack(fill="x", pady=(0, 25))
        
        self.power_buttons = {}
        for power in POWER_RATINGS:
            btn = ctk.CTkButton(power_frame, text=f"{power}\nkW", width=90, height=70,
                               font=ctk.CTkFont(size=18, weight="bold"),
                               fg_color=Theme.BG_CARD, hover_color=Theme.BG_CARD_HOVER,
                               border_width=2, border_color=Theme.BORDER, corner_radius=12,
                               command=lambda p=power: self._select_power(p))
            btn.pack(side="left", padx=(0, 10))
            self.power_buttons[power] = btn
        
        # Results section (hidden initially)
        self.results_frame = ctk.CTkFrame(content, fg_color="transparent")
        
        # Blue banner
        self.banner = ctk.CTkFrame(self.results_frame, fg_color=Theme.BLUE, corner_radius=16, height=100)
        self.banner.pack(fill="x", pady=(0, 20))
        self.banner.pack_propagate(False)
        
        banner_inner = ctk.CTkFrame(self.banner, fg_color="transparent")
        banner_inner.pack(fill="both", expand=True, padx=25, pady=15)
        
        banner_left = ctk.CTkFrame(banner_inner, fg_color="transparent")
        banner_left.pack(side="left", fill="y")
        
        self.banner_badges = ctk.CTkFrame(banner_left, fg_color="transparent")
        self.banner_badges.pack(anchor="w")
        
        self.phase_badge = ctk.CTkLabel(self.banner_badges, text="Single Phase",
                                        font=ctk.CTkFont(size=11), fg_color="#2563eb",
                                        corner_radius=4, text_color="white")
        self.phase_badge.pack(side="left", padx=(0, 6), ipadx=8, ipady=2)
        
        self.power_badge = ctk.CTkLabel(self.banner_badges, text="30 kW",
                                        font=ctk.CTkFont(size=11), fg_color="#2563eb",
                                        corner_radius=4, text_color="white")
        self.power_badge.pack(side="left", ipadx=8, ipady=2)
        
        ctk.CTkLabel(banner_left, text="Complete Installation Package",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color="white").pack(anchor="w", pady=(8, 2))
        ctk.CTkLabel(banner_left, text="Includes specs, wiring diagram, load calc & safety checklist",
                    font=ctk.CTkFont(size=12), text_color="#e2e8f0").pack(anchor="w")
        
        banner_btns = ctk.CTkFrame(banner_inner, fg_color="transparent")
        banner_btns.pack(side="right")
        
        ctk.CTkButton(banner_btns, text="⬇ Generate PDF", font=ctk.CTkFont(size=12),
                     fg_color=Theme.PURPLE, hover_color=Theme.PURPLE_DARK, height=36,
                     corner_radius=6, command=self._save_report).pack(side="left", padx=(0, 8))
        ctk.CTkButton(banner_btns, text="↻ Change Selection", font=ctk.CTkFont(size=12),
                     fg_color="#1e40af", hover_color="#1e3a8a", height=36,
                     corner_radius=6, command=self._reset_selection).pack(side="left")
        
        # Tabs
        self.tabs_frame = ctk.CTkFrame(self.results_frame, fg_color=Theme.BG_CARD,
                                       corner_radius=10, border_width=1, border_color=Theme.BORDER)
        self.tabs_frame.pack(fill="x", pady=(0, 20))
        
        tabs_inner = ctk.CTkFrame(self.tabs_frame, fg_color="transparent")
        tabs_inner.pack(fill="x", padx=4, pady=4)
        
        self.tab_buttons = {}
        for tab, label in [("specs", "Specs"), ("load", "Load Calc"), ("diagram", "Diagram"),
                          ("safety", "Safety"), ("report", "Report")]:
            btn = ctk.CTkButton(tabs_inner, text=label, font=ctk.CTkFont(size=12),
                               fg_color=Theme.BLUE if tab == "specs" else "transparent",
                               hover_color=Theme.BG_CARD_HOVER, height=32, corner_radius=6,
                               command=lambda t=tab: self._switch_tab(t))
            btn.pack(side="left", fill="x", expand=True, padx=2)
            self.tab_buttons[tab] = btn
        
        # Tab content area
        self.tab_content = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        self.tab_content.pack(fill="both", expand=True)
    
    def _select_phase(self, phase: str):
        self.selected_phase = phase
        for p, card in self.phase_buttons.items():
            if p == phase:
                card.configure(border_color=Theme.BLUE, fg_color=Theme.BLUE_BG)
            else:
                card.configure(border_color=Theme.BORDER, fg_color=Theme.BG_CARD)
        
        if self.selected_power:
            self._update_specs()
    
    def _select_power(self, power: int):
        self.selected_power = power
        for p, btn in self.power_buttons.items():
            btn.configure(border_color=Theme.BLUE if p == power else Theme.BORDER,
                         fg_color=Theme.BLUE_BG if p == power else Theme.BG_CARD)
        
        if self.selected_phase:
            self._update_specs()
    
    def _update_specs(self):
        if self.selected_phase == "single":
            self.current_specs = SINGLE_PHASE_SPECS.get(self.selected_power)
        else:
            self.current_specs = THREE_PHASE_SPECS.get(self.selected_power)
        
        # Update banner
        phase_text = "Single Phase" if self.selected_phase == "single" else "Three Phase"
        self.phase_badge.configure(text=phase_text)
        self.power_badge.configure(text=f"{self.selected_power} kW")
        
        # Show results
        self.results_frame.pack(fill="both", expand=True)
        self._switch_tab("specs")
    
    def _switch_tab(self, tab: str):
        self.current_tab = tab
        for t, btn in self.tab_buttons.items():
            btn.configure(fg_color=Theme.BLUE if t == tab else "transparent")
        
        # Clear content
        for widget in self.tab_content.winfo_children():
            widget.destroy()
        
        if tab == "specs":
            self._build_specs_tab()
        elif tab == "load":
            self._build_load_tab()
        elif tab == "diagram":
            self._build_diagram_tab()
        elif tab == "safety":
            self._build_safety_tab()
        elif tab == "report":
            self._build_report_tab()
    
    def _build_specs_tab(self):
        specs = self.current_specs
        if not specs:
            return
        
        # Specs header
        header = ctk.CTkFrame(self.tab_content, fg_color=Theme.BLUE, corner_radius=12)
        header.pack(fill="x", pady=(0, 15))
        
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(header_inner, text="X-Ray Medical Imaging System Specifications",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="white").pack(anchor="w")
        
        info_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        info_frame.pack(anchor="w", pady=(8, 0))
        
        phase_text = "Single Phase" if self.selected_phase == "single" else "Three Phase"
        for label, value in [("Type:", phase_text), ("Power Rating:", f"{self.selected_power} kW"),
                            ("Date:", datetime.now().strftime("%B %d, %Y"))]:
            ctk.CTkLabel(info_frame, text=f"{label} {value}", font=ctk.CTkFont(size=12),
                        text_color="#e2e8f0").pack(side="left", padx=(0, 20))
        
        # Spec cards grid
        grid = ctk.CTkFrame(self.tab_content, fg_color="transparent")
        grid.pack(fill="x")
        
        # Color to dark background mapping
        color_bg_map = {
            Theme.YELLOW: "#422006",
            Theme.BLUE_LIGHT: "#1e3a5f",
            Theme.GREEN: "#14532d",
            Theme.PURPLE: "#3b0764",
            Theme.EMERALD: "#064e3b",
            Theme.ORANGE: "#431407",
            Theme.CYAN: "#083344",
            Theme.PINK: "#500724",
        }
        
        spec_items = [
            ("Voltage", specs.voltage, "⚡", Theme.YELLOW),
            ("Amperage", specs.amperage, "◎", Theme.BLUE_LIGHT),
            ("Wire Gauge (Hot)", specs.wire_gauge, "━", Theme.GREEN),
            ("Neutral Wire", specs.neutral_wire, "━", Theme.PURPLE),
            ("Ground Wire", specs.ground_wire, "━", Theme.EMERALD),
            ("Breaker Size", specs.breaker_size, "▢", Theme.ORANGE),
            ("Conduit Size", specs.conduit_size, "◯", Theme.CYAN),
            ("Connection Type", specs.receptacle, "⎓", Theme.PINK),
        ]
        
        for i, (label, value, icon, color) in enumerate(spec_items):
            card = ctk.CTkFrame(grid, fg_color=Theme.BG_CARD, corner_radius=12,
                               border_width=1, border_color=Theme.BORDER)
            row, col = divmod(i, 2)
            card.grid(row=row, column=col, padx=(0 if col == 0 else 8, 8 if col == 0 else 0),
                     pady=8, sticky="nsew")
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=18, pady=15)
            
            # Icon with dark tinted background
            icon_bg_color = color_bg_map.get(color, Theme.BG_SECONDARY)
            icon_bg = ctk.CTkFrame(inner, width=40, height=40, fg_color=icon_bg_color, corner_radius=8)
            icon_bg.pack(side="left")
            icon_bg.pack_propagate(False)
            ctk.CTkLabel(icon_bg, text=icon, font=ctk.CTkFont(size=18),
                        text_color=color).place(relx=0.5, rely=0.5, anchor="center")
            
            text_frame = ctk.CTkFrame(inner, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=(15, 0))
            
            ctk.CTkLabel(text_frame, text=label, font=ctk.CTkFont(size=11),
                        text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
            ctk.CTkLabel(text_frame, text=value, font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=Theme.TEXT_PRIMARY, wraplength=250).pack(anchor="w")
            
            # Hover effect
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=Theme.BG_CARD_HOVER))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=Theme.BG_CARD))
        
        grid.columnconfigure((0, 1), weight=1)
        
        # Notes
        notes_frame = ctk.CTkFrame(self.tab_content, fg_color="#422006", corner_radius=12,
                                  border_width=1, border_color="#92400e")
        notes_frame.pack(fill="x", pady=(15, 0))
        
        notes_inner = ctk.CTkFrame(notes_frame, fg_color="transparent")
        notes_inner.pack(fill="x", padx=18, pady=15)
        
        ctk.CTkLabel(notes_inner, text="⚠", font=ctk.CTkFont(size=18),
                    text_color=Theme.AMBER).pack(side="left", anchor="n")
        
        notes_text = ctk.CTkFrame(notes_inner, fg_color="transparent")
        notes_text.pack(side="left", fill="x", expand=True, padx=(12, 0))
        
        ctk.CTkLabel(notes_text, text="Important Notes", font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=Theme.AMBER).pack(anchor="w")
        ctk.CTkLabel(notes_text, text=specs.notes, font=ctk.CTkFont(size=12),
                    text_color="#fcd34d", wraplength=600).pack(anchor="w", pady=(4, 0))
    
    def _build_load_tab(self):
        # Header with add button
        header = ctk.CTkFrame(self.tab_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(header, text="Load Calculator", font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(header, text="+ Add Load", font=ctk.CTkFont(size=12),
                     fg_color=Theme.BLUE, hover_color=Theme.BLUE_DARK, height=34,
                     corner_radius=6, command=self._add_load).pack(side="right")
        
        # Loads list
        loads_frame = ctk.CTkFrame(self.tab_content, fg_color=Theme.BG_CARD, corner_radius=12)
        loads_frame.pack(fill="x", pady=(0, 15))
        
        for i, load in enumerate(self.loads):
            row = ctk.CTkFrame(loads_frame, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=12)
            
            ctk.CTkLabel(row, text=load["name"], font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=Theme.TEXT_PRIMARY).pack(side="left")
            
            watts = load["watts"] * load["quantity"]
            ctk.CTkLabel(row, text=f"{watts:,} W", font=ctk.CTkFont(size=13),
                        text_color=Theme.TEXT_SECONDARY).pack(side="left", padx=(15, 0))
            
            ctk.CTkButton(row, text="×", width=30, height=30, font=ctk.CTkFont(size=14),
                         fg_color="transparent", hover_color=Theme.BG_CARD_HOVER,
                         command=lambda lid=load["id"]: self._remove_load(lid)).pack(side="right")
            
            if i < len(self.loads) - 1:
                ctk.CTkFrame(loads_frame, height=1, fg_color=Theme.BORDER).pack(fill="x", padx=18)
        
        # Summary
        total_watts = sum(l["watts"] * l["quantity"] for l in self.loads)
        total_kw = total_watts / 1000
        capacity = self.selected_power or 30
        usage = (total_watts / (capacity * 1000)) * 100
        
        if usage > 100:
            status_color, status = "#ef4444", "OVERLOADED"
        elif usage > 80:
            status_color, status = Theme.YELLOW, "HIGH LOAD"
        else:
            status_color, status = Theme.GREEN, "SAFE"
        
        summary = ctk.CTkFrame(self.tab_content, fg_color=Theme.BG_CARD, corner_radius=12)
        summary.pack(fill="x")
        
        summary_inner = ctk.CTkFrame(summary, fg_color="transparent")
        summary_inner.pack(fill="x", padx=20, pady=18)
        
        stats = [
            ("Total Load", f"{total_kw:.1f} kW"),
            ("Capacity", f"{capacity} kW"),
            ("Usage", f"{usage:.0f}%"),
            ("Status", status),
        ]
        
        for label, value in stats:
            col = ctk.CTkFrame(summary_inner, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(col, text=label, font=ctk.CTkFont(size=11),
                        text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
            ctk.CTkLabel(col, text=value, font=ctk.CTkFont(size=16, weight="bold"),
                        text_color=status_color if label in ["Status", "Usage"] else Theme.TEXT_PRIMARY).pack(anchor="w")
        
        # Progress bar
        progress = ctk.CTkProgressBar(summary_inner, height=10, corner_radius=5,
                                      progress_color=status_color, fg_color=Theme.BORDER)
        progress.pack(fill="x", pady=(15, 0))
        progress.set(min(usage / 100, 1.0))
    
    def _add_load(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Load")
        dialog.geometry("350x280")
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 350) // 2
        y = self.winfo_y() + (self.winfo_height() - 280) // 2
        dialog.geometry(f"+{x}+{y}")
        
        content = ctk.CTkFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(content, text="Add New Load", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        
        name_var = ctk.StringVar()
        watts_var = ctk.StringVar()
        qty_var = ctk.StringVar(value="1")
        
        for label, var, placeholder in [("Name", name_var, "e.g., X-Ray Tube"),
                                        ("Watts", watts_var, "e.g., 15000"),
                                        ("Quantity", qty_var, "1")]:
            ctk.CTkLabel(content, text=label, font=ctk.CTkFont(size=11),
                        text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(12, 4))
            ctk.CTkEntry(content, textvariable=var, placeholder_text=placeholder,
                        height=36, fg_color=Theme.BG_CARD).pack(fill="x")
        
        def submit():
            try:
                self.loads.append({
                    "id": self.load_id,
                    "name": name_var.get() or "New Load",
                    "watts": int(watts_var.get() or 0),
                    "quantity": int(qty_var.get() or 1)
                })
                self.load_id += 1
                dialog.destroy()
                self._switch_tab("load")
            except ValueError:
                pass
        
        ctk.CTkButton(content, text="Add", font=ctk.CTkFont(size=12),
                     fg_color=Theme.GREEN, hover_color=Theme.GREEN_DARK,
                     height=36, command=submit).pack(fill="x", pady=(20, 0))
    
    def _remove_load(self, load_id: int):
        self.loads = [l for l in self.loads if l["id"] != load_id]
        self._switch_tab("load")
    
    def _build_diagram_tab(self):
        ctk.CTkLabel(self.tab_content, text="Wiring Diagram", font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 15))
        
        canvas_frame = ctk.CTkFrame(self.tab_content, fg_color=Theme.BG_CARD, corner_radius=12)
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=Theme.BG_CARD, highlightthickness=0, width=700, height=400)
        canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        specs = self.current_specs
        if not specs:
            return
        
        # Colors
        red, green, blue, yellow = "#ef4444", "#22c55e", "#3b82f6", "#eab308"
        gray, text_color, purple = "#94a3b8", Theme.TEXT_PRIMARY, "#a855f7"
        
        phase = self.selected_phase
        power = self.selected_power
        
        # Title
        title = f"{'SINGLE' if phase == 'single' else 'THREE'} PHASE - {power} kW"
        canvas.create_text(350, 25, text=title, font=("Segoe UI", 14, "bold"), fill=text_color)
        
        # Draw boxes
        boxes = [
            (50, 80, 160, 160, "POWER SOURCE", specs.voltage, Theme.BORDER),
            (220, 80, 330, 160, "BREAKER", specs.breaker_size, purple),
            (390, 80, 500, 160, "DISCONNECT", "Fused", yellow),
            (390, 220, 500, 320, "EQUIPMENT", f"{power} kW", blue),
            (220, 240, 330, 320, "GROUND", "<1Ω", green),
        ]
        
        for x1, y1, x2, y2, label, value, color in boxes:
            canvas.create_rectangle(x1, y1, x2, y2, fill=Theme.BG_SECONDARY, outline=color, width=2)
            canvas.create_text((x1+x2)//2, (y1+y2)//2 - 10, text=label, font=("Segoe UI", 10, "bold"), fill=text_color)
            canvas.create_text((x1+x2)//2, (y1+y2)//2 + 12, text=value, font=("Segoe UI", 10), fill=color)
        
        # Wires
        if phase == "single":
            canvas.create_line(160, 100, 220, 100, fill=red, width=3)
            canvas.create_line(330, 100, 390, 100, fill=red, width=3)
            canvas.create_line(445, 160, 445, 220, fill=red, width=3)
            
            canvas.create_line(160, 120, 220, 120, fill=gray, width=3)
            canvas.create_line(330, 120, 390, 120, fill=gray, width=3)
            canvas.create_line(425, 160, 425, 220, fill=gray, width=3)
            
            canvas.create_line(160, 140, 220, 140, fill=green, width=3)
            canvas.create_line(330, 140, 360, 140, fill=green, width=3)
            canvas.create_line(360, 140, 360, 270, fill=green, width=3)
            canvas.create_line(330, 270, 390, 270, fill=green, width=3)
        else:
            canvas.create_line(160, 95, 220, 95, fill=red, width=3)
            canvas.create_line(330, 95, 390, 95, fill=red, width=3)
            canvas.create_line(460, 160, 460, 220, fill=red, width=3)
            
            canvas.create_line(160, 115, 220, 115, fill=yellow, width=3)
            canvas.create_line(330, 115, 390, 115, fill=yellow, width=3)
            canvas.create_line(445, 160, 445, 220, fill=yellow, width=3)
            
            canvas.create_line(160, 135, 220, 135, fill=blue, width=3)
            canvas.create_line(330, 135, 390, 135, fill=blue, width=3)
            canvas.create_line(430, 160, 430, 220, fill=blue, width=3)
            
            canvas.create_line(160, 155, 220, 155, fill=green, width=3)
            canvas.create_line(330, 155, 360, 155, fill=green, width=3)
            canvas.create_line(360, 155, 360, 270, fill=green, width=3)
            canvas.create_line(330, 270, 390, 270, fill=green, width=3)
        
        # Legend
        if phase == "single":
            legend = [("Hot", red, 150), ("Neutral", gray, 280), ("Ground", green, 410)]
        else:
            legend = [("Phase A", red, 100), ("Phase B", yellow, 220), ("Phase C", blue, 340), ("Ground", green, 460)]
        
        for label, color, x in legend:
            canvas.create_line(x, 360, x+30, 360, fill=color, width=4)
            canvas.create_text(x+40, 360, text=label, font=("Segoe UI", 10), fill=text_color, anchor="w")
    
    def _build_safety_tab(self):
        ctk.CTkLabel(self.tab_content, text="Safety & Compliance Checklist",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 15))
        
        for category, items in SAFETY_CHECKLIST.items():
            card = ctk.CTkFrame(self.tab_content, fg_color=Theme.BG_CARD, corner_radius=12)
            card.pack(fill="x", pady=(0, 12))
            
            ctk.CTkLabel(card, text=category, font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=Theme.TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(15, 10))
            
            for item in items:
                if item not in self.checklist_vars:
                    self.checklist_vars[item] = ctk.BooleanVar()
                
                ctk.CTkCheckBox(card, text=item, variable=self.checklist_vars[item],
                               font=ctk.CTkFont(size=12), fg_color=Theme.BLUE,
                               hover_color=Theme.BLUE_DARK).pack(anchor="w", padx=18, pady=4)
            
            ctk.CTkFrame(card, height=10, fg_color="transparent").pack()
    
    def _build_report_tab(self):
        ctk.CTkLabel(self.tab_content, text="Report Configuration",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 15))
        
        form = ctk.CTkFrame(self.tab_content, fg_color=Theme.BG_CARD, corner_radius=12)
        form.pack(fill="x")
        
        form_inner = ctk.CTkFrame(form, fg_color="transparent")
        form_inner.pack(fill="x", padx=20, pady=20)
        
        fields = [
            ("project_name", "Project Name *"),
            ("project_address", "Address"),
            ("contractor", "Contractor"),
            ("electrician", "Electrician"),
            ("license_number", "License #"),
        ]
        
        for field_id, label in fields:
            ctk.CTkLabel(form_inner, text=label, font=ctk.CTkFont(size=11),
                        text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(10, 4))
            ctk.CTkEntry(form_inner, textvariable=self.project_info[field_id],
                        height=38, fg_color=Theme.BG_SECONDARY).pack(fill="x")
    
    def _reset_selection(self):
        self.selected_phase = None
        self.selected_power = None
        self.current_specs = None
        
        for card in self.phase_buttons.values():
            card.configure(border_color=Theme.BORDER, fg_color=Theme.BG_CARD)
        for btn in self.power_buttons.values():
            btn.configure(border_color=Theme.BORDER, fg_color=Theme.BG_CARD)
        
        self.results_frame.pack_forget()
    
    def _save_report(self):
        if not self.current_specs:
            self._toast("Please select a configuration first", "warning")
            return
        
        # Gather data
        specs = self.current_specs
        data = {
            'report_id': hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            'project_name': self.project_info["project_name"].get() or "Untitled Project",
            'project_address': self.project_info["project_address"].get(),
            'contractor': self.project_info["contractor"].get(),
            'electrician': self.project_info["electrician"].get(),
            'license_number': self.project_info["license_number"].get(),
            'phase_type': self.selected_phase,
            'power_rating': self.selected_power,
            'specs': {
                'voltage': specs.voltage,
                'amperage': specs.amperage,
                'wire_gauge': specs.wire_gauge,
                'neutral_wire': specs.neutral_wire,
                'ground_wire': specs.ground_wire,
                'conduit_size': specs.conduit_size,
                'breaker_size': specs.breaker_size,
                'receptacle': specs.receptacle,
            },
            'specs_notes': specs.notes,
            'loads': self.loads,
            'checklist': {k: v.get() for k, v in self.checklist_vars.items()},
        }
        
        # Generate filename
        safe_name = "".join(c for c in data['project_name'] if c.isalnum() or c in ' -_').strip()[:40]
        safe_name = safe_name.replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_name}_{data['phase_type']}_{data['power_rating']}kW_{timestamp}.pdf"
        pdf_path = str(self.reports_dir / filename)
        
        # Generate PDF
        self._toast("Generating PDF...", "info")
        if not self.pdf.generate(pdf_path, data):
            self._toast("Failed to generate PDF", "error")
            return
        
        # Save to database
        report = SavedReport(
            id=data['report_id'],
            project_name=data['project_name'],
            phase_type=data['phase_type'],
            power_rating=data['power_rating'],
            status="completed",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            project_address=data['project_address'],
            contractor=data['contractor'],
            electrician=data['electrician'],
            license_number=data['license_number'],
            checklist_data=json.dumps(data['checklist']),
            load_data=json.dumps(data['loads']),
            pdf_path=pdf_path
        )
        
        self.db.save_report(report)
        self._toast("Report saved successfully!", "success")
        
        # Open PDF
        try:
            if sys.platform == 'win32':
                os.startfile(pdf_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', pdf_path])
            else:
                subprocess.run(['xdg-open', pdf_path])
        except Exception as e:
            self._toast(f"Could not open PDF: {e}", "warning")
    
    # =========================================================================
    # SUPPORT PAGE
    # =========================================================================
    
    def _build_support_page(self):
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent",
                                      scrollbar_button_color=Theme.BORDER)
        self.pages["support"] = page
        
        content = ctk.CTkFrame(page, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)
        
        ctk.CTkLabel(content, text="Support Center", font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(content, text="Frequently asked questions and troubleshooting",
                    font=ctk.CTkFont(size=13), text_color=Theme.TEXT_SECONDARY).pack(anchor="w", pady=(0, 25))
        
        for faq in FAQ_DATABASE:
            card = ctk.CTkFrame(content, fg_color=Theme.BG_CARD, corner_radius=12)
            card.pack(fill="x", pady=(0, 12))
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=18)
            
            ctk.CTkLabel(inner, text=faq["category"].upper(), font=ctk.CTkFont(size=10),
                        text_color=Theme.BLUE, fg_color=Theme.BLUE_BG,
                        corner_radius=4).pack(anchor="w", ipadx=8, ipady=2)
            ctk.CTkLabel(inner, text=faq["question"], font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=Theme.TEXT_PRIMARY).pack(anchor="w", pady=(10, 4))
            ctk.CTkLabel(inner, text=faq["answer"], font=ctk.CTkFont(size=12),
                        text_color=Theme.TEXT_SECONDARY, wraplength=700).pack(anchor="w")
    
    # =========================================================================
    # REPORTS PAGE
    # =========================================================================
    
    def _build_reports_page(self):
        page = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent",
                                      scrollbar_button_color=Theme.BORDER)
        self.pages["reports"] = page
        
        self.reports_content = ctk.CTkFrame(page, fg_color="transparent")
        self.reports_content.pack(fill="both", expand=True, padx=40, pady=30)
    
    def _refresh_reports(self):
        for widget in self.reports_content.winfo_children():
            widget.destroy()
        
        header = ctk.CTkFrame(self.reports_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="Reports", font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=Theme.TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(header, text="📁 Open Folder", font=ctk.CTkFont(size=12),
                     fg_color=Theme.BG_CARD, hover_color=Theme.BG_CARD_HOVER,
                     height=36, corner_radius=8, command=self._open_reports_folder).pack(side="right")
        
        reports = self.db.get_reports(limit=20)
        
        if not reports:
            empty = ctk.CTkFrame(self.reports_content, fg_color=Theme.BG_CARD, corner_radius=12)
            empty.pack(fill="x", pady=50)
            ctk.CTkLabel(empty, text="No reports yet", font=ctk.CTkFont(size=16),
                        text_color=Theme.TEXT_MUTED).pack(pady=40)
            return
        
        for report in reports:
            card = ctk.CTkFrame(self.reports_content, fg_color=Theme.BG_CARD, corner_radius=12)
            card.pack(fill="x", pady=(0, 10))
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=15)
            
            # Status dot
            ctk.CTkFrame(inner, width=10, height=10, fg_color=Theme.GREEN,
                        corner_radius=5).pack(side="left")
            
            # Info
            info = ctk.CTkFrame(inner, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=(12, 0))
            
            ctk.CTkLabel(info, text=report.project_name or "Untitled",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=Theme.TEXT_PRIMARY).pack(anchor="w")
            
            phase = "Single Phase" if report.phase_type == "single" else "Three Phase"
            ctk.CTkLabel(info, text=f"{phase} • {report.power_rating} kW",
                        font=ctk.CTkFont(size=12),
                        text_color=Theme.TEXT_SECONDARY).pack(anchor="w")
            
            # Date
            try:
                date = datetime.fromisoformat(report.created_at).strftime("%b %d, %Y")
            except:
                date = "N/A"
            ctk.CTkLabel(inner, text=date, font=ctk.CTkFont(size=11),
                        text_color=Theme.TEXT_MUTED).pack(side="right", padx=(0, 15))
            
            # Open button
            if report.pdf_path and os.path.exists(report.pdf_path):
                ctk.CTkButton(inner, text="Open", width=70, height=32,
                             font=ctk.CTkFont(size=11), fg_color=Theme.BLUE,
                             hover_color=Theme.BLUE_DARK, corner_radius=6,
                             command=lambda p=report.pdf_path: self._open_pdf(p)).pack(side="right")
    
    def _open_pdf(self, path: str):
        try:
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', path])
            else:
                subprocess.run(['xdg-open', path])
        except Exception as e:
            self._toast(f"Could not open: {e}", "error")
    
    def _open_reports_folder(self):
        try:
            if sys.platform == 'win32':
                os.startfile(str(self.reports_dir))
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(self.reports_dir)])
            else:
                subprocess.run(['xdg-open', str(self.reports_dir)])
        except Exception as e:
            self._toast(f"Could not open folder: {e}", "error")


# =============================================================================
# MAIN
# =============================================================================

def main():
    app = GeneratorSpecsApp()
    app.mainloop()


if __name__ == "__main__":
    main()