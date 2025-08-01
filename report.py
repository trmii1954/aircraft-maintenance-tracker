from datetime import datetime, timezone

# from dateutil.relativedelta import relativedelta

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import red, black


from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# Register the font - using built-in fonts instead of external TTF files
# Option 1: Use built-in fonts (no registration needed)
# Option 2: If you have Arial TTF files, update paths to:
# pdfmetrics.registerFont(TTFont('Arial', '/Users/trmii/Desktop/Dropbox/trmPythonProjects/21104316/project/planes/reports/fonts/ARIAL.TTF'))
# pdfmetrics.registerFont(TTFont('Arial-Bold', '/Users/trmii/Desktop/Dropbox/trmPythonProjects/21104316/project/planes/reports/fonts/ARIALBD.TTF'))


custom_styles = {
    "Title": ParagraphStyle(
        name="Title",
        fontName="Helvetica",
        fontSize=24,
        textColor="darkblue",
        alignment=1,  # Center alignment
    ),
    "Subtitle": ParagraphStyle(
        name="Subtitle",
        fontName="Helvetica",
        fontSize=16,
        textColor="green",
        spaceAfter=10,
    ),
    "Subsubtitle": ParagraphStyle(
        name="Subsubtitle",
        fontName="Helvetica",
        fontSize=12,
        textColor="darkblue",
        spaceAfter=2,
        spaceBefore=12,
        leading=18,
        alignment=1,  # Center alignment
    ),
    "BodyText": ParagraphStyle(
        name="BodyText",
        fontName="Helvetica",
        fontSize=12,
        textColor="red",
        spaceBefore=10,
        leftIndent=20,  # Adds a 20-point indent to the left
    ),
}


def pdf_report(self, report_type):
    # Create a PDF object with a filename
    c = SimpleDocTemplate(
        f"{self.folder}/reports/{self.registration} {report_type} Report.pdf",
        pagesize=letter,
    )

    # Content for the PDF
    content = []

    # Add a title
    title = Paragraph(f"{self.registration}", custom_styles["Title"])
    content.append(title)
    content.append(Spacer(1, 20))

    # Add plane profile
    content.append(
        Paragraph(
            f"<font name='Helvetica-Bold'>{self.make} {self.model} with serial {self.serial} and registration {self.registration}.</font>"
        )
    )
    content.append(Paragraph(f"Plane stored in {self.folder}{self.registration}."))
    content.append(Paragraph(f"Systems: {", ".join(list(self.major_systems.keys()))}"))
    content.append(Paragraph(f"Manufacture Date:  {self.manufacture_date}"))
    content.append(
        Paragraph(
            f"Current Hours from Google sheet, ID ending with {self.google_sheet_id[-6:]}."
        )
    )
    content.append(
        Paragraph(
            f"Day Zero Hours: Hobbs {self.day_zero_hobbs_hours}, Flight {self.day_zero_flight_hours}."
        )
    )
    content.append(
        Paragraph(
            f"Current  Hours: Hobbs {self.hobbs_hours}, Flight {self.flight_hours}."
        )
    )
    content.append(Paragraph(f"Last Flight on {self.last_flight_date}"))
    content.append(Spacer(1, 12))

    # add hours since purchased
    hh = self.hobbs_hours - self.day_zero_hobbs_hours
    fh = self.flight_hours - self.day_zero_flight_hours
    content.append(
        Paragraph(
            f"<font name='Helvetica-Bold'>Hours since day zero (purchase) -- Hobbs: {hh:.1f}, Flight: {fh:.1f}</font>"
        )
    )
    content.append(Spacer(1, 20))

    content.append(
        Paragraph("Major Systems and Their Subsystems", custom_styles["Subtitle"])
    )
    for s in self.major_systems:
        content = content + report_system(self.major_systems[s])

    if report_type in ("all", "configuration"):
        content.append(PageBreak())
        content.append(
            Paragraph(
                "<font size=18 color='green'>Configuration.<br/>Sorted by Last Maintenance Date</font>",
                custom_styles["Subsubtitle"],
            )
        )
        content.append(Spacer(1, 6))
        for s in self.major_systems:
            together = report_system(self.major_systems[s])
            together.append(Spacer(1, 6))
            together = together + report_subsystem(self.major_systems[s])
            together.append(Spacer(1, 16))
            content = content + [KeepTogether(together)]

    if report_type in ("all", "maintenance"):

        content.append(PageBreak())
        content.append(
            Paragraph(
                "<font size= 18 color='green'>Maintenance Status.<br/>Sorted by Maintenance Due Date</font>",
                custom_styles["Subsubtitle"],
            )
        )
        content.append(
            Paragraph(
                "<font size=10 color='lightgrey'>ITIS = Interval Time in Service Interval</font>"
            )
        )
        content.append(Spacer(1, 12))

        for s in self.major_systems:
            together = [
                Paragraph(f"<font size=14 color='blue'>{s.title()} System</font>")
            ]
            together.append(Spacer(1, 12))
            together = together + report_maintenance(
                self.major_systems[s], self.flight_hours
            )
            together.append(Spacer(1, 12))

            content = content + [KeepTogether(together)]

    if report_type in ("all", "log"):
        for s in sorted(self.major_systems):
            content.append(PageBreak())
            content.append(
                Paragraph(
                    f"Major System: <font size=18 color='green'>{s.title()}</font>",
                    custom_styles["Subsubtitle"],
                )
            )
            content.append(Spacer(1, 6))
            content += report_log(self.major_systems[s])
            content.append(
                Paragraph(
                    f"<font size=14 color='brown'>{s.title()} Subsystems Log<br/>(sorted by subsystem)</font>",
                    custom_styles["Subsubtitle"],
                )
            )
            for ss in dict(sorted(self.major_systems[s].subsystems.items())).values():
                together = [
                    Paragraph(f"{ss.subsystem_name}", custom_styles["Subsubtitle"])
                ]
                together = together + report_log(ss)
                content = content + [KeepTogether(together)]

    # Build the PDF
    disclaim = "WARNING: See Logbooks for Definitive Information."
    c.build(
        content,
        onFirstPage=make_header_footer(report_type, disclaim),
        onLaterPages=make_header_footer(report_type, disclaim),
    )

    # Apply metadata after building the document
    c.canv.setAuthor("Tom")
    c.canv.setTitle("Title Metadata")

    print(f"PDF has been created: {report_type.title()} Report")


