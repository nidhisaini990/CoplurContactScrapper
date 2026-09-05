import { INDIAN_STATES } from "./SearchForm";

interface LeadFiltersProps {
  filterText: string;
  onFilterChange: (value: string) => void;
  selectedState: string;
  onStateChange: (state: string) => void;
  totalCount: number;
  filteredCount: number;
}

export default function LeadFilters({
  filterText,
  onFilterChange,
  selectedState,
  onStateChange,
  totalCount,
  filteredCount,
}: LeadFiltersProps) {
  return (
    <div className="lead-filters">
      <input
        type="text"
        placeholder="Filter by organization, contact, email, location…"
        value={filterText}
        onChange={(e) => onFilterChange(e.target.value)}
      />
      <select
        value={selectedState}
        onChange={(e) => onStateChange(e.target.value)}
        aria-label="Filter by state"
      >
        <option value="">All States</option>
        {INDIAN_STATES.map((st) => (
          <option key={st} value={st}>
            {st}
          </option>
        ))}
      </select>
      <span className="lead-count">
        Showing {filteredCount} of {totalCount} leads
      </span>
    </div>
  );
}
