import { useState } from "react";
import type { SearchRequest } from "../types/lead";

interface SearchFormProps {
  onSearch: (request: SearchRequest) => void;
  isLoading: boolean;
}

interface SegmentDefaults {
  industry: string;
  keywords: string;
  roles: string;
}

const SEGMENT_DEFAULTS: Partial<Record<string, SegmentDefaults>> = {
  "Engineering Colleges": {
    industry: "Education",
    keywords: "placement, employability, coding assessment",
    roles: "Training and Placement Officer, Placement Director",
  },
  Universities: {
    industry: "Education",
    keywords: "placement, career services, campus hiring",
    roles: "Director of Career Services, Placement Officer",
  },
  "Technical Institutes": {
    industry: "Education",
    keywords: "placement, employability, technical training",
    roles: "Placement Director, Career Services Head",
  },
  "Professional Training Institutes": {
    industry: "Education",
    keywords: "corporate training, certification, skill assessment",
    roles: "Head of Training, Program Director",
  },
  "EdTech Organizations": {
    industry: "Education Technology",
    keywords: "online learning, assessments, talent acquisition",
    roles: "Head of Talent Acquisition, HR Director",
  },
  "Skill Development Organizations": {
    industry: "Education",
    keywords: "skill development, vocational training, assessments",
    roles: "Head of Training, Placement Coordinator",
  },
  "Companies / Workforce Organizations": {
    industry: "Recruitment",
    keywords: "hiring, candidate assessment, workforce development",
    roles: "HR Manager, Talent Acquisition Lead",
  },
};

const TARGET_SEGMENTS = Object.keys(SEGMENT_DEFAULTS);

export const INDIAN_STATES = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
  "Andaman and Nicobar Islands",
  "Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi",
  "Jammu and Kashmir",
  "Ladakh",
  "Lakshadweep",
  "Puducherry",
];

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const initialSegment = TARGET_SEGMENTS[0];
  const initialDefaults = SEGMENT_DEFAULTS[initialSegment];
  const [targetSegment, setTargetSegment] = useState(initialSegment);
  const [industry, setIndustry] = useState(initialDefaults?.industry ?? "Education");
  const [location, setLocation] = useState("India");
  const [state, setState] = useState("");
  const [keywords, setKeywords] = useState(initialDefaults?.keywords ?? "");
  const [roles, setRoles] = useState(initialDefaults?.roles ?? "");

  const handleSegmentChange = (segment: string) => {
    setTargetSegment(segment);
    const defaults = SEGMENT_DEFAULTS[segment];
    if (defaults) {
      setIndustry(defaults.industry);
      setKeywords(defaults.keywords);
      setRoles(defaults.roles);
    }
  };

  const [limit, setLimit] = useState(20);
  const [minRelevanceScore, setMinRelevanceScore] = useState(60);
  const [requireContactInfo, setRequireContactInfo] = useState(false);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSearch({
      target_segment: targetSegment,
      industry: industry || undefined,
      location: location || undefined,
      state: state || undefined,
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
      require_contact_info: requireContactInfo,
    });
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>
          Target Segment
          <select value={targetSegment} onChange={(e) => handleSegmentChange(e.target.value)}>
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
        <label>
          State
          <select value={state} onChange={(e) => setState(e.target.value)}>
            <option value="">All States</option>
            {INDIAN_STATES.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
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
      <div className="form-row">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={requireContactInfo}
            onChange={(e) => setRequireContactInfo(e.target.checked)}
          />
          Only show leads with an email or phone number
        </label>
      </div>
    </form>
  );
}
