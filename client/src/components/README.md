# Components

This folder contains all the React components for the AI Quiz Generator application.

## Component Structure

### Core Components

- **TopicInputSection** - Handles topic input and quiz generation
- **QuizSection** - Displays quiz questions and handles quiz taking
- **ResultsSection** - Shows quiz results and feedback
- **HistorySection** - Displays quiz history
- **QuestionCard** - Individual quiz question component

### Component Hierarchy

```
App
├── TopicInputSection (when no quiz)
├── QuizSection (when taking quiz)
│   └── QuestionCard (multiple)
├── ResultsSection (when quiz completed)
└── HistorySection (always visible if history exists)
```

### Props Interface

Each component follows a clear props interface pattern:

- **TopicInputSection**: `topic`, `setTopic`, `isGenerating`, `onGenerateQuiz`, `error`
- **QuizSection**: `quiz`, `userAnswers`, `onAnswerSelect`, `onSubmitQuiz`, `onStartNewQuiz`
- **QuestionCard**: `question`, `questionIndex`, `userAnswer`, `onAnswerSelect`
- **ResultsSection**: `results`, `quiz`, `onStartNewQuiz`
- **HistorySection**: `quizHistory`

### Type Safety

All components use TypeScript interfaces defined in `../types/quiz.ts` for type safety and consistency.

### Utilities

Common utility functions like `getScoreColor` are centralized in `../utils/scoreUtils.ts` to avoid duplication.

### Styling

All components use CSS classes defined in `App.css` for consistent styling across the application.
