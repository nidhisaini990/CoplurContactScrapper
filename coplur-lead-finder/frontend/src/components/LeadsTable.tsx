import type { Lead } from "../types/lead";

interface LeadsTableProps {
  leads: Lead[];
  isSelected: (lead: Lead) => boolean;
  onToggleSelect: (index: number) => void;
  onToggleSelectAll: () => void;
  onDelete: (index: number) => void;
  allSelected: boolean;
}

export default function LeadsTable({
  leads,
  isSelected,
  onToggleSelect,
  onToggleSelectAll,
  onDelete,
  allSelected,
}: LeadsTableProps) {
  if (leads.length === 0) {
    return <p className="empty-state">No leads found. Try adjusting your search criteria.</p>;
  }

  return (
    <div className="leads-table-wrapper">
      <table className="leads-table">
        <thead>
          <tr>
            <th>
              <input type="checkbox" checked={allSelected} onChange={onToggleSelectAll} />
            </th>
            <th>Organization</th>
            <th>Contact</th>
            <th>Designation</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Location</th>
            <th>Score</th>
            <th>Reason</th>
            <th>Source</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead, index) => (
            <tr key={`${lead.organization_name}-${index}`}>
              <td>
                <input
                  type="checkbox"
                  checked={isSelected(lead)}
                  onChange={() => onToggleSelect(index)}
                />
              </td>
              <td>
                {lead.website ? (
                  <a href={lead.website} target="_blank" rel="noreferrer">
                    {lead.organization_name}
                  </a>
                ) : (
                  lead.organization_name
                )}
              </td>
              <td>{lead.contact_name || "—"}</td>
              <td>{lead.designation || "—"}</td>
              <td>{lead.business_email || "—"}</td>
              <td>{lead.business_phone || "—"}</td>
              <td>{[lead.city, lead.state, lead.country].filter(Boolean).join(", ") || "—"}</td>
              <td>{lead.relevance_score}</td>
              <td className="reason-cell" title={lead.relevance_reason || ""}>
                {lead.relevance_reason || "—"}
              </td>
              <td>
                {lead.source_url ? (
                  <a href={lead.source_url} target="_blank" rel="noreferrer">
                    Link
                  </a>
                ) : (
                  "—"
                )}
              </td>
              <td>
                <button className="delete-btn" onClick={() => onDelete(index)} aria-label="Delete lead">
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
