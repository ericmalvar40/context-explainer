import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ChevronDown, ChevronUp, ExternalLink, Search } from "lucide-react";
import type { ExplainResponse } from "../api/client";

interface Props {
  response: ExplainResponse;
  postText: string;
}

export function ExplanationCard({ response, postText }: Props) {
  const [showSources, setShowSources] = useState(false);
  const [showMeta, setShowMeta] = useState(false);

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="border-b border-gray-100 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">Explanation</h2>
          <p className="mt-1 text-sm text-gray-500 line-clamp-2">{postText}</p>
        </div>

        <ul className="divide-y divide-gray-50 px-6 py-2">
          {response.bullets.map((bullet, i) => (
            <li key={i} className="py-3 flex gap-3">
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                {i + 1}
              </span>
              <div className="prose prose-sm prose-blue max-w-none text-gray-700">
                <ReactMarkdown
                  components={{
                    a: ({ href, children }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 underline decoration-blue-300"
                      >
                        {children}
                      </a>
                    ),
                  }}
                >
                  {bullet}
                </ReactMarkdown>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {response.sources.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <button
            onClick={() => setShowSources(!showSources)}
            className="flex w-full items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <ExternalLink size={16} className="text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                Sources ({response.sources.length})
              </span>
            </div>
            {showSources ? (
              <ChevronUp size={16} className="text-gray-400" />
            ) : (
              <ChevronDown size={16} className="text-gray-400" />
            )}
          </button>

          {showSources && (
            <ul className="border-t border-gray-100 px-6 py-3 space-y-2">
              {response.sources.map((source, i) => (
                <li key={i}>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-start gap-2 rounded-md p-2 text-sm hover:bg-gray-50 transition-colors"
                  >
                    <ExternalLink
                      size={14}
                      className="mt-0.5 shrink-0 text-gray-400"
                    />
                    <div>
                      <p className="font-medium text-gray-800">
                        {source.title}
                      </p>
                      <p className="text-xs text-gray-400 truncate max-w-md">
                        {source.url}
                      </p>
                    </div>
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <button
          onClick={() => setShowMeta(!showMeta)}
          className="flex w-full items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Search size={16} className="text-gray-400" />
            <span className="text-sm font-medium text-gray-700">
              Pipeline details
            </span>
          </div>
          {showMeta ? (
            <ChevronUp size={16} className="text-gray-400" />
          ) : (
            <ChevronDown size={16} className="text-gray-400" />
          )}
        </button>

        {showMeta && (
          <div className="border-t border-gray-100 px-6 py-4 text-sm text-gray-600 space-y-2">
            <p>
              <span className="font-medium">Model:</span>{" "}
              {response.metadata.model}
            </p>
            <p>
              <span className="font-medium">Search queries:</span>
            </p>
            <ul className="list-disc pl-5 space-y-1">
              {response.metadata.search_queries.map((q, i) => (
                <li key={i} className="text-gray-500">
                  {q}
                </li>
              ))}
            </ul>
            <p>
              <span className="font-medium">Results found:</span>{" "}
              {response.metadata.total_results_found} total,{" "}
              {response.metadata.results_after_rerank} after reranking
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
