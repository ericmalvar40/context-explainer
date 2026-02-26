import { useState } from "react";
import { PostInput } from "./components/PostInput";
import { ExplanationCard } from "./components/ExplanationCard";
import { explainPost, type ExplainResponse } from "./api/client";

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<ExplainResponse | null>(null);
  const [currentPost, setCurrentPost] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (postText: string, imageUrl?: string) => {
    setIsLoading(true);
    setError(null);
    setCurrentPost(postText);
    setResponse(null);

    try {
      const result = await explainPost({
        post_text: postText,
        post_image_url: imageUrl ?? null,
      });
      setResponse(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to explain post"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-2xl mx-auto px-4 py-12">
        <header className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Contextual Post Explainer
          </h1>
          <p className="text-gray-600">
            Paste a social media post and get context-aware explanations powered
            by AI
          </p>
        </header>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <PostInput onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8">
            {error}
          </div>
        )}

        {isLoading && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8 animate-pulse">
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-5/6" />
              <div className="h-4 bg-gray-200 rounded w-2/3" />
            </div>
            <p className="mt-4 text-sm text-gray-400 text-center">
              Analyzing post, searching the web, and synthesizing context...
            </p>
          </div>
        )}

        {response && (
          <ExplanationCard response={response} postText={currentPost} />
        )}

        <footer className="mt-12 text-center text-sm text-gray-400">
          Built with FastAPI, React, and OpenAI
        </footer>
      </div>
    </div>
  );
}

export default App;
