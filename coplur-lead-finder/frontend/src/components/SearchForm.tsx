import { useState } from "react";
import type { SearchRequest } from "../types/lead";

interface SearchFormProps {
  onSearch: (request: SearchRequest) => void;
  isLoading: boolean;
}

const TARGET_SEGMENTS = [
  "Engineering Colleges",
  "Universities",
  "Technical Institutes",
  "Professional Training Institutes",
  "EdTech Organizations",
  "Skill Development Organizations",
  "Companies / Workforce Organizations",
];

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [targetSegment, setTargetSegment] = useState(TARGET_SEGMENTS[0]);
  const [industry, setIndustry] = useState("Education");
  const [location, setLocation] = useState("India");
  const [keywords, setKeywords] = useState("placement, employability, coding assessment");
  const [roles, setRoles] = useState("Training and Placement Officer, Placement Director");
  const [limit, setLimit] = useState(20);
  const [minRelevanceScore, setMinRelevanceScore] = useState(60);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSearch({
      target_segment: targetSegment,
      industry: industry || undefined,
      location: location || undefined,
      keywords: keywords
        .split(",")
        .map((k) => k.trim())
        .filter(Boolean),
      roles: roles
        .split(",")
        .map((r) => r.trim())
        .filter(Boolean),
      limit,
      min_relevance_score: minRelevanceScore,
    });
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>
          Target Segment
          <select value={targetSegment} onChange={(e) => setTargetSegment(e.target.value)}>
            {TARGET_SEGMENTS.map((segment) => (
              <option key={segment} value={segment}>
                {segment}
              </option>
            ))}
          </select>
        </label>
        <label>
          Industry
          <input value={industry} onChange={(e) => setIndustry(e.target.value)} placeholder="e.g. Education" />
        </label>
        <label>
          Location
          <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. India" />
        </label>
      </div>
      <div className="form-row">
        <label className="wide">
          Keywords (comma separated)
          <input value={keywords} onChange={(e) => setKeywords(e.target.value)} />
        </label>
      </div>
      <div className="form-row">
        <label className="wide">
          Decision Maker Roles (comma separated)
          <input value={roles} onChange={(e) => setRoles(e.target.value)} />
        </label>
      </div>
      <div className="form-row">
        <label>
          Number of Leads
          <input
            type="number"
            min={1}
            max={200}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          />
        </label>
        <label>
          Minimum Relevance Score
          <input
            type="number"
            min={0}
            max={100}
            value={minRelevanceScore}
            onChange={(e) => setMinRelevanceScore(Number(e.target.value))}
          />
        </label>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Searching…" : "Find Potential Leads"}
        </button>
      </div>
    </form>
  );
}
