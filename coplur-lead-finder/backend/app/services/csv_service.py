"""Generates a clean, Excel-friendly CSV export from a list of leads."""
import csv
import io

from app.models.lead import Lead
from app.utils.text_cleaner import sanitize_csv_field

CSV_COLUMNS = [
    "Organization Name",
    "Website",
    "Industry",
    "Organization Type",
    "City",
    "State",
    "Country",
    "Contact Name",
    "Designation",
    "Department",
    "Business Email",
    "Business Phone",
    "LinkedIn URL",
    "Organization LinkedIn",
    "Source URL",
    "Relevance Score",
    "Why Relevant",
]


def leads_to_csv(leads: list[Lead]) -> str:
    """Serialize leads into a UTF-8 CSV string with sanitized fields."""
    buffer = io.StringIO()
    # BOM helps Excel detect UTF-8 encoding correctly.
    buffer.write("\ufeff")
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)

    for lead in leads:
        writer.writerow(
            [
                sanitize_csv_field(lead.organization_name),
                sanitize_csv_field(lead.website),
                sanitize_csv_field(lead.industry),
                sanitize_csv_field(lead.organization_type),
                sanitize_csv_field(lead.city),
                sanitize_csv_field(lead.state),
                sanitize_csv_field(lead.country),
                sanitize_csv_field(lead.contact_name),
                sanitize_csv_field(lead.designation),
                sanitize_csv_field(lead.department),
                sanitize_csv_field(lead.business_email),
                sanitize_csv_field(lead.business_phone),
                sanitize_csv_field(lead.linkedin_url),
                sanitize_csv_field(lead.organization_linkedin),
                sanitize_csv_field(lead.source_url),
                lead.relevance_score,
                sanitize_csv_field(lead.relevance_reason),
            ]
        )

    return buffer.getvalue()
