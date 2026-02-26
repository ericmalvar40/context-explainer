import axios from "axios";

export interface Source {
  title: string;
  url: string;
}

export interface ExplainResponse {
  bullets: string[];
  sources: Source[];
  metadata: {
    search_queries: string[];
    model: string;
    total_results_found: number;
    results_after_rerank: number;
  };
}

interface ExplainRequest {
  post_text: string;
  post_image_url: string | null;
}

const api = axios.create({ baseURL: "/" });

export async function explainPost(
  request: ExplainRequest
): Promise<ExplainResponse> {
  const { data } = await api.post<ExplainResponse>("/api/explain", request);
  return data;
}
