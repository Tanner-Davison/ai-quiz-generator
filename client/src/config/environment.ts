
export interface EnvironmentConfig {
  apiUrl: string;
  environment: string;
  appName: string;
  isDevelopment: boolean;
  isProduction: boolean;
}

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

export const buildApiUrl = (endpoint: string): string => {
  const config = getEnvironmentConfig();
  const baseUrl = config.apiUrl.replace(/\/$/, '');
  const cleanEndpoint = endpoint.replace(/^\//, '');
  
  return `${baseUrl}/${cleanEndpoint}`;
};

export const log = (message: string, data?: any): void => {
  const config = getEnvironmentConfig();
  
  if (config.isDevelopment) {
    console.log(`[${config.environment.toUpperCase()}] ${message}`, data || '');
  }
};

export const logError = (message: string, error?: any): void => {
  const config = getEnvironmentConfig();
  
  if (config.isDevelopment) {
    console.error(`[${config.environment.toUpperCase()}] ERROR: ${message}`, error || '');
  }
};

export default getEnvironmentConfig;
