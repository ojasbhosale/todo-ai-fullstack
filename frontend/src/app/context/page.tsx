'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import {
  Plus,
  MessageSquare,
  Mail,
  FileText,
  Calendar,
  Search,
  Filter,
  Brain,
  TrendingUp,
} from 'lucide-react';
import Layout from '@/components/layout/Layout';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Badge from '@/components/ui/Badge';
import Modal from '@/components/ui/Modal';
import { useContext } from '@/hooks/useContext';
import { ContextEntry, ContextEntryCreate } from '@/types';
import { format } from 'date-fns';

export default function ContextPage() {
  const { entries, loading, createEntry, deleteEntry, analyzeContent } = useContext();
  
  const [showAddModal, setShowAddModal] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [sourceFilter, setSourceFilter] = React.useState('');
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [formData, setFormData] = React.useState<ContextEntryCreate>({
    content: '',
    source_type: 'notes',
    metadata: {},
  });

  const filteredEntries = React.useMemo(() => {
    return entries.filter(entry => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!entry.content.toLowerCase().includes(query)) {
          return false;
        }
      }
      if (sourceFilter && entry.source_type !== sourceFilter) return false;
      return true;
    });
  }, [entries, searchQuery, sourceFilter]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      await createEntry(formData);
      setFormData({ content: '', source_type: 'notes', metadata: {} });
      setShowAddModal(false);
    } catch (error) {
      console.error('Failed to create context entry:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setShowAddModal(false);
      setFormData({ content: '', source_type: 'notes', metadata: {} });
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this context entry?')) {
      await deleteEntry(id);
    }
  };

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'email':
        return <Mail className="w-4 h-4" />;
      case 'whatsapp':
        return <MessageSquare className="w-4 h-4" />;
      case 'calendar':
        return <Calendar className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getSourceColor = (sourceType: string) => {
    switch (sourceType) {
      case 'email':
        return 'primary';
      case 'whatsapp':
        return 'success';
      case 'calendar':
        return 'warning';
      default:
        return 'default';
    }
  };

  const sourceOptions = [
    { value: '', label: 'All Sources' },
    { value: 'email', label: 'Email' },
    { value: 'whatsapp', label: 'WhatsApp' },
    { value: 'notes', label: 'Notes' },
    { value: 'calendar', label: 'Calendar' },
  ];

  const sourceTypeOptions = [
    { value: 'email', label: 'Email' },
    { value: 'whatsapp', label: 'WhatsApp' },
    { value: 'notes', label: 'Notes' },
    { value: 'calendar', label: 'Calendar' },
  ];

  return (
    <Layout>
      <Toaster position="top-right" />
      
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Context Entries
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Manage your daily context data for AI-powered insights
            </p>
          </div>
          <Button
            onClick={() => setShowAddModal(true)}
            className="flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Context
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Total Entries
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {entries.length}
                </p>
              </div>
              <div className="p-3 rounded-full bg-blue-500">
                <FileText className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Processed
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {entries.filter(e => e.is_processed).length}
                </p>
              </div>
              <div className="p-3 rounded-full bg-green-500">
                <Brain className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Avg Relevance
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {entries.length > 0 
                    ? (entries.reduce((sum, e) => sum + e.relevance_score, 0) / entries.length).toFixed(1)
                    : '0.0'
                  }
                </p>
              </div>
              <div className="p-3 rounded-full bg-purple-500">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Sources
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {new Set(entries.map(e => e.source_type)).size}
                </p>
              </div>
              <div className="p-3 rounded-full bg-yellow-500">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="Search context entries..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="flex items-center space-x-4">
            <Filter className="w-4 h-4 text-gray-400" />
            <Select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              options={sourceOptions}
            />
          </div>
        </div>

        {/* Context Entries */}
        {loading ? (
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, index) => (
              <div
                key={index}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-pulse"
              >
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-2"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
                <div className="flex space-x-2">
                  <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-16"></div>
                  <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-12"></div>
                </div>
              </div>
            ))}
          </div>
        ) : filteredEntries.length > 0 ? (
          <div className="space-y-4">
            {filteredEntries.map((entry) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <Badge variant={getSourceColor(entry.source_type)} className="flex items-center">
                        {getSourceIcon(entry.source_type)}
                        <span className="ml-1 capitalize">{entry.source_type}</span>
                      </Badge>
                      
                      <Badge variant={entry.is_processed ? 'success' : 'warning'}>
                        {entry.is_processed ? 'Processed' : 'Pending'}
                      </Badge>
                      
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        Relevance: {(entry.relevance_score * 100).toFixed(0)}%
                      </span>
                      
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {format(new Date(entry.created_at), 'MMM d, yyyy HH:mm')}
                      </span>
                    </div>

                    <p className="text-gray-900 dark:text-white mb-3">
                      {entry.content}
                    </p>

                    {entry.extracted_keywords.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {entry.extracted_keywords.slice(0, 5).map((keyword, index) => (
                          <span
                            key={index}
                            className="inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded"
                          >
                            #{keyword}
                          </span>
                        ))}
                      </div>
                    )}

                    {entry.processed_insights && Object.keys(entry.processed_insights).length > 0 && (
                      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                        <h4 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">
                          AI Insights:
                        </h4>
                        <div className="text-sm text-blue-700 dark:text-blue-400">
                          {entry.processed_insights.sentiment && (
                            <p>Sentiment: <span className="font-medium">{entry.processed_insights.sentiment}</span></p>
                          )}
                          {entry.processed_insights.insights && Array.isArray(entry.processed_insights.insights) && (
                            <ul className="list-disc list-inside mt-1">
                              {entry.processed_insights.insights.map((insight: string, index: number) => (
                                <li key={index}>{insight}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => handleDelete(entry.id, e)}
                    className="text-red-600 hover:text-red-700"
                  >
                    Delete
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No context entries found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Start adding context data to get AI-powered insights.
            </p>
            <Button onClick={() => setShowAddModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Context
            </Button>
          </motion.div>
        )}
      </div>

      {/* Add Context Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={handleClose}
        title="Add Context Entry"
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Source Type"
            value={formData.source_type}
            onChange={(e) => setFormData(prev => ({ ...prev, source_type: e.target.value as any }))}
            options={sourceTypeOptions}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Content
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
              placeholder="Enter your context content..."
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
              required
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
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
              Add Context
            </Button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
}