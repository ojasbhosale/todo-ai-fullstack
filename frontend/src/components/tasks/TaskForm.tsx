'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { Sparkles, AlertCircle } from 'lucide-react';
import { Task, TaskCreate, AITaskSuggestion } from '@/types';
import { useCategories } from '@/hooks/useCategories';
import { useTasks } from '@/hooks/useTasks';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Modal from '@/components/ui/Modal';

interface TaskFormProps {
  isOpen: boolean;
  onClose: () => void;
  task?: Task | null;
  onSubmit: (task: TaskCreate) => void;
}

const TaskForm: React.FC<TaskFormProps> = ({
  isOpen,
  onClose,
  task,
  onSubmit,
}) => {
  const { categories } = useCategories();
  const { getAISuggestions } = useTasks();
  
  const [formData, setFormData] = useState<TaskCreate>({
    title: '',
    description: '',
    category: '',
    priority_score: 5,
    deadline: null,
    status: 'pending',
  });
  
  const [aiSuggestions, setAiSuggestions] = useState<AITaskSuggestion | null>(null);
  const [loadingAI, setLoadingAI] = useState(false);
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description,
        category: task.category,
        priority_score: task.priority_score,
        deadline: task.deadline,
        status: task.status,
      });
    } else {
      setFormData({
        title: '',
        description: '',
        category: '',
        priority_score: 5,
        deadline: null,
        status: 'pending',
      });
    }
    setAiSuggestions(null);
    setShowAISuggestions(false);
  }, [task, isOpen]);

  const handleInputChange = (field: keyof TaskCreate, value: string | number | null) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleGetAISuggestions = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!formData.title.trim()) return;
    
    setLoadingAI(true);
    try {
      const suggestions = await getAISuggestions({
        title: formData.title,
        description: formData.description,
        category: formData.category,
      });
      setAiSuggestions(suggestions);
      setShowAISuggestions(true);
    } catch (error) {
      console.error('Failed to get AI suggestions:', error);
    } finally {
      setLoadingAI(false);
    }
  };

  const applyAISuggestions = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!aiSuggestions) return;
    
    setFormData(prev => ({
      ...prev,
      priority_score: aiSuggestions.priority_score,
      deadline: aiSuggestions.suggested_deadline,
      description: aiSuggestions.enhanced_description,
      category: aiSuggestions.suggested_category,
    }));
    setShowAISuggestions(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Failed to submit task:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  const statusOptions = [
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  const priorityOptions = Array.from({ length: 10 }, (_, i) => ({
    value: (i + 1).toString(),
    label: `Priority ${i + 1}`,
  }));

  const categoryOptions = [
    { value: '', label: 'Select Category' },
    ...categories.map(cat => ({ value: cat.name, label: cat.name })),
  ];

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={task ? 'Edit Task' : 'Create New Task'}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <Input
              label="Task Title"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="Enter task title..."
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Enter task description..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
            />
          </div>

          <Select
            label="Category"
            value={formData.category}
            onChange={(e) => handleInputChange('category', e.target.value)}
            options={categoryOptions}
          />

          <Select
            label="Priority"
            value={(formData.priority_score ?? 5).toString()}
            onChange={(e) => handleInputChange('priority_score', parseInt(e.target.value))}
            options={priorityOptions}
          />

          <Input
            label="Deadline"
            type="datetime-local"
            value={formData.deadline ? format(new Date(formData.deadline), "yyyy-MM-dd'T'HH:mm") : ''}
            onChange={(e) => handleInputChange('deadline', e.target.value || null)}
          />

          <Select
            label="Status"
            value={formData.status}
            onChange={(e) => handleInputChange('status', e.target.value)}
            options={statusOptions}
          />
        </div>

        {/* AI Suggestions Section */}
        <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-primary-500" />
              AI Suggestions
            </h3>
            <Button
              type="button"
              variant="secondary"
              onClick={handleGetAISuggestions}
              loading={loadingAI}
              disabled={!formData.title.trim() || isSubmitting}
            >
              Get AI Suggestions
            </Button>
          </div>

          {showAISuggestions && aiSuggestions && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 space-y-4"
            >
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-blue-900 dark:text-blue-300">
                  AI Recommendations
                </h4>
                <Button
                  type="button"
                  size="sm"
                  onClick={applyAISuggestions}
                  disabled={isSubmitting}
                >
                  Apply All
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-blue-800 dark:text-blue-300">Priority:</span>
                  <Badge variant="primary" className="ml-2">
                    {aiSuggestions.priority_score}/10
                  </Badge>
                </div>

                {aiSuggestions.suggested_deadline && (
                  <div>
                    <span className="font-medium text-blue-800 dark:text-blue-300">Deadline:</span>
                    <span className="ml-2 text-blue-700 dark:text-blue-400">
                      {format(new Date(aiSuggestions.suggested_deadline), 'MMM d, yyyy')}
                    </span>
                  </div>
                )}

                <div>
                  <span className="font-medium text-blue-800 dark:text-blue-300">Category:</span>
                  <span className="ml-2 text-blue-700 dark:text-blue-400">
                    {aiSuggestions.suggested_category}
                  </span>
                </div>

                <div>
                  <span className="font-medium text-blue-800 dark:text-blue-300">Duration:</span>
                  <span className="ml-2 text-blue-700 dark:text-blue-400">
                    {aiSuggestions.estimated_duration}
                  </span>
                </div>
              </div>

              {aiSuggestions.enhanced_description && (
                <div>
                  <span className="font-medium text-blue-800 dark:text-blue-300">Enhanced Description:</span>
                  <p className="mt-1 text-blue-700 dark:text-blue-400">
                    {aiSuggestions.enhanced_description}
                  </p>
                </div>
              )}

              {aiSuggestions.ai_suggested_tags.length > 0 && (
                <div>
                  <span className="font-medium text-blue-800 dark:text-blue-300">Suggested Tags:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {aiSuggestions.ai_suggested_tags.map((tag, index) => (
                      <Badge key={index} variant="primary" size="sm">
                        #{tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {aiSuggestions.reasoning && (
                <div>
                  <span className="font-medium text-blue-800 dark:text-blue-300">AI Reasoning:</span>
                  <p className="mt-1 text-blue-700 dark:text-blue-400 text-sm">
                    {aiSuggestions.reasoning}
                  </p>
                </div>
              )}

              {aiSuggestions.context_insights.length > 0 && (
                <div>
                  <span className="font-medium text-blue-800 dark:text-blue-300">Context Insights:</span>
                  <ul className="mt-1 space-y-1">
                    {aiSuggestions.context_insights.map((insight, index) => (
                      <li key={index} className="text-blue-700 dark:text-blue-400 text-sm flex items-start">
                        <AlertCircle className="w-3 h-3 mr-1 mt-0.5 flex-shrink-0" />
                        {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>
          )}
        </div>

        <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
          <Button 
            type="button" 
            variant="secondary" 
            onClick={handleClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button 
            type="submit"
            loading={isSubmitting}
            disabled={isSubmitting}
          >
            {task ? 'Update Task' : 'Create Task'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default TaskForm;