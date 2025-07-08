import { useState, useEffect } from 'react';
import { ContextEntry, ContextEntryCreate } from '@/types';
import { contextApi } from '@/lib/api';
import toast from 'react-hot-toast';

export const useContext = () => {
  const [entries, setEntries] = useState<ContextEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEntries = async (params?: {
    source_type?: string;
    is_processed?: boolean;
    min_relevance?: number;
  }) => {
    try {
      setLoading(true);
      const data = await contextApi.getAll(params);
      setEntries(data);
      setError(null);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
        toast.error(err.message);
      } else {
        setError('Failed to fetch context entries');
        toast.error('Failed to fetch context entries');
      }
    } finally {
      setLoading(false);
    }
  };

  const createEntry = async (entry: ContextEntryCreate) => {
    try {
      const newEntry = await contextApi.create(entry);
      setEntries(prev => [newEntry, ...prev]);
      toast.success('Context entry added successfully!');
      return newEntry;
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error(err.message);
      } else {
        toast.error('Failed to add context entry');
      }
      throw err;
    }
  };

  const updateEntry = async (id: string, updates: Partial<ContextEntryCreate>) => {
    try {
      const updatedEntry = await contextApi.update(id, updates);
      setEntries(prev => prev.map(entry => entry.id === id ? updatedEntry : entry));
      toast.success('Context entry updated successfully!');
      return updatedEntry;
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error(err.message);
      } else {
        toast.error('Failed to update context entry');
      }
      throw err;
    }
  };

  const deleteEntry = async (id: string) => {
    try {
      await contextApi.delete(id);
      setEntries(prev => prev.filter(entry => entry.id !== id));
      toast.success('Context entry deleted successfully!');
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error(err.message);
      } else {
        toast.error('Failed to delete context entry');
      }
      throw err;
    }
  };

  const analyzeContent = async (data: {
    content: string;
    source_type: string;
  }) => {
    try {
      return await contextApi.analyze(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error(err.message);
      } else {
        toast.error('Failed to analyze content');
      }
      throw err;
    }
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  return {
    entries,
    loading,
    error,
    fetchEntries,
    createEntry,
    updateEntry,
    deleteEntry,
    analyzeContent,
  };
};