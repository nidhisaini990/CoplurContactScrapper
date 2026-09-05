import { useMemo, useState } from "react";
import SearchForm from "./components/SearchForm";
import LeadsTable from "./components/LeadsTable";
import LeadFilters from "./components/LeadFilters";
import LoadingState from "./components/LoadingState";
import ExportButton from "./components/ExportButton";
import { searchLeads } from "./services/api";
import type { Lead, SearchRequest } from "./types/lead";
import "./App.css";

const leadKey = (lead: Lead) => `${lead.organization_name}::${lead.website ?? ""}::${lead.source_url ?? ""}`;

function App() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [filterText, setFilterText] = useState("");
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());

  const handleSearch = async (request: SearchRequest) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const response = await searchLeads(request);
      const sorted = [...response.leads].sort((a, b) => b.relevance_score - a.relevance_score);
      setLeads(sorted);
      setSelectedKeys(new Set(sorted.map(leadKey)));
    } catch {
      setError("Something went wrong while searching for leads. Please try again.");
      setLeads([]);
      setSelectedKeys(new Set());
    } finally {
      setIsLoading(false);
    }
  };

  const filteredLeads = useMemo(() => {
    const query = filterText.trim().toLowerCase();
    if (!query) return leads;
    return leads.filter((lead) =>
      [
        lead.organization_name,
        lead.contact_name,
        lead.business_email,
        lead.city,
        lead.state,
        lead.country,
      ]
        .filter(Boolean)
        .some((value) => value!.toLowerCase().includes(query))
    );
  }, [leads, filterText]);

  const handleToggleSelect = (index: number) => {
    const key = leadKey(filteredLeads[index]);
    setSelectedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const allFilteredSelected = filteredLeads.length > 0 && filteredLeads.every((lead) => selectedKeys.has(leadKey(lead)));

  const handleToggleSelectAll = () => {
    setSelectedKeys((prev) => {
      const next = new Set(prev);
      if (allFilteredSelected) {
        filteredLeads.forEach((lead) => next.delete(leadKey(lead)));
      } else {
        filteredLeads.forEach((lead) => next.add(leadKey(lead)));
      }
      return next;
    });
  };

  const handleDelete = (index: number) => {
    const lead = filteredLeads[index];
    const key = leadKey(lead);
    setLeads((prev) => prev.filter((l) => leadKey(l) !== key));
    setSelectedKeys((prev) => {
      const next = new Set(prev);
      next.delete(key);
      return next;
    });
  };

  const selectedLeads = filteredLeads.filter((lead) => selectedKeys.has(leadKey(lead)));

  return (
    <div className="app">
      <header className="app-header">
        <h1>Coplur Lead Finder</h1>
        <p>Find potential customers and export contact details</p>
      </header>

      <SearchForm onSearch={handleSearch} isLoading={isLoading} />

      {isLoading && <LoadingState />}
      {error && <p className="error-banner">{error}</p>}

      {!isLoading && hasSearched && !error && (
        <section className="results-section">
          <div className="results-toolbar">
            <LeadFilters
              filterText={filterText}
              onFilterChange={setFilterText}
              totalCount={leads.length}
              filteredCount={filteredLeads.length}
            />
            <ExportButton leads={selectedLeads} />
          </div>
          <LeadsTable
            leads={filteredLeads}
            isSelected={(lead) => selectedKeys.has(leadKey(lead))}
            onToggleSelect={handleToggleSelect}
            onToggleSelectAll={handleToggleSelectAll}
            onDelete={handleDelete}
            allSelected={allFilteredSelected}
          />
        </section>
      )}
    </div>
  );
}

export default App;
