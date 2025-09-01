// Environment configuration utility
export interface EnvironmentConfig {
  apiUrl: string;
  environment: string;
  appName: string;
  isDevelopment: boolean;
  isProduction: boolean;
}

// Get environment configuration
export const getEnvironmentConfig = (): EnvironmentConfig => {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const environment = import.meta.env.VITE_ENVIRONMENT || 'development';
  const appName = import.meta.env.VITE_APP_NAME || 'AI Quiz Generator';
  
  return {
    apiUrl,
    environment,
    appName,
    isDevelopment: environment === 'development',
    isProduction: environment === 'production',
  };
};

// API URL builder
export const buildApiUrl = (endpoint: string): string => {
  const config = getEnvironmentConfig();
  const baseUrl = config.apiUrl.replace(/\/$/, ''); // Remove trailing slash
  const cleanEndpoint = endpoint.replace(/^\//, ''); // Remove leading slash
  
  return `${baseUrl}/${cleanEndpoint}`;
};

// Environment-specific logging
export const log = (message: string, data?: any): void => {
  const config = getEnvironmentConfig();
  
  if (config.isDevelopment) {
    console.log(`[${config.environment.toUpperCase()}] ${message}`, data || '');
  }
};

// Environment-specific error logging
export const logError = (message: string, error?: any): void => {
  const config = getEnvironmentConfig();
  
  if (config.isDevelopment) {
    console.error(`[${config.environment.toUpperCase()}] ERROR: ${message}`, error || '');
  }
};

export default getEnvironmentConfig;
