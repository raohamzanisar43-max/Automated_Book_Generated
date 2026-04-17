import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useMutation } from 'react-query';
import { Book, ArrowLeft, Save } from 'lucide-react';

import { bookAPI } from '../services/api';
import { useCreateBook } from '../hooks/useBooks';
import LoadingSpinner from '../components/LoadingSpinner';

const CreateBook = () => {
  const navigate = useNavigate();
  const createBookMutation = useCreateBook();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
  } = useForm();

  const watchedTitle = watch('title', '');

  const onSubmit = async (data) => {
    try {
      const result = await createBookMutation.mutateAsync(data);
      navigate(`/books/${result.id}`);
    } catch (error) {
      // Error is handled by the mutation hook
    }
  };

  const handleCancel = () => {
    navigate('/');
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={handleCancel}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </button>
        <div className="flex items-center">
          <Book className="w-8 h-8 text-primary-600 mr-3" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Create New Book</h1>
            <p className="text-gray-600">Start your automated book generation journey</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="card p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Book Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Book Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              {...register('title', {
                required: 'Book title is required',
                minLength: {
                  value: 3,
                  message: 'Title must be at least 3 characters long',
                },
                maxLength: {
                  value: 200,
                  message: 'Title must not exceed 200 characters',
                },
              })}
              className={`input ${errors.title ? 'border-red-500' : ''}`}
              placeholder="Enter your book title..."
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
            )}
          </div>

          {/* Notes for Outline Generation */}
          <div>
            <label htmlFor="notes_on_outline_before" className="block text-sm font-medium text-gray-700 mb-2">
              Notes for Outline Generation <span className="text-red-500">*</span>
            </label>
            <textarea
              id="notes_on_outline_before"
              {...register('notes_on_outline_before', {
                required: 'Notes are required for outline generation',
                minLength: {
                  value: 10,
                  message: 'Please provide at least 10 characters of notes',
                },
              })}
              rows={6}
              className={`input ${errors.notes_on_outline_before ? 'border-red-500' : ''}`}
              placeholder="Describe your book requirements, target audience, writing style, key topics to cover, research preferences, and any specific instructions for the AI..."
            />
            {errors.notes_on_outline_before && (
              <p className="mt-1 text-sm text-red-600">
                {errors.notes_on_outline_before.message}
              </p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              Provide detailed notes to help the AI generate a comprehensive outline for your book.
            </p>
          </div>

          {/* Preview Section */}
          {watchedTitle && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Preview</h3>
              <div className="text-sm text-gray-600">
                <p><strong>Title:</strong> {watchedTitle}</p>
                <p><strong>Status:</strong> Will be generated as draft outline</p>
              </div>
            </div>
          )}

          {/* Form Actions */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleCancel}
              className="btn btn-secondary"
              disabled={isSubmitting || createBookMutation.isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting || createBookMutation.isLoading}
            >
              {isSubmitting || createBookMutation.isLoading ? (
                <>
                  <LoadingSpinner size="small" text="" />
                  Creating...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Create Book
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Help Section */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">
          <Book className="w-4 h-4 inline mr-2" />
          Tips for Creating a Great Book
        </h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Be specific about your target audience and their knowledge level</li>
          <li>Include preferred writing style (formal, casual, academic, etc.)</li>
          <li>Mention key topics or themes you want to cover</li>
          <li>Specify any research requirements or sources to include</li>
          <li>Provide examples of similar books you like</li>
        </ul>
      </div>
    </div>
  );
};

export default CreateBook;
