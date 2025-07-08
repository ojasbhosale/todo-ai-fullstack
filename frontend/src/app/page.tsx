'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import {
  CheckSquare,
  Clock,
  AlertTriangle,
  TrendingUp,
  Calendar,
  Brain,
  Plus,
  Filter,
} from 'lucide-react';
import Layout from '@/components/layout/Layout';
import StatsCard from '@/components/dashboard/StatsCard';
import TaskCard from '@/components/tasks/TaskCard';
import TaskForm from '@/components/tasks/TaskForm';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import { useTasks, useTaskStatistics } from '@/hooks/useTasks';
import { useCategories } from '@/hooks/useCategories';
import { Task, TaskCreate } from '@/types';

export default function Dashboard() {
  const { tasks, loading, createTask, updateTask, deleteTask } = useTasks();
  const { statistics } = useTaskStatistics();
  const { categories } = useCategories();
  
  const [selectedTask, setSelectedTask] = React.useState<Task | null>(null);
  const [showTaskForm, setShowTaskForm] = React.useState(false);
  const [filter, setFilter] = React.useState({
    status: '',
    category: '',
    priority: '',
  });

  const filteredTasks = React.useMemo(() => {
    return tasks.filter(task => {
      if (filter.status && task.status !== filter.status) return false;
      if (filter.category && task.category !== filter.category) return false;
      if (filter.priority && task.priority_score.toString() !== filter.priority) return false;
      return true;
    });
  }, [tasks, filter]);

  const recentTasks = filteredTasks.slice(0, 6);

  const handleCreateTask = (taskData: TaskCreate) => {
    createTask(taskData);
  };

  const handleUpdateTask = (taskData: TaskCreate) => {
    if (selectedTask) {
      updateTask(selectedTask.id, taskData);
      setSelectedTask(null);
    }
  };

  const handleStatusChange = async (id: string, status: string) => {
    await updateTask(id, { status });
  };

  const handleEditTask = (task: Task) => {
    setSelectedTask(task);
    setShowTaskForm(true);
  };

  const handleDeleteTask = async (id: string) => {
    if (confirm('Are you sure you want to delete this task?')) {
      await deleteTask(id);
    }
  };

  const statusOptions = [
    { value: '', label: 'All Status' },
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
  ];

  const categoryOptions = [
    { value: '', label: 'All Categories' },
    ...categories.map(cat => ({ value: cat.name, label: cat.name })),
  ];

  const priorityOptions = [
    { value: '', label: 'All Priorities' },
    ...Array.from({ length: 10 }, (_, i) => ({
      value: (i + 1).toString(),
      label: `Priority ${i + 1}`,
    })),
  ];

  return (
    <Layout>
      <Toaster position="top-right" />
      
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Welcome back! Here&#39;s your task overview.
            </p>
          </div>
          <Button
            onClick={() => {
              setSelectedTask(null);
              setShowTaskForm(true);
            }}
            className="flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Task
          </Button>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatsCard
              title="Total Tasks"
              value={statistics.total_tasks}
              icon={CheckSquare}
              color="blue"
            />
            <StatsCard
              title="Pending Tasks"
              value={statistics.pending_tasks}
              icon={Clock}
              color="yellow"
            />
            <StatsCard
              title="Overdue Tasks"
              value={statistics.overdue_tasks}
              icon={AlertTriangle}
              color="red"
            />
            <StatsCard
              title="Avg Priority"
              value={statistics.average_priority.toFixed(1)}
              icon={TrendingUp}
              color="green"
            />
          </div>
        )}

        {/* Quick Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Today&#39;s Focus
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">High Priority</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {statistics?.high_priority_tasks || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">In Progress</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {statistics?.in_progress_tasks || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Completed</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {statistics?.completed_tasks || 0}
                </span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
              <Brain className="w-5 h-5 mr-2" />
              AI Insights
            </h3>
            <div className="space-y-3">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Most productive time: <span className="font-medium text-gray-900 dark:text-white">Morning</span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Completion rate: <span className="font-medium text-green-600">85%</span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Avg task duration: <span className="font-medium text-gray-900 dark:text-white">2.5 hours</span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Categories
            </h3>
            <div className="space-y-2">
              {statistics?.categories.slice(0, 4).map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">{category}</span>
                  <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                    <div
                      className="h-2 bg-primary-500 rounded-full"
                      style={{ width: `${Math.random() * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center space-x-4">
            <Filter className="w-5 h-5 text-gray-400" />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 flex-1">
              <Select
                value={filter.status}
                onChange={(e) => setFilter(prev => ({ ...prev, status: e.target.value }))}
                options={statusOptions}
              />
              <Select
                value={filter.category}
                onChange={(e) => setFilter(prev => ({ ...prev, category: e.target.value }))}
                options={categoryOptions}
              />
              <Select
                value={filter.priority}
                onChange={(e) => setFilter(prev => ({ ...prev, priority: e.target.value }))}
                options={priorityOptions}
              />
            </div>
          </div>
        </div>

        {/* Recent Tasks */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Recent Tasks
            </h2>
            <Button variant="ghost" size="sm">
              View All
            </Button>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, index) => (
                <div
                  key={index}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 animate-pulse"
                >
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
                  <div className="flex space-x-2">
                    <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
                    <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-12"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : recentTasks.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onEdit={handleEditTask}
                  onDelete={handleDeleteTask}
                  onStatusChange={handleStatusChange}
                />
              ))}
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <CheckSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No tasks found
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Get started by creating your first task.
              </p>
              <Button
                onClick={() => {
                  setSelectedTask(null);
                  setShowTaskForm(true);
                }}
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Task
              </Button>
            </motion.div>
          )}
        </div>
      </div>

      {/* Task Form Modal */}
      <TaskForm
        isOpen={showTaskForm}
        onClose={() => {
          setShowTaskForm(false);
          setSelectedTask(null);
        }}
        task={selectedTask}
        onSubmit={selectedTask ? handleUpdateTask : handleCreateTask}
      />
    </Layout>
  );
}