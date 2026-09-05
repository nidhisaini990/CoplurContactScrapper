export interface Lead {
  organization_name: string;
  website?: string | null;
  industry?: string | null;
  organization_type?: string | null;

  city?: string | null;
  state?: string | null;
  country?: string | null;

  contact_name?: string | null;
  designation?: string | null;
  department?: string | null;

  business_email?: string | null;
  business_phone?: string | null;

  linkedin_url?: string | null;
  organization_linkedin?: string | null;

  source_url?: string | null;

  relevance_score: number;
  relevance_reason?: string | null;
}

export interface SearchRequest {
  target_segment: string;
  industry?: string;
  location?: string;
  country?: string;
  keywords: string[];
  roles: string[];
  limit: number;
  min_relevance_score: number;
}

export interface SearchResponse {
  total: number;
  leads: Lead[];
}
