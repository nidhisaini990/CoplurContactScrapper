import { useState } from "react";
import type { Lead } from "../types/lead";
import { exportLeadsToCsv } from "../services/api";

interface ExportButtonProps {
  leads: Lead[];
}

export default function ExportButton({ leads }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setError(null);
    setIsExporting(true);
    try {
      const blob = await exportLeadsToCsv(leads);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "coplur_leads.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to export leads to CSV", err);
      setError("Failed to export CSV. Please try again.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="export-button">
      <button onClick={handleExport} disabled={leads.length === 0 || isExporting}>
        {isExporting ? "Exporting…" : `Export Selected to CSV (${leads.length})`}
      </button>
      {error && <span className="error-text">{error}</span>}
    </div>
  );
}
