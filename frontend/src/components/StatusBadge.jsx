import React from 'react';
import { CheckCircle, Clock, PauseCircle, AlertCircle, BookOpen } from 'lucide-react';

const StatusBadge = ({ status }) => {
  const getStatusConfig = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return {
          color: 'bg-green-100 text-green-800',
          icon: CheckCircle,
          text: 'Completed',
        };
      case 'generating_chapters':
      case 'compiling':
      case 'in_progress':
        return {
          color: 'bg-blue-100 text-blue-800',
          icon: Clock,
          text: 'In Progress',
        };
      case 'paused':
        return {
          color: 'bg-yellow-100 text-yellow-800',
          icon: PauseCircle,
          text: 'Paused',
        };
      case 'draft_outline':
        return {
          color: 'bg-purple-100 text-purple-800',
          icon: BookOpen,
          text: 'Draft Outline',
        };
      case 'review_outline':
      case 'reviewing_chapters':
        return {
          color: 'bg-indigo-100 text-indigo-800',
          icon: AlertCircle,
          text: 'Review Needed',
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-800',
          icon: Clock,
          text: status || 'Unknown',
        };
    }
  };

  const config = getStatusConfig(status);
  const Icon = config.icon;

  return (
    <span className={`status-badge ${config.color} flex items-center`}>
      <Icon className="w-3 h-3 mr-1" />
      {config.text}
    </span>
  );
};

export default StatusBadge;
