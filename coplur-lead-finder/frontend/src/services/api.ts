import type { Lead, SearchRequest, SearchResponse } from "../types/lead";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function searchLeads(request: SearchRequest): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/leads/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Search failed with status ${response.status}`);
  }
  return response.json();
}

export async function exportLeadsToCsv(leads: Lead[]): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/leads/export`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ leads }),
  });
  if (!response.ok) {
    throw new Error(`Export failed with status ${response.status}`);
  }
  return response.blob();
}
