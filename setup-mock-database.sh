#!/bin/bash

# Mock Database Setup Script for AI Test Generator
# This script creates a PostgreSQL database with sample data matching the app structure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="ai_quiz_db"
DB_USER="postgres"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5433"
DB_CONTAINER_NAME="ai-quiz-db"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if PostgreSQL container is running
check_postgres_container() {
    if docker ps | grep -q "$DB_CONTAINER_NAME"; then
        return 0
    else
        return 1
    fi
}

# Function to start PostgreSQL container
start_postgres_container() {
    print_status "Starting PostgreSQL container..."
    
    if check_postgres_container; then
        print_warning "PostgreSQL container is already running"
        return 0
    fi
    
    # Check if container exists but is stopped
    if docker ps -a | grep -q "$DB_CONTAINER_NAME"; then
        print_status "Starting existing PostgreSQL container..."
        docker start "$DB_CONTAINER_NAME"
    else
        print_status "Creating new PostgreSQL container..."
        docker run -d \
            --name "$DB_CONTAINER_NAME" \
            -e POSTGRES_USER="$DB_USER" \
            -e POSTGRES_PASSWORD="$DB_PASSWORD" \
            -e POSTGRES_DB="postgres" \
            -p "$DB_PORT:5432" \
            postgres:15-alpine
    fi
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    sleep 5
    
    # Test connection
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker exec "$DB_CONTAINER_NAME" pg_isready -U "$DB_USER" >/dev/null 2>&1; then
            print_success "PostgreSQL is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - waiting for PostgreSQL..."
        sleep 2
        ((attempt++))
    done
    
    print_error "PostgreSQL failed to start within expected time"
    exit 1
}

# Function to create database
create_database() {
    print_status "Creating database '$DB_NAME'..."
    
    # Create database if it doesn't exist
    docker exec "$DB_CONTAINER_NAME" psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true
    
    print_success "Database '$DB_NAME' is ready"
}

# Function to create tables
create_tables() {
    print_status "Creating database tables..."
    
    # Create tables SQL
    local create_tables_sql="
    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
    
    -- Create quizzes table
    CREATE TABLE IF NOT EXISTS quizzes (
        id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
        topic VARCHAR(255) NOT NULL,
        model VARCHAR(100),
        temperature FLOAT DEFAULT 0.2,
        wikipedia_enhanced BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE
    );
    
    -- Create quiz_questions table
    CREATE TABLE IF NOT EXISTS quiz_questions (
        id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
        quiz_id VARCHAR NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
        question TEXT NOT NULL,
        options JSON NOT NULL,
        correct_answer INTEGER NOT NULL,
        explanation TEXT,
        question_order INTEGER DEFAULT 0
    );
    
    -- Create quiz_submissions table
    CREATE TABLE IF NOT EXISTS quiz_submissions (
        id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
        quiz_id VARCHAR NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
        user_id VARCHAR(100),
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        percentage FLOAT NOT NULL,
        submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create quiz_answers table
    CREATE TABLE IF NOT EXISTS quiz_answers (
        id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
        submission_id VARCHAR NOT NULL REFERENCES quiz_submissions(id) ON DELETE CASCADE,
        question_id VARCHAR NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
        user_answer INTEGER NOT NULL,
        is_correct BOOLEAN NOT NULL
    );
    
    -- Create chat_sessions table
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
        user_id VARCHAR(100),
        model VARCHAR(100),
        system_prompt TEXT DEFAULT 'You are a helpful assistant.',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE
    );
    
    -- Create chat_messages table
    CREATE TABLE IF NOT EXISTS chat_messages (
        id VARCHAR PRIMARY KEY DEFAULT uuid_generate_v4()::text,
        session_id VARCHAR NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
        role VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        model VARCHAR(100),
        usage JSON,
        finish_reason VARCHAR(100)
    );
    
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_quiz_questions_quiz_id ON quiz_questions(quiz_id);
    CREATE INDEX IF NOT EXISTS idx_quiz_submissions_quiz_id ON quiz_submissions(quiz_id);
    CREATE INDEX IF NOT EXISTS idx_quiz_answers_submission_id ON quiz_answers(submission_id);
    CREATE INDEX IF NOT EXISTS idx_quiz_answers_question_id ON quiz_answers(question_id);
    CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
    CREATE INDEX IF NOT EXISTS idx_quizzes_created_at ON quizzes(created_at);
    CREATE INDEX IF NOT EXISTS idx_quiz_submissions_submitted_at ON quiz_submissions(submitted_at);
    "
    
    # Execute SQL
    docker exec "$DB_CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "$create_tables_sql"
    
    print_success "Database tables created successfully"
}

