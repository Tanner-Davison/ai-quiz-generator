import React from 'react';
import { TopicInputSectionStyles as styles } from '../cssmodules';

interface TopicInputSectionProps {
  topic: string;
  setTopic: (topic: string) => void;
  isGenerating: boolean;
  onGenerateQuiz: () => void;
  error: string | null;
}

const TopicInputSection: React.FC<TopicInputSectionProps> = ({
  topic,
  setTopic,
  isGenerating,
  onGenerateQuiz,
  error
}) => {
  return (
    <div className={styles.topicInputSection}>
      <h2>What would you like to learn about?</h2>
      <div className={styles.inputGroup}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g., Photosynthesis, Neural Networks, Ancient Rome..."
          className={styles.topicInput}
          onKeyDown={(e) => e.key === 'Enter' && onGenerateQuiz()}
        />
        <button
          onClick={onGenerateQuiz}
          disabled={isGenerating || !topic.trim()}
          className={styles.generateBtn}
        >
          {isGenerating ? 'Generating Quiz...' : 'Generate Quiz'}
        </button>
      </div>
      {error && <div className={styles.errorMessage}>{error}</div>}
    </div>
  );
};

export default TopicInputSection;
