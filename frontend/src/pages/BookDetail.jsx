import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from 'react-query';
import { useForm } from 'react-hook-form';
import {
  Book,
  ArrowLeft,
  Edit,
  Save,
  RefreshCw,
  CheckCircle,
  MessageSquare,
  Download,
  FileText,
  Eye,
} from 'lucide-react';

import { bookAPI } from '../services/api';
import {
  useBook,
  useBookChapters,
  useUpdateOutline,
  useRegenerateOutline,
  useGenerateChapter,
  useFinalReview,
  useExportBook,
} from '../hooks/useBooks';
import StatusBadge from '../components/StatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { format } from 'date-fns';

const BookDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [showOutlineEditor, setShowOutlineEditor] = useState(false);
  const [showFinalReview, setShowFinalReview] = useState(false);

  const { data: book, isLoading: bookLoading, error: bookError } = useBook(id);
  const { data: chapters = [], isLoading: chaptersLoading } = useBookChapters(id);

  const updateOutlineMutation = useUpdateOutline();
  const regenerateOutlineMutation = useRegenerateOutline();
  const generateChapterMutation = useGenerateChapter();
  const finalReviewMutation = useFinalReview();
  const exportBookMutation = useExportBook();

  const {
    register: registerOutline,
    handleSubmit: handleOutlineSubmit,
    formState: { errors: outlineErrors },
    reset: resetOutline,
  } = useForm();

  const {
    register: registerFinalReview,
    handleSubmit: handleFinalReviewSubmit,
    formState: { errors: finalReviewErrors },
    reset: resetFinalReview,
  } = useForm();

  const onOutlineUpdate = async (data) => {
    try {
      await updateOutlineMutation.mutateAsync({
        id,
        ...data,
      });
      setShowOutlineEditor(false);
    } catch (error) {
      // Error handled by mutation hook
    }
  };

  const onRegenerateOutline = async () => {
    try {
      await regenerateOutlineMutation.mutateAsync(id);
    } catch (error) {
      // Error handled by mutation hook
    }
  };

  const onGenerateChapter = async (chapterNumber) => {
    try {
      await generateChapterMutation.mutateAsync({
        bookId: id,
        chapterNumber,
        chapter_notes_status: 'no_notes_needed',
      });
    } catch (error) {
      // Error handled by mutation hook
    }
  };

  const onFinalReview = async (data) => {
    try {
      await finalReviewMutation.mutateAsync({
        id,
        ...data,
      });
      setShowFinalReview(false);
    } catch (error) {
      // Error handled by mutation hook
    }
  };

  const onExportBook = async (format) => {
    try {
      await exportBookMutation.mutateAsync({ id, format });
    } catch (error) {
      // Error handled by mutation hook
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return format(new Date(dateString), 'MMM dd, yyyy \'at\' h:mm a');
  };

  if (bookLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="large" text="Loading book details..." />
      </div>
    );
  }

  if (bookError || !book) {
    return (
      <div className="text-center py-12">
        <Book className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Book not found</h3>
        <p className="text-gray-600 mb-4">The book you're looking for doesn't exist</p>
        <button onClick={() => navigate('/')} className="btn btn-primary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const canGenerateChapters = book.outline && book.status_outline_notes === 'no_notes_needed';
  const canFinalReview = chapters.length > 0 && chapters.every(ch => ch.content);
  const canExport = book.status === 'completed';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex items-start space-x-4">
          <button
            onClick={() => navigate('/')}
            className="text-gray-600 hover:text-gray-900 mt-1"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{book.title}</h1>
            <div className="flex items-center space-x-4 mt-2">
              <StatusBadge status={book.status} />
              <span className="text-sm text-gray-500">
                Created {formatDate(book.created_at)}
              </span>
            </div>
          </div>
        </div>

        <div className="flex space-x-2">
          {book.outline && (
            <button
              onClick={() => setShowOutlineEditor(!showOutlineEditor)}
              className="btn btn-secondary"
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit Outline
            </button>
          )}
          {canExport && (
            <div className="relative group">
              <button className="btn btn-success">
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                <button
                  onClick={() => onExportBook('docx')}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Export as DOCX
                </button>
                <button
                  onClick={() => onExportBook('pdf')}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Export as PDF
                </button>
                <button
                  onClick={() => onExportBook('txt')}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Export as TXT
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {['overview', 'outline', 'chapters', 'review'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {/* Book Info */}
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Book Information</h2>
                <div className="space-y-3">
                  <div>
                    <span className="font-medium text-gray-700">Status:</span>
                    <StatusBadge status={book.status} className="ml-2" />
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Created:</span>
                    <span className="ml-2 text-gray-600">{formatDate(book.created_at)}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Last Updated:</span>
                    <span className="ml-2 text-gray-600">{formatDate(book.updated_at)}</span>
                  </div>
                  {book.file_url && (
                    <div>
                      <span className="font-medium text-gray-700">Output File:</span>
                      <a
                        href={book.file_url}
                        className="ml-2 text-primary-600 hover:text-primary-800"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Download
                      </a>
                    </div>
                  )}
                </div>
              </div>

              {/* Progress */}
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Generation Progress</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Outline</span>
                    <span className="text-sm text-gray-600">
                      {book.outline ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Chapters</span>
                    <span className="text-sm text-gray-600">
                      {chapters.filter(ch => ch.content).length}/{chapters.length} Generated
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Final Review</span>
                    <span className="text-sm text-gray-600">
                      {book.final_review_notes_status ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="space-y-4">
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  {!book.outline && (
                    <p className="text-sm text-gray-600">Outline is being generated...</p>
                  )}
                  {book.outline && !canGenerateChapters && (
                    <button
                      onClick={() => setShowOutlineEditor(true)}
                      className="w-full btn btn-primary"
                    >
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Review Outline
                    </button>
                  )}
                  {canGenerateChapters && (
                    <button
                      onClick={() => onGenerateChapter(chapters.length + 1)}
                      className="w-full btn btn-primary"
                      disabled={generateChapterMutation.isLoading}
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      Generate Next Chapter
                    </button>
                  )}
                  {canFinalReview && (
                    <button
                      onClick={() => setShowFinalReview(true)}
                      className="w-full btn btn-success"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Final Review
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Outline Tab */}
        {activeTab === 'outline' && (
          <div className="space-y-6">
            <div className="card p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Book Outline</h2>
                <div className="flex space-x-2">
                  <button
                    onClick={onRegenerateOutline}
                    className="btn btn-secondary"
                    disabled={regenerateOutlineMutation.isLoading}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Regenerate
                  </button>
                  <button
                    onClick={() => setShowOutlineEditor(true)}
                    className="btn btn-primary"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit
                  </button>
                </div>
              </div>

              {book.outline ? (
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap text-gray-700 font-mono text-sm">
                    {book.outline}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="w-12 h-12 mx-auto mb-4" />
                  <p>No outline generated yet</p>
                </div>
              )}
            </div>

            {/* Initial Notes */}
            {book.notes_on_outline_before && (
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Initial Requirements</h3>
                <p className="text-gray-700 whitespace-pre-wrap">
                  {book.notes_on_outline_before}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Chapters Tab */}
        {activeTab === 'chapters' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900">Chapters</h2>
              {canGenerateChapters && (
                <button
                  onClick={() => onGenerateChapter(chapters.length + 1)}
                  className="btn btn-primary"
                  disabled={generateChapterMutation.isLoading}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Generate Next Chapter
                </button>
              )}
            </div>

            {chapters.length === 0 ? (
              <div className="card p-12 text-center">
                <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No chapters yet</h3>
                <p className="text-gray-600 mb-4">
                  {canGenerateChapters
                    ? 'Start generating chapters for your book'
                    : 'Complete outline review to start generating chapters'}
                </p>
                {canGenerateChapters && (
                  <button
                    onClick={() => onGenerateChapter(1)}
                    className="btn btn-primary"
                    disabled={generateChapterMutation.isLoading}
                  >
                    Generate First Chapter
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {chapters.map((chapter) => (
                  <div key={chapter.id} className="card p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {chapter.title || `Chapter ${chapter.chapter_number}`}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {formatDate(chapter.created_at)}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${
                            chapter.content
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {chapter.content ? 'Generated' : 'Pending'}
                        </span>
                        {chapter.content && (
                          <button
                            onClick={() => navigate(`/books/${id}/chapters/${chapter.chapter_number}`)}
                            className="text-primary-600 hover:text-primary-800"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>

                    {chapter.summary && (
                      <div className="text-sm text-gray-600 mb-3">
                        <strong>Summary:</strong> {chapter.summary}
                      </div>
                    )}

                    {chapter.chapter_notes && (
                      <div className="text-sm text-gray-600">
                        <strong>Notes:</strong> {chapter.chapter_notes}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Review Tab */}
        {activeTab === 'review' && (
          <div className="space-y-6">
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Final Review</h2>
              
              {canFinalReview ? (
                <div className="space-y-4">
                  <p className="text-gray-600">
                    All chapters have been generated. You can now proceed with final review and compilation.
                  </p>
                  <button
                    onClick={() => setShowFinalReview(true)}
                    className="btn btn-success"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Start Final Review
                  </button>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 mx-auto mb-4" />
                  <p>Complete chapter generation before proceeding to final review</p>
                  <div className="mt-4 text-sm">
                    Progress: {chapters.filter(ch => ch.content).length}/{chapters.length} chapters
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Outline Editor Modal */}
      {showOutlineEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Review & Edit Outline</h3>
            
            <form onSubmit={handleOutlineSubmit(onOutlineUpdate)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Feedback Notes
                </label>
                <textarea
                  {...registerOutline('notes_on_outline_after')}
                  rows={4}
                  className="input"
                  placeholder="Add your feedback on the outline..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review Status
                </label>
                <select {...registerOutline('status_outline_notes')} className="input">
                  <option value="yes">Needs more work</option>
                  <option value="no_notes_needed">Approved - proceed to chapters</option>
                  <option value="no">Pause - need to review later</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowOutlineEditor(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={updateOutlineMutation.isLoading}
                >
                  {updateOutlineMutation.isLoading ? 'Saving...' : 'Save Review'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Final Review Modal */}
      {showFinalReview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Final Review</h3>
            
            <form onSubmit={handleFinalReviewSubmit(onFinalReview)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Final Review Notes (Optional)
                </label>
                <textarea
                  {...registerFinalReview('final_review_notes')}
                  rows={4}
                  className="input"
                  placeholder="Add any final notes or feedback..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review Status
                </label>
                <select {...registerFinalReview('final_review_notes_status')} className="input">
                  <option value="no_notes_needed">Approved - compile book</option>
                  <option value="yes">Needs final revisions</option>
                  <option value="no">Pause - need to review later</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowFinalReview(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-success"
                  disabled={finalReviewMutation.isLoading}
                >
                  {finalReviewMutation.isLoading ? 'Processing...' : 'Submit Review'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default BookDetail;