# Function to insert sample data
insert_sample_data() {
    print_status "Inserting sample data..."
    
    # Sample data SQL
    local sample_data_sql="
    -- Insert sample quizzes
    INSERT INTO quizzes (id, topic, model, temperature, wikipedia_enhanced, created_at) VALUES
    ('quiz-001', 'Python Programming Basics', 'llama-3.1-70b-versatile', 0.2, true, NOW() - INTERVAL '2 days'),
    ('quiz-002', 'React Hooks and State Management', 'llama-3.1-70b-versatile', 0.3, false, NOW() - INTERVAL '1 day'),
    ('quiz-003', 'Database Design Principles', 'llama-3.1-70b-versatile', 0.1, true, NOW() - INTERVAL '3 hours'),
    ('quiz-004', 'Machine Learning Fundamentals', 'llama-3.1-70b-versatile', 0.4, true, NOW() - INTERVAL '1 hour'),
    ('quiz-005', 'Docker and Containerization', 'llama-3.1-70b-versatile', 0.2, false, NOW() - INTERVAL '30 minutes')
    ON CONFLICT (id) DO NOTHING;
    
    -- Insert sample quiz questions for Python quiz
    INSERT INTO quiz_questions (id, quiz_id, question, options, correct_answer, explanation, question_order) VALUES
    ('q-001', 'quiz-001', 'What is the correct way to create a list in Python?', '[\"list()\", \"[]\", \"new list()\", \"List()\"]', 1, 'In Python, you can create a list using square brackets [] or the list() constructor.', 1),
    ('q-002', 'quiz-001', 'Which keyword is used to define a function in Python?', '[\"function\", \"def\", \"func\", \"define\"]', 1, 'The \"def\" keyword is used to define functions in Python.', 2),
    ('q-003', 'quiz-001', 'What does the len() function return?', '[\"The last element\", \"The number of elements\", \"The first element\", \"A boolean value\"]', 1, 'The len() function returns the number of elements in a sequence.', 3),
    ('q-004', 'quiz-001', 'Which of the following is a mutable data type?', '[\"tuple\", \"string\", \"list\", \"frozenset\"]', 2, 'Lists are mutable, meaning their contents can be changed after creation.', 4),
    ('q-005', 'quiz-001', 'What is the output of: print(2 ** 3)?', '[\"6\", \"8\", \"9\", \"5\"]', 1, 'The ** operator is used for exponentiation, so 2 ** 3 = 8.', 5)
    ON CONFLICT (id) DO NOTHING;
    
    -- Insert sample quiz questions for React quiz
    INSERT INTO quiz_questions (id, quiz_id, question, options, correct_answer, explanation, question_order) VALUES
    ('q-006', 'quiz-002', 'Which hook is used to manage state in functional components?', '[\"useState\", \"useEffect\", \"useContext\", \"useReducer\"]', 0, 'useState is the primary hook for managing local state in functional components.', 1),
    ('q-007', 'quiz-002', 'When does useEffect run by default?', '[\"Only on mount\", \"After every render\", \"Only on unmount\", \"Never\"]', 1, 'useEffect runs after every render by default, unless dependencies are specified.', 2),
    ('q-008', 'quiz-002', 'What is the purpose of the dependency array in useEffect?', '[\"To specify which props to watch\", \"To control when the effect runs\", \"To pass data to the effect\", \"To clean up resources\"]', 1, 'The dependency array controls when the effect should re-run.', 3),
    ('q-009', 'quiz-002', 'Which hook is used to share state between components?', '[\"useState\", \"useEffect\", \"useContext\", \"useMemo\"]', 2, 'useContext is used to share state between components without prop drilling.', 4),
    ('q-010', 'quiz-002', 'What does useCallback return?', '[\"A memoized value\", \"A memoized callback function\", \"A state value\", \"An effect cleanup function\"]', 1, 'useCallback returns a memoized version of the callback function.', 5)
    ON CONFLICT (id) DO NOTHING;
    
    -- Insert sample quiz submissions
    INSERT INTO quiz_submissions (id, quiz_id, user_id, score, total_questions, percentage, submitted_at) VALUES
    ('sub-001', 'quiz-001', 'user-123', 4, 5, 80.0, NOW() - INTERVAL '1 day'),
    ('sub-002', 'quiz-001', 'user-456', 3, 5, 60.0, NOW() - INTERVAL '12 hours'),
    ('sub-003', 'quiz-002', 'user-123', 5, 5, 100.0, NOW() - INTERVAL '6 hours'),
    ('sub-004', 'quiz-002', 'user-789', 2, 5, 40.0, NOW() - INTERVAL '2 hours'),
    ('sub-005', 'quiz-003', 'user-456', 4, 5, 80.0, NOW() - INTERVAL '1 hour')
    ON CONFLICT (id) DO NOTHING;
    
    -- Insert sample quiz answers
    INSERT INTO quiz_answers (id, submission_id, question_id, user_answer, is_correct) VALUES
    ('a-001', 'sub-001', 'q-001', 1, true),
    ('a-002', 'sub-001', 'q-002', 1, true),
    ('a-003', 'sub-001', 'q-003', 1, true),
    ('a-004', 'sub-001', 'q-004', 2, true),
    ('a-005', 'sub-001', 'q-005', 0, false),
    ('a-006', 'sub-002', 'q-001', 1, true),
    ('a-007', 'sub-002', 'q-002', 1, true),
    ('a-008', 'sub-002', 'q-003', 1, true),
    ('a-009', 'sub-002', 'q-004', 0, false),
    ('a-010', 'sub-002', 'q-005', 0, false),
    ('a-011', 'sub-003', 'q-006', 0, true),
    ('a-012', 'sub-003', 'q-007', 1, true),
    ('a-013', 'sub-003', 'q-008', 1, true),
    ('a-014', 'sub-003', 'q-009', 2, true),
    ('a-015', 'sub-003', 'q-010', 1, true)
    ON CONFLICT (id) DO NOTHING;
    
    -- Insert sample chat sessions
    INSERT INTO chat_sessions (id, user_id, model, system_prompt, created_at) VALUES
    ('chat-001', 'user-123', 'llama-3.1-70b-versatile', 'You are a helpful programming tutor.', NOW() - INTERVAL '2 days'),
    ('chat-002', 'user-456', 'llama-3.1-70b-versatile', 'You are an expert in web development.', NOW() - INTERVAL '1 day'),
    ('chat-003', 'user-789', 'llama-3.1-70b-versatile', 'You are a database design specialist.', NOW() - INTERVAL '3 hours')
    ON CONFLICT (id) DO NOTHING;
    
    -- Insert sample chat messages
    INSERT INTO chat_messages (id, session_id, role, content, created_at, model, usage, finish_reason) VALUES
    ('msg-001', 'chat-001', 'user', 'Can you explain how Python decorators work?', NOW() - INTERVAL '2 days', 'llama-3.1-70b-versatile', '{\"prompt_tokens\": 15, \"completion_tokens\": 150}', 'stop'),
    ('msg-002', 'chat-001', 'assistant', 'Python decorators are a powerful feature that allows you to modify or extend the behavior of functions or classes without permanently modifying their code. They are essentially functions that take another function as an argument and return a modified version of that function...', NOW() - INTERVAL '2 days', 'llama-3.1-70b-versatile', '{\"prompt_tokens\": 15, \"completion_tokens\": 150}', 'stop'),
    ('msg-003', 'chat-002', 'user', 'What are the best practices for React state management?', NOW() - INTERVAL '1 day', 'llama-3.1-70b-versatile', '{\"prompt_tokens\": 12, \"completion_tokens\": 200}', 'stop'),
    ('msg-004', 'chat-002', 'assistant', 'Here are some key best practices for React state management: 1. Keep state as local as possible - only lift state up when multiple components need it. 2. Use useState for simple local state. 3. Use useReducer for complex state logic. 4. Consider Context API for sharing state across many components...', NOW() - INTERVAL '1 day', 'llama-3.1-70b-versatile', '{\"prompt_tokens\": 12, \"completion_tokens\": 200}', 'stop'),
    ('msg-005', 'chat-003', 'user', 'How do I design a normalized database schema?', NOW() - INTERVAL '3 hours', 'llama-3.1-70b-versatile', '{\"prompt_tokens\": 18, \"completion_tokens\": 180}', 'stop'),
    ('msg-006', 'chat-003', 'assistant', 'Database normalization is the process of organizing data to minimize redundancy and dependency. Here are the main normal forms: 1NF - Each column contains atomic values. 2NF - All non-key attributes are fully functionally dependent on the primary key. 3NF - No transitive dependencies...', NOW() - INTERVAL '3 hours', 'llama-3.1-70b-versatile', '{\"prompt_tokens\": 18, \"completion_tokens\": 180}', 'stop')
    ON CONFLICT (id) DO NOTHING;
    "
    
    # Execute SQL
    docker exec "$DB_CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "$sample_data_sql"
    
    print_success "Sample data inserted successfully"
}

