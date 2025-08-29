# CSS Modules

This folder contains all CSS module files for the AI Quiz Generator application.

## Structure

- `App.module.css` - Main application styles with global CSS reset
- `TopicInputSection.module.css` - Topic input form styling
- `QuizSection.module.css` - Quiz section layout and action buttons
- `QuestionCard.module.css` - Individual question card styling
- `ResultsSection.module.css` - Quiz results display styling
- `HistorySection.module.css` - Quiz history section styling

## Usage

All CSS modules are exported through the barrel export in `index.ts`:

```typescript
import { AppStyles, TopicInputSectionStyles } from '../cssmodules';

// Use with alias for cleaner code
const styles = AppStyles;
```

## Benefits

- **Scoped styling**: CSS class names are automatically scoped to prevent conflicts
- **Better organization**: All styling files are centralized in one folder
- **Clean imports**: Single import statement for all styles
- **Type safety**: TypeScript support for CSS module imports
- **Maintainability**: Easy to find and update styles

## Naming Convention

CSS modules use camelCase naming to match JavaScript conventions:
- `.topicInputSection` instead of `.topic-input-section`
- `.generateBtn` instead of `.generate-btn`
- `.questionCard` instead of `.question-card`
