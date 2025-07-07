import { useState, useEffect } from 'react';
import { Category, CategoryCreate } from '@/types';
import { categoriesApi } from '@/lib/api';
import toast from 'react-hot-toast';

export const useCategories = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = async (params?: {
    is_active?: boolean;
    search?: string;
  }) => {
    try {
      setLoading(true);
      const data = await categoriesApi.getAll(params);
      setCategories(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch categories');
      toast.error('Failed to fetch categories');
    } finally {
      setLoading(false);
    }
  };

  const createCategory = async (category: CategoryCreate) => {
    try {
      const newCategory = await categoriesApi.create(category);
      setCategories(prev => [newCategory, ...prev]);
      toast.success('Category created successfully!');
      return newCategory;
    } catch (err: any) {
      toast.error('Failed to create category');
      throw err;
    }
  };

  const updateCategory = async (id: string, updates: Partial<CategoryCreate>) => {
    try {
      const updatedCategory = await categoriesApi.update(id, updates);
      setCategories(prev => prev.map(cat => cat.id === id ? updatedCategory : cat));
      toast.success('Category updated successfully!');
      return updatedCategory;
    } catch (err: any) {
      toast.error('Failed to update category');
      throw err;
    }
  };

  const deleteCategory = async (id: string) => {
    try {
      await categoriesApi.delete(id);
      setCategories(prev => prev.filter(cat => cat.id !== id));
      toast.success('Category deleted successfully!');
    } catch (err: any) {
      toast.error('Failed to delete category');
      throw err;
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  return {
    categories,
    loading,
    error,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
  };
};