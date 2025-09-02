import React from 'react';
import { TopicInputSectionStyles as styles } from '../cssmodules';

interface TopicInputSectionProps {
  topic: string;
  setTopic: (topic: string) => void;
  isGenerating: boolean;
  onGenerateQuiz: () => void;
  onGenerateEnhancedQuiz?: () => void;
  error: string | null;
}

const TopicInputSection: React.FC<TopicInputSectionProps> = ({
  topic,
  setTopic,
  isGenerating,
  onGenerateQuiz,
  onGenerateEnhancedQuiz,
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
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={onGenerateQuiz}
            disabled={isGenerating || !topic.trim()}
            className={styles.generateBtn}
            style={{ flex: 1 }}
          >
            {isGenerating ? 'Generating Quiz...' : 'Generate Quiz'}
          </button>
          {onGenerateEnhancedQuiz && (
            <button
              onClick={onGenerateEnhancedQuiz}
              disabled={isGenerating || !topic.trim()}
              style={{
                flex: 1,
                padding: '12px 16px',
                backgroundColor: '#0ea5e9',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: isGenerating || !topic.trim() ? 'not-allowed' : 'pointer',
                opacity: isGenerating || !topic.trim() ? 0.6 : 1,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <span>📚</span>
              {isGenerating ? 'Enhancing...' : 'Enhanced Quiz'}
            </button>
          )}
        </div>
      </div>
      {error && <div className={styles.errorMessage}>{error}</div>}
    </div>
  );
};

export default TopicInputSection;
