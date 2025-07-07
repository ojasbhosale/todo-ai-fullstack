import { useState, useEffect } from 'react';
import { Task, TaskCreate, TaskUpdate, TaskStatistics } from '@/types';
import { tasksApi } from '@/lib/api';
import toast from 'react-hot-toast';

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async (params?: {
    status?: string;
    category?: string;
    priority?: number;
    overdue?: boolean;
  }) => {
    try {
      setLoading(true);
      const data = await tasksApi.getAll(params);
      setTasks(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch tasks');
      toast.error('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (task: TaskCreate) => {
    try {
      const newTask = await tasksApi.create(task);
      setTasks(prev => [newTask, ...prev]);
      toast.success('Task created successfully!');
      return newTask;
    } catch (err: any) {
      toast.error('Failed to create task');
      throw err;
    }
  };

  const updateTask = async (id: string, updates: TaskUpdate) => {
    try {
      const updatedTask = await tasksApi.update(id, updates);
      setTasks(prev => prev.map(task => task.id === id ? updatedTask : task));
      toast.success('Task updated successfully!');
      return updatedTask;
    } catch (err: any) {
      toast.error('Failed to update task');
      throw err;
    }
  };

  const deleteTask = async (id: string) => {
    try {
      await tasksApi.delete(id);
      setTasks(prev => prev.filter(task => task.id !== id));
      toast.success('Task deleted successfully!');
    } catch (err: any) {
      toast.error('Failed to delete task');
      throw err;
    }
  };

  const getAISuggestions = async (data: {
    title: string;
    description?: string;
    category?: string;
  }) => {
    try {
      return await tasksApi.getAISuggestions({
        ...data,
        current_workload: tasks.filter(t => t.status === 'pending').length,
      });
    } catch (err: any) {
      toast.error('Failed to get AI suggestions');
      throw err;
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    getAISuggestions,
  };
};

export const useTaskStatistics = () => {
  const [statistics, setStatistics] = useState<TaskStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const data = await tasksApi.getStatistics();
        setStatistics(data);
      } catch (err) {
        console.error('Failed to fetch statistics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStatistics();
  }, []);

  return { statistics, loading };
};