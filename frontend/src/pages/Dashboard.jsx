import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { Book, CheckCircle, Clock, PauseCircle, Eye, Edit, Download, RefreshCw } from 'lucide-react';

import { bookAPI } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { format } from 'date-fns';

const Dashboard = () => {
  const { data: books = [], isLoading, error, refetch } = useQuery('books', () => bookAPI.getBooks());

  // Calculate stats
  const stats = {
    total: books.length,
    completed: books.filter(book => book.status === 'completed').length,
    inProgress: books.filter(book => ['generating_chapters', 'compiling', 'in_progress'].includes(book.status)).length,
    paused: books.filter(book => book.status === 'paused').length,
  };

  // Get progress percentage based on status
  const getProgress = (book) => {
    switch (book.status) {
      case 'completed':
        return 100;
      case 'compiling':
        return 90;
      case 'reviewing_chapters':
        return 75;
      case 'generating_chapters':
        return 50;
      case 'review_outline':
        return 25;
      case 'draft_outline':
        return 10;
      default:
        return 0;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return format(new Date(dateString), 'MMM dd, yyyy');
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" text="Loading books..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <Book className="w-16 h-16 mx-auto mb-4" />
          <p className="text-lg font-medium">Failed to load books</p>
          <p className="text-sm">Please try again later</p>
        </div>
        <button
          onClick={() => refetch()}
          className="btn btn-primary"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Manage your automated book generation projects</p>
        </div>
        <Link to="/books/new" className="btn btn-primary">
          <Book className="w-4 h-4 mr-2" />
          Create New Book
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-full">
              <Book className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Total Books</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-full">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-full">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">{stats.inProgress}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="p-3 bg-red-100 rounded-full">
              <PauseCircle className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Paused</p>
              <p className="text-2xl font-bold text-gray-900">{stats.paused}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Books Table */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Your Books</h2>
        </div>
        
        {books.length === 0 ? (
          <div className="text-center py-12">
            <Book className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No books yet</h3>
            <p className="text-gray-600 mb-4">Create your first book to get started</p>
            <Link to="/books/new" className="btn btn-primary">
              <Book className="w-4 h-4 mr-2" />
              Create Book
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {books.map((book) => {
                  const progress = getProgress(book);
                  return (
                    <tr key={book.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {book.title}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={book.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${progress}%` }}
                            />
                          </div>
                          <span className="ml-2 text-sm text-gray-600">
                            {progress}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(book.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <Link
                            to={`/books/${book.id}`}
                            className="text-primary-600 hover:text-primary-900 inline-flex items-center"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Link>
                          <Link
                            to={`/books/${book.id}`}
                            className="text-indigo-600 hover:text-indigo-900 inline-flex items-center"
                          >
                            <Edit className="w-4 h-4 mr-1" />
                            Edit
                          </Link>
                          {book.status === 'completed' && (
                            <button
                              onClick={() => handleExport(book.id)}
                              className="text-green-600 hover:text-green-900 inline-flex items-center"
                            >
                              <Download className="w-4 h-4 mr-1" />
                              Export
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

// Export handler (you can expand this with the actual export hook)
const handleExport = async (bookId) => {
  try {
    // This would use the useExportBook hook in a real component
    console.log('Exporting book:', bookId);
  } catch (error) {
    console.error('Export failed:', error);
  }
};

export default Dashboard;
