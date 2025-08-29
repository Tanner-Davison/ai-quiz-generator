export const getScoreColor = (percentage: number): string => {
  if (percentage >= 80) return '#4CAF50';
  if (percentage >= 60) return '#FF9800';
  return '#F44336';
};
