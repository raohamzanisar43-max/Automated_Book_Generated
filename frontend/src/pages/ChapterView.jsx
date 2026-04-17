import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation } from 'react-query';
import { useForm } from 'react-hook-form';
import {
  ArrowLeft,
  Edit,
  Save,
  RefreshCw,
  MessageSquare,
  FileText,
  Book,
  Download,
} from 'lucide-react';

import { bookAPI } from '../services/api';
import { useBook, useGenerateChapter } from '../hooks/useBooks';
import LoadingSpinner from '../components/LoadingSpinner';
import StatusBadge from '../components/StatusBadge';
import { format } from 'date-fns';

const ChapterView = () => {
  const { id, chapterNumber } = useParams();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);

  const chapterNumberInt = parseInt(chapterNumber);
  
  const { data: book, isLoading: bookLoading } = useBook(id);
  const { data: chapters = [], isLoading: chaptersLoading } = useBookChapters(id);
  
  const currentChapter = chapters.find(ch => ch.chapter_number === chapterNumberInt);
  const previousChapter = chapters.find(ch => ch.chapter_number === chapterNumberInt - 1);
  const nextChapter = chapters.find(ch => ch.chapter_number === chapterNumberInt + 1);

  const generateChapterMutation = useGenerateChapter();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm();

  const onRegenerateChapter = async (data) => {
    try {
      await generateChapterMutation.mutateAsync({
        bookId: id,
        chapterNumber: chapterNumberInt,
        chapter_notes: data.chapter_notes,
        chapter_notes_status: 'yes',
      });
      setIsEditing(false);
    } catch (error) {
      // Error handled by mutation hook
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return format(new Date(dateString), 'MMM dd, yyyy \'at\' h:mm a');
  };

  if (bookLoading || chaptersLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" text="Loading chapter..." />
      </div>
    );
  }

  if (!book || !currentChapter) {
    return (
      <div className="text-center py-12">
        <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Chapter not found</h3>
        <p className="text-gray-600 mb-4">The chapter you're looking for doesn't exist</p>
        <Link to={`/books/${id}`} className="btn btn-primary">
          Back to Book
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex items-start space-x-4">
          <Link
            to={`/books/${id}`}
            className="text-gray-600 hover:text-gray-900 mt-1"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {currentChapter.title || `Chapter ${chapterNumber}`}
            </h1>
            <div className="flex items-center space-x-4 mt-2">
              <span className="text-sm text-gray-600">
                {book.title}
              </span>
              <span className="text-sm text-gray-500">
                {formatDate(currentChapter.created_at)}
              </span>
              {currentChapter.content && (
                <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                  Generated
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex space-x-2">
          {currentChapter.content && (
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="btn btn-secondary"
            >
              <Edit className="w-4 h-4 mr-2" />
              {isEditing ? 'Cancel' : 'Edit'}
            </button>
          )}
          <button
            onClick={() => {
              reset();
              setIsEditing(true);
            }}
            className="btn btn-primary"
            disabled={generateChapterMutation.isLoading}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Regenerate
          </button>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center card p-4">
        <div className="flex items-center space-x-4">
          {previousChapter && (
            <Link
              to={`/books/${id}/chapters/${previousChapter.chapter_number}`}
              className="flex items-center text-primary-600 hover:text-primary-800"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Chapter {previousChapter.chapter_number}
            </Link>
          )}
        </div>
        
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Book className="w-4 h-4" />
          <span>
            Chapter {chapterNumber} of {chapters.length}
          </span>
        </div>

        <div className="flex items-center space-x-4">
          {nextChapter && (
            <Link
              to={`/books/${id}/chapters/${nextChapter.chapter_number}`}
              className="flex items-center text-primary-600 hover:text-primary-800"
            >
              Chapter {nextChapter.chapter_number}
              <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
            </Link>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          {isEditing ? (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Regenerate Chapter
              </h3>
              <form onSubmit={handleSubmit(onRegenerateChapter)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Feedback Notes
                  </label>
                  <textarea
                    {...register('chapter_notes')}
                    rows={6}
                    className="input"
                    placeholder="Provide feedback on what to improve, change, or add to this chapter..."
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Describe what you'd like to change about this chapter
                  </p>
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setIsEditing(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={generateChapterMutation.isLoading}
                  >
                    {generateChapterMutation.isLoading ? (
                      <>
                        <LoadingSpinner size="small" text="" />
                        Regenerating...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Regenerate Chapter
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Chapter Content</h3>
              
              {currentChapter.content ? (
                <div className="prose max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                    {currentChapter.content}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <FileText className="w-16 h-16 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Chapter not generated yet
                  </h3>
                  <p className="text-gray-600 mb-4">
                    This chapter hasn't been generated yet
                  </p>
                  <button
                    onClick={() => {
                      reset();
                      setIsEditing(true);
                    }}
                    className="btn btn-primary"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    Generate Chapter
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Chapter Info */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Chapter Info</h3>
            <div className="space-y-3">
              <div>
                <span className="font-medium text-gray-700">Chapter:</span>
                <span className="ml-2 text-gray-600">{chapterNumber}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Status:</span>
                <span className="ml-2">
                  {currentChapter.content ? (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      Generated
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                      Pending
                    </span>
                  )}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Created:</span>
                <span className="ml-2 text-gray-600">
                  {formatDate(currentChapter.created_at)}
                </span>
              </div>
              {currentChapter.updated_at !== currentChapter.created_at && (
                <div>
                  <span className="font-medium text-gray-700">Updated:</span>
                  <span className="ml-2 text-gray-600">
                    {formatDate(currentChapter.updated_at)}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Summary */}
          {currentChapter.summary && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Summary</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {currentChapter.summary}
              </p>
            </div>
          )}

          {/* Notes */}
          {currentChapter.chapter_notes && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Notes</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {currentChapter.chapter_notes}
              </p>
            </div>
          )}

          {/* Quick Actions */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button
                onClick={() => {
                  reset();
                  setIsEditing(true);
                }}
                className="w-full btn btn-secondary text-sm"
                disabled={generateChapterMutation.isLoading}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Regenerate
              </button>
              
              {currentChapter.content && (
                <button className="w-full btn btn-secondary text-sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export Chapter
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Chapter Navigation Footer */}
      <div className="flex justify-between items-center card p-4">
        <div className="flex items-center space-x-4">
          {previousChapter && (
            <Link
              to={`/books/${id}/chapters/${previousChapter.chapter_number}`}
              className="flex items-center text-primary-600 hover:text-primary-800"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Previous: Chapter {previousChapter.chapter_number}
            </Link>
          )}
        </div>
        
        <Link
          to={`/books/${id}`}
          className="text-gray-600 hover:text-gray-900"
        >
          Back to Book
        </Link>

        <div className="flex items-center space-x-4">
          {nextChapter && (
            <Link
              to={`/books/${id}/chapters/${nextChapter.chapter_number}`}
              className="flex items-center text-primary-600 hover:text-primary-800"
            >
              Next: Chapter {nextChapter.chapter_number}
              <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChapterView;