def report_system(system):
    r = [Paragraph(f"<font color='blue'>{system.subsystem_name} System</font>")]
    r.append(
        Paragraph(
            f"<font name='Helvetica-Bold'>{system.make} {system.model} {system.serial}</font>"
        )
    )
    r.append(
        Paragraph(
            f"<font name='Helvetica-Bold'>Last Major System Maintenance {system.maintenance_date}</font>"
        )
    )
    r.append(
        Paragraph(f"Subsystems: {", ".join(sorted(list(system.subsystems.keys())))}")
    )
    r.append(Spacer(1, 12))
    return r


def report_subsystem(system):

    t = [["Subsystem", "Make", "Model", "Serial Number", "Last Maintenance"]]
    for ss in system.subsystems.keys():
        t.append(
            [
                ss,
                system.subsystems[ss].make,
                system.subsystems[ss].model,
                system.subsystems[ss].serial,
                system.subsystems[ss].maintenance_date,
            ]
        )

    sorted_t = sorted(
        t, key=lambda maintenance_date: maintenance_date[-1], reverse=True
    )
    table = Table(sorted_t)
    style = TableStyle(
        [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.Color(red=0.0, green=0.4, blue=0.8),
            ),  # Header row background
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold font for headers
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),  # Padding for headers
            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black,
            ),  # Grid lines for the entire table
        ]
    )
    # Apply the style to the table
    table.setStyle(style)
    return [table]


def report_log(subsystem):

    t = [list(subsystem.action_log[0].keys())]
    for d in subsystem.action_log:
        t.append(list(d.values()))
        # print(d.values())
        # print(d)
        # print()

    table = Table(t)
    style = TableStyle(
        [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.Color(red=0.0, green=0.4, blue=0.8),
            ),  # Header row background
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold font for headers
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),  # Padding for headers
            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black,
            ),  # Grid lines for the entire table
        ]
    )
    # Apply the style to the table
    table.setStyle(style)
    return [table]


def report_maintenance(major_system, flight_hours):

    # get the data for a major system, one row per subsystem
    t = maintenance_table(major_system, flight_hours)

    # make a table for reportlab
    table = Table(t)
    style = TableStyle(
        [
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.Color(red=0.0, green=0.4, blue=0.8),
            ),  # Header row background
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # Bold font for headers
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),  # Padding for headers
            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black,
            ),  # Grid lines for the entire table
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),  # Align column 3 to the left
        ]
    )
    # Apply the style to the table
    table.setStyle(style)

    return [table]


#### make a funtion that returns the row
#### argument is the subsystem
### a method of subsystem
### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def maintenance_table(system, flight_hours):
    """
    Returns a row for each subsystem with a calculated "Due At/On" Value (if able)
    ["Subsystem","Last Maint","@Flt Hours","Interval","Interval TIS","Remaining","Due At/On"]
    """
    table: list = [system.maintenance_status(flight_hours)]
    table[0][0] = "Major System: " + table[0][0]
    for ss in system.subsystems.keys():
        table.append(system.subsystems[ss].maintenance_status(flight_hours))

    # sort on Due Date or Time
    sorted_table = sorted(
        table, key=lambda x: make_sort_key(x[6])
    )  # x[6] is due_in_at_s
    hdr = [
        "Subsystem",
        "Last Maint",
        "@Flt Hours",
        "Interval",
        "Interval TIS",
        "Remaining",
        "Due At/On",
    ]

    #  # Process the table to add formatting
    #     for row in table:
    #         if len(row) > 5 and isinstance(row[5], str) and '-' in row[5]:
    #             # Convert to Paragraph with red color
    #             row[5] = Paragraph(f'<font color="red">{row[5]}</font>')

    return [hdr] + sorted_table


def make_sort_key(due) -> float:
    """
    Key to sort the maintenance subsystems by when due.
    Due can be  8601 date, hours or ''  Empty string for subsystems which have not specific interval.
    Make a the sort key a float
    """
    if isinstance(due, str):
        if due == "":
            return float(99999999)  # force systems w/o due date to last in the sort
        else:
            return float(due)
    else:
        return float(due.strftime("%Y%m%d"))


# Custom header and footer function
def make_header_footer(report_type, disclaim):
    def header_footer(canvas, doc):
        # Add a header
        canvas.saveState()
        canvas.setFont("Helvetica", 12)
        canvas.drawString(50, doc.pagesize[1] - 50, f"{report_type.title()} Report")
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(red)
        canvas.drawString(
            doc.pagesize[0] - 250, doc.pagesize[1] - 40, f"{disclaim.title()}"
        )
        canvas.setFillColor(black)

        # Add a footer
        canvas.setFont("Helvetica", 10)
        canvas.drawString(0.5 * inch, 0.5 * inch, f"Page {doc.page}")
        canvas.drawRightString(
            8.0 * inch, 0.5 * inch, f"{datetime.now(timezone.utc)} UTC"
        )
        canvas.restoreState()

    return header_footer


def main(): ...


if __name__ == "__main__":
    main()
