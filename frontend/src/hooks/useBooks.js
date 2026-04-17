import { useQuery, useMutation, useQueryClient } from 'react-query';
import { bookAPI } from '../services/api';
import toast from 'react-hot-toast';

// Hook to fetch all books
export const useBooks = (params = {}) => {
  return useQuery(
    ['books', params],
    () => bookAPI.getBooks(params),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      onError: (error) => {
        toast.error('Failed to fetch books');
      },
    }
  );
};

// Hook to fetch single book
export const useBook = (id) => {
  return useQuery(
    ['book', id],
    () => bookAPI.getBook(id),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000, // 2 minutes
      onError: (error) => {
        toast.error('Failed to fetch book details');
      },
    }
  );
};

// Hook to fetch book chapters
export const useBookChapters = (bookId) => {
  return useQuery(
    ['chapters', bookId],
    () => bookAPI.getBookChapters(bookId),
    {
      enabled: !!bookId,
      staleTime: 2 * 60 * 1000,
      onError: (error) => {
        toast.error('Failed to fetch chapters');
      },
    }
  );
};

// Hook to create book
export const useCreateBook = () => {
  const queryClient = useQueryClient();

  return useMutation(bookAPI.createBook, {
    onSuccess: (data) => {
      toast.success('Book created successfully!');
      queryClient.invalidateQueries('books');
      return data;
    },
    onError: (error) => {
      toast.error('Failed to create book');
    },
  });
};

// Hook to update book
export const useUpdateBook = () => {
  const queryClient = useQueryClient();

  return useMutation(
    ({ id, ...data }) => bookAPI.updateBook(id, data),
    {
      onSuccess: (data, variables) => {
        toast.success('Book updated successfully!');
        queryClient.invalidateQueries(['book', variables.id]);
        queryClient.invalidateQueries('books');
      },
      onError: (error) => {
        toast.error('Failed to update book');
      },
    }
  );
};

// Hook to update outline
export const useUpdateOutline = () => {
  const queryClient = useQueryClient();

  return useMutation(
    ({ id, ...data }) => bookAPI.updateOutline(id, data),
    {
      onSuccess: (data, variables) => {
        toast.success('Outline updated successfully!');
        queryClient.invalidateQueries(['book', variables.id]);
        queryClient.invalidateQueries('books');
      },
      onError: (error) => {
        toast.error('Failed to update outline');
      },
    }
  );
};

// Hook to regenerate outline
export const useRegenerateOutline = () => {
  const queryClient = useQueryClient();

  return useMutation(bookAPI.regenerateOutline, {
    onSuccess: (data, variables) => {
      toast.success('Outline regenerated successfully!');
      queryClient.invalidateQueries(['book', variables]);
      queryClient.invalidateQueries('books');
    },
    onError: (error) => {
      toast.error('Failed to regenerate outline');
    },
  });
};

// Hook to generate chapter
export const useGenerateChapter = () => {
  const queryClient = useQueryClient();

  return useMutation(
    ({ bookId, chapterNumber, ...data }) => 
      bookAPI.generateChapter(bookId, chapterNumber, data),
    {
      onSuccess: (data, variables) => {
        toast.success(`Chapter ${variables.chapterNumber} generated successfully!`);
        queryClient.invalidateQueries(['chapters', variables.bookId]);
        queryClient.invalidateQueries(['book', variables.bookId]);
      },
      onError: (error) => {
        toast.error('Failed to generate chapter');
      },
    }
  );
};

// Hook for final review
export const useFinalReview = () => {
  const queryClient = useQueryClient();

  return useMutation(
    ({ id, ...data }) => bookAPI.finalReview(id, data),
    {
      onSuccess: (data, variables) => {
        toast.success('Final review submitted successfully!');
        queryClient.invalidateQueries(['book', variables.id]);
        queryClient.invalidateQueries('books');
      },
      onError: (error) => {
        toast.error('Failed to submit final review');
      },
    }
  );
};

// Hook to export book
export const useExportBook = () => {
  return useMutation(
    ({ id, format }) => bookAPI.exportBook(id, format),
    {
      onSuccess: (data) => {
        toast.success(`Book exported successfully as ${data.data.format.toUpperCase()}!`);
        // You could trigger file download here if needed
      },
      onError: (error) => {
        toast.error('Failed to export book');
      },
    }
  );
};