# Function to validate database setup
validate_database() {
    print_status "Validating database setup..."
    
    # Check if tables exist and have data
    local validation_sql="
    SELECT 
        'quizzes' as table_name, 
        COUNT(*) as record_count 
    FROM quizzes
    UNION ALL
    SELECT 
        'quiz_questions' as table_name, 
        COUNT(*) as record_count 
    FROM quiz_questions
    UNION ALL
    SELECT 
        'quiz_submissions' as table_name, 
        COUNT(*) as record_count 
    FROM quiz_submissions
    UNION ALL
    SELECT 
        'quiz_answers' as table_name, 
        COUNT(*) as record_count 
    FROM quiz_answers
    UNION ALL
    SELECT 
        'chat_sessions' as table_name, 
        COUNT(*) as record_count 
    FROM chat_sessions
    UNION ALL
    SELECT 
        'chat_messages' as table_name, 
        COUNT(*) as record_count 
    FROM chat_messages;
    "
    
    print_status "Database validation results:"
    docker exec "$DB_CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "$validation_sql"
    
    print_success "Database validation completed"
}

# Function to create environment file
create_env_file() {
    print_status "Creating environment configuration file..."
    
    local env_content="# Mock Database Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Database Configuration (Mock Database)
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME

# API Keys (Mock values for development)
GROQ_API_KEY=mock_groq_api_key_for_development

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Origins (Development)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:4173,http://localhost:8080

# Development-specific settings
SKIP_DB_INIT=false
LOG_LEVEL=DEBUG
"
    
    echo "$env_content" > mock-database.env
    
    print_success "Environment file created: mock-database.env"
}

