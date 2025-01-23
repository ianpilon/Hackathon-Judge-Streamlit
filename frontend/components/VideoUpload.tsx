import { useState } from 'react';
import axios from 'axios';

const VideoUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a video file');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/analyze`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setResults(response.data);
    } catch (err) {
      setError('Error analyzing video. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            className="w-full"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full py-2 px-4 rounded-md text-white ${
            loading
              ? 'bg-gray-400'
              : 'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          {loading ? 'Analyzing...' : 'Analyze Video'}
        </button>

        {error && (
          <div className="text-red-500 mt-2">{error}</div>
        )}

        {results && (
          <div className="mt-6 space-y-4">
            <h2 className="text-xl font-bold">Analysis Results</h2>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold">Visual Analysis</h3>
              <pre className="mt-2 whitespace-pre-wrap">
                {JSON.stringify(results.visual_analysis, null, 2)}
              </pre>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold">Audio Analysis</h3>
              <pre className="mt-2 whitespace-pre-wrap">
                {JSON.stringify(results.audio_analysis, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default VideoUpload;
