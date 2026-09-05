interface LeadFiltersProps {
  filterText: string;
  onFilterChange: (value: string) => void;
  totalCount: number;
  filteredCount: number;
}

export default function LeadFilters({ filterText, onFilterChange, totalCount, filteredCount }: LeadFiltersProps) {
  return (
    <div className="lead-filters">
      <input
        type="text"
        placeholder="Filter by organization, contact, email, location…"
        value={filterText}
        onChange={(e) => onFilterChange(e.target.value)}
      />
      <span className="lead-count">
        Showing {filteredCount} of {totalCount} leads
      </span>
    </div>
  );
}
