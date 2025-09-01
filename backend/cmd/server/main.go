package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/jobtracker/backend/internal/config"
	"github.com/jobtracker/backend/internal/handlers"
	"github.com/jobtracker/backend/internal/services"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	// Initialize configuration
	cfg := config.New()

	// Initialize services
	gmailService := services.NewGmailService(cfg)
	agentService := services.NewAgentService(cfg)
	dbService := services.NewDatabaseService(cfg)

	// Initialize handlers
	handler := handlers.New(cfg, gmailService, agentService, dbService)

	// Setup Gin router
	if cfg.Environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}
	
	router := gin.Default()

	// CORS middleware
	router.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Credentials", "true")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Header("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "job-application-tracker-backend",
			"version": "1.0.0",
		})
	})

	// API routes
	v1 := router.Group("/api/v1")
	{
		// GraphQL endpoint
		v1.POST("/graphql", handler.GraphQL())
		v1.GET("/graphql", handler.GraphQLPlayground())
		
		// WebSocket endpoint for real-time updates
		v1.GET("/ws", handler.WebSocket())
		
		// OAuth endpoints
		auth := v1.Group("/auth")
		{
			auth.GET("/gmail", handler.InitiateGmailAuth())
			auth.GET("/gmail/callback", handler.HandleGmailCallback())
			auth.POST("/logout", handler.Logout())
		}
	}

	// Create HTTP server
	srv := &http.Server{
		Addr:    ":" + cfg.Port,
		Handler: router,
	}

	// Start server in a goroutine
	go func() {
		log.Printf("Server starting on port %s", cfg.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	// Give outstanding requests 30 seconds to complete
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited")
}
