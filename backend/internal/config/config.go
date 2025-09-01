package config

import (
	"os"
	"strconv"
)

type Config struct {
	Environment   string
	Port          string
	DatabaseURL   string
	RedisURL      string
	
	// Gmail API
	GmailCredentialsPath string
	GmailClientID        string
	GmailClientSecret    string
	GmailRedirectURI     string
	
	// Anthropic API
	AnthropicAPIKey      string
	
	// Agents Service
	AgentsServiceURL     string
	
	// Security
	JWTSecret            string
	SessionSecret        string
	
	// File Storage
	ExcelOutputDir       string
	MaxFileSizeMB        int
	
	// Rate Limiting
	RateLimitRequestsPerMinute int
	GmailAPIRateLimitPerSecond int
}

func New() *Config {
	return &Config{
		Environment:   getEnv("APP_ENV", "development"),
		Port:          getEnv("APP_PORT", "8080"),
		DatabaseURL:   getEnv("DATABASE_URL", "postgresql://user:password@localhost:5432/jobtracker"),
		RedisURL:      getEnv("REDIS_URL", "redis://localhost:6379"),
		
		GmailCredentialsPath: getEnv("GMAIL_CREDENTIALS_PATH", "./credentials/gmail_credentials.json"),
		GmailClientID:        getEnv("GMAIL_CLIENT_ID", ""),
		GmailClientSecret:    getEnv("GMAIL_CLIENT_SECRET", ""),
		GmailRedirectURI:     getEnv("GMAIL_REDIRECT_URI", "http://localhost:8080/auth/gmail/callback"),
		
		AnthropicAPIKey:      getEnv("ANTHROPIC_API_KEY", ""),
		
		AgentsServiceURL:     getEnv("AGENTS_SERVICE_URL", "http://localhost:8000"),
		
		JWTSecret:            getEnv("JWT_SECRET", "your-jwt-secret"),
		SessionSecret:        getEnv("SESSION_SECRET", "your-session-secret"),
		
		ExcelOutputDir:       getEnv("EXCEL_OUTPUT_DIR", "./outputs"),
		MaxFileSizeMB:        getEnvAsInt("MAX_FILE_SIZE_MB", 50),
		
		RateLimitRequestsPerMinute: getEnvAsInt("RATE_LIMIT_REQUESTS_PER_MINUTE", 100),
		GmailAPIRateLimitPerSecond: getEnvAsInt("GMAIL_API_RATE_LIMIT_PER_SECOND", 10),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}
