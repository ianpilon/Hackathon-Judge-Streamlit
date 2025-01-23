import type { NextPage } from 'next';
import Head from 'next/head';
import VideoUpload from '../components/VideoUpload';

const Home: NextPage = () => {
  return (
    <div>
      <Head>
        <title>Video Analysis System</title>
        <meta name="description" content="Analyze videos using AI" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-100">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
              Video Analysis System
            </h1>
            <VideoUpload />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;
