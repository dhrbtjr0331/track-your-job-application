import React from 'react';
import { ApolloProvider } from '@apollo/client';
import { QueryClient, QueryClientProvider } from 'react-query';
import { apolloClient } from './services/apollo';
import Dashboard from './components/Dashboard/Dashboard';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <ApolloProvider client={apolloClient}>
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <header className="py-8">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  Job Application Tracker
                </h1>
                <p className="text-xl text-gray-600">
                  AI-powered tracking of your job applications from Gmail
                </p>
              </div>
            </header>
            
            <main className="pb-16">
              <Dashboard />
            </main>
            
            <footer className="border-t border-gray-200 py-8 text-center text-gray-500">
              <p>&copy; 2024 Job Application Tracker. All rights reserved.</p>
            </footer>
          </div>
        </div>
      </QueryClientProvider>
    </ApolloProvider>
  );
}

export default App;