# Function to display connection information
display_connection_info() {
    print_success "Mock database setup completed successfully!"
    echo ""
    echo -e "${GREEN}Database Connection Information:${NC}"
    echo "  Host: $DB_HOST"
    echo "  Port: $DB_PORT"
    echo "  Database: $DB_NAME"
    echo "  Username: $DB_USER"
    echo "  Password: $DB_PASSWORD"
    echo ""
    echo -e "${GREEN}Connection String:${NC}"
    echo "  postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    echo ""
    echo -e "${GREEN}Environment File:${NC}"
    echo "  mock-database.env"
    echo ""
    echo -e "${GREEN}Useful Commands:${NC}"
    echo "  Connect to database: docker exec -it $DB_CONTAINER_NAME psql -U $DB_USER -d $DB_NAME"
    echo "  View logs: docker logs $DB_CONTAINER_NAME"
    echo "  Stop container: docker stop $DB_CONTAINER_NAME"
    echo "  Start container: docker start $DB_CONTAINER_NAME"
    echo "  Remove container: docker rm -f $DB_CONTAINER_NAME"
    echo ""
    echo -e "${YELLOW}Note:${NC} This is a mock database for development purposes only."
    echo "  Do not use this configuration in production!"
}

# Function to cleanup on exit
cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Setup failed. You may need to clean up manually:"
        echo "  docker rm -f $DB_CONTAINER_NAME"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  AI Test Generator Mock DB Setup${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    # Set up cleanup trap
    trap cleanup EXIT
    
    # Check prerequisites
    check_docker
    
    # Start PostgreSQL container
    start_postgres_container
    
    # Create database
    create_database
    
    # Create tables
    create_tables
    
    # Insert sample data
    insert_sample_data
    
    # Validate setup
    validate_database
    
    # Create environment file
    create_env_file
    
    # Display connection information
    display_connection_info
}

# Handle command line arguments
case "${1:-}" in
    "stop")
        print_status "Stopping mock database container..."
        docker stop "$DB_CONTAINER_NAME" 2>/dev/null || true
        print_success "Mock database container stopped"
        ;;
    "start")
        print_status "Starting mock database container..."
        docker start "$DB_CONTAINER_NAME" 2>/dev/null || true
        print_success "Mock database container started"
        ;;
    "restart")
        print_status "Restarting mock database container..."
        docker restart "$DB_CONTAINER_NAME" 2>/dev/null || true
        print_success "Mock database container restarted"
        ;;
    "remove")
        print_status "Removing mock database container..."
        docker rm -f "$DB_CONTAINER_NAME" 2>/dev/null || true
        print_success "Mock database container removed"
        ;;
    "status")
        if check_postgres_container; then
            print_success "Mock database container is running"
            docker exec "$DB_CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT 'Database is accessible' as status;"
        else
            print_warning "Mock database container is not running"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  - Set up mock database (default)"
        echo "  start      - Start the mock database container"
        echo "  stop       - Stop the mock database container"
        echo "  restart    - Restart the mock database container"
        echo "  remove     - Remove the mock database container"
        echo "  status     - Check the status of the mock database"
        echo "  help       - Show this help message"
        echo ""
        echo "The script will create a PostgreSQL container with sample data"
        echo "matching your AI Test Generator application structure."
        ;;
    *)
        main
        ;;
esac
