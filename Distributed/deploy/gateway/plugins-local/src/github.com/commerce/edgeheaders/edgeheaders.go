// Package edgeheaders is a local Traefik middleware.
//
// prepare: drop client identity headers, normalize X-Correlation-Id, and stamp
// that id plus the storefront CORS headers onto the response.
// cors: answer OPTIONS here so a browser preflight never reaches the JWT check
// or an upstream. The allow-list is not *.
//
// This package does not read orders, prices, stock, or roles.
package edgeheaders

import (
	"context"
	"crypto/rand"
	"errors"
	"fmt"
	"net/http"
)

// Config is the plugin block in the dynamic configuration.
type Config struct {
	Mode          string   `json:"mode,omitempty"`
	StripHeaders  []string `json:"stripHeaders,omitempty"`
	AllowOrigins  []string `json:"allowOrigins,omitempty"`
	AllowMethods  string   `json:"allowMethods,omitempty"`
	AllowHeaders  string   `json:"allowHeaders,omitempty"`
	ExposeHeaders string   `json:"exposeHeaders,omitempty"`
}

// CreateConfig is the constructor Traefik looks up.
func CreateConfig() *Config {
	return &Config{}
}

type middleware struct {
	next   http.Handler
	config *Config
}

// New builds the middleware. mode is prepare or cors.
func New(_ context.Context, next http.Handler, config *Config, _ string) (http.Handler, error) {
	if config == nil {
		return nil, errors.New("edgeheaders config is missing")
	}
	if config.Mode != "prepare" && config.Mode != "cors" {
		return nil, errors.New("edgeheaders mode must be prepare or cors")
	}
	return &middleware{next: next, config: config}, nil
}

func (m *middleware) ServeHTTP(rw http.ResponseWriter, req *http.Request) {
	if m.config.Mode == "cors" {
		if req.Method == http.MethodOptions {
			rw.WriteHeader(http.StatusNoContent)
			return
		}
		m.next.ServeHTTP(rw, req)
		return
	}

	for _, name := range m.config.StripHeaders {
		req.Header.Del(name)
	}
	raw := req.Header.Get("X-Correlation-Id")
	id := raw
	if !isUUID(raw) {
		generated, err := uuid4()
		if err != nil {
			http.Error(rw, "correlation id unavailable", http.StatusInternalServerError)
			return
		}
		id = generated
	}
	req.Header.Set("X-Correlation-Id", id)
	origin := req.Header.Get("Origin")
	wrapped := &stamp{
		ResponseWriter: rw,
		id:             id,
		origin:         origin,
		originAllowed:  originAllowed(m.config.AllowOrigins, origin),
		allowMethods:   m.config.AllowMethods,
		allowHeaders:   m.config.AllowHeaders,
		exposeHeaders:  m.config.ExposeHeaders,
	}
	m.next.ServeHTTP(wrapped, req)
}

type stamp struct {
	http.ResponseWriter
	id            string
	origin        string
	originAllowed bool
	allowMethods  string
	allowHeaders  string
	exposeHeaders string
	wrote         bool
}

func (s *stamp) WriteHeader(code int) {
	if s.wrote {
		return
	}
	s.wrote = true
	header := s.ResponseWriter.Header()
	header.Set("X-Correlation-Id", s.id)
	if s.originAllowed {
		header.Set("Access-Control-Allow-Origin", s.origin)
		header.Set("Vary", "Origin")
		header.Set("Access-Control-Allow-Methods", s.allowMethods)
		header.Set("Access-Control-Allow-Headers", s.allowHeaders)
		header.Set("Access-Control-Expose-Headers", s.exposeHeaders)
		header.Set("Access-Control-Max-Age", "600")
	} else {
		header.Del("Access-Control-Allow-Origin")
	}
	s.ResponseWriter.WriteHeader(code)
}

func (s *stamp) Write(body []byte) (int, error) {
	if !s.wrote {
		s.WriteHeader(http.StatusOK)
	}
	return s.ResponseWriter.Write(body)
}

func originAllowed(origins []string, origin string) bool {
	if origin == "" {
		return false
	}
	for _, allowed := range origins {
		if allowed == origin {
			return true
		}
	}
	return false
}

func isUUID(value string) bool {
	if len(value) != 36 {
		return false
	}
	for index, char := range value {
		switch index {
		case 8, 13, 18, 23:
			if char != '-' {
				return false
			}
		default:
			if !isHex(char) {
				return false
			}
		}
	}
	return true
}

func isHex(char rune) bool {
	if char >= '0' && char <= '9' {
		return true
	}
	if char >= 'a' && char <= 'f' {
		return true
	}
	return char >= 'A' && char <= 'F'
}

func uuid4() (string, error) {
	var buf [16]byte
	if _, err := rand.Read(buf[:]); err != nil {
		return "", err
	}
	buf[6] = (buf[6] & 0x0f) | 0x40
	buf[8] = (buf[8] & 0x3f) | 0x80
	return fmt.Sprintf("%x-%x-%x-%x-%x", buf[0:4], buf[4:6], buf[6:8], buf[8:10], buf[10:16]), nil
}
