'use client';

import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import {
  Calendar,
  AlertTriangle,
  CheckCircle,
  Circle,
  MoreVertical,
  Edit,
  Trash2,
  Play,
} from 'lucide-react';
import { Task } from '@/types';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onStatusChange: (id: string, status: string) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onEdit,
  onDelete,
  onStatusChange,
}) => {
  const [showActions, setShowActions] = React.useState(false);
  const actionsRef = useRef<HTMLDivElement>(null);

  // Close actions menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (actionsRef.current && !actionsRef.current.contains(event.target as Node)) {
        setShowActions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'danger';
    if (priority >= 6) return 'warning';
    if (priority >= 4) return 'primary';
    return 'default';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in_progress':
        return <Play className="w-5 h-5 text-blue-500" />;
      default:
        return <Circle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'cancelled':
        return 'danger';
      default:
        return 'default';
    }
  };

  const handleStatusToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    onStatusChange(task.id, newStatus);
  };

  const handleActionsToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowActions(!showActions);
  };

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit(task);
    setShowActions(false);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this task?')) {
      onDelete(task.id);
    }
    setShowActions(false);
  };

  const handleStatusChange = (e: React.MouseEvent, newStatus: string) => {
    e.stopPropagation();
    onStatusChange(task.id, newStatus);
    setShowActions(false);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ y: -2 }}
      className={`
        bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4
        hover:shadow-md transition-all duration-200 cursor-pointer
        ${task.is_overdue ? 'border-l-4 border-l-red-500' : ''}
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <button
            onClick={handleStatusToggle}
            className="mt-1 hover:scale-110 transition-transform"
          >
            {getStatusIcon(task.status)}
          </button>

          <div className="flex-1 min-w-0">
            <h3 className={`text-lg font-medium text-gray-900 dark:text-white ${
              task.status === 'completed' ? 'line-through opacity-60' : ''
            }`}>
              {task.title}
            </h3>
            
            {task.description && (
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                {task.description}
              </p>
            )}

            {task.ai_enhanced_description && task.ai_enhanced_description !== task.description && (
              <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded border-l-2 border-blue-200 dark:border-blue-700">
                <p className="text-xs text-blue-700 dark:text-blue-300 font-medium mb-1">
                  AI Enhancement:
                </p>
                <p className="text-sm text-blue-600 dark:text-blue-400">
                  {task.ai_enhanced_description}
                </p>
              </div>
            )}

            <div className="flex items-center space-x-4 mt-3">
              {task.deadline && (
                <div className={`flex items-center space-x-1 text-sm ${
                  task.is_overdue ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-400'
                }`}>
                  <Calendar className="w-4 h-4" />
                  <span>{format(new Date(task.deadline), 'MMM d, yyyy')}</span>
                  {task.is_overdue && <AlertTriangle className="w-4 h-4 ml-1" />}
                </div>
              )}

              {task.category && (
                <Badge variant="default" size="sm">
                  {task.category}
                </Badge>
              )}

              <Badge variant={getPriorityColor(task.priority_score)} size="sm">
                P{task.priority_score}
              </Badge>

              <Badge variant={getStatusColor(task.status)} size="sm">
                {task.status.replace('_', ' ')}
              </Badge>
            </div>

            {task.ai_suggested_tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {task.ai_suggested_tags.slice(0, 3).map((tag, index) => (
                  <span
                    key={index}
                    className="inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded"
                  >
                    #{tag}
                  </span>
                ))}
                {task.ai_suggested_tags.length > 3 && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    +{task.ai_suggested_tags.length - 3} more
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="relative" ref={actionsRef}>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleActionsToggle}
            className="p-1"
          >
            <MoreVertical className="w-4 h-4" />
          </Button>

          {showActions && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="absolute right-0 top-8 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-20"
            >
              <button
                onClick={handleEdit}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
              >
                <Edit className="w-4 h-4 mr-2" />
                Edit Task
              </button>
              
              <button
                onClick={(e) => handleStatusChange(e, task.status === 'in_progress' ? 'pending' : 'in_progress')}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
              >
                <Play className="w-4 h-4 mr-2" />
                {task.status === 'in_progress' ? 'Mark Pending' : 'Start Task'}
              </button>
              
              <button
                onClick={handleDelete}
                className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Task
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default TaskCard;