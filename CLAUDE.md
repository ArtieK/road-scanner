# Transportation Comparison App - MVP

## Project Summary

A city-agnostic web app that compares transportation options (rideshare, bikes, scooters, transit) for any trip. Starting with Chicago, designed for easy expansion to NYC.

**Core Value**: Save money by instantly seeing all options (e.g., $18 Uber vs $6 Divvy) without checking multiple apps.

---

## Confirmed Requirements

| Requirement | Decision |
|-------------|----------|
| Target City | Chicago first, city-agnostic architecture |
| Transport Modes | Uber (confirmed API) → Divvy → CTA → Scooters |
| Lyft | Research later |
| Ranking Priority | Cost > Time > Convenience |
| Convenience Definition | Walking distance + wait time only |
| Walking Option | Not included |
| Booking | Deep links to native apps (no in-app payments) |

---

## Tech Stack

- **Frontend**: React + Vite + TypeScript + TanStack Query + Zustand + Tailwind CSS
- **Backend**: Python + FastAPI + Poetry
- **APIs**: Uber Estimates, Divvy GBFS, Google Maps (Places + Directions), CTA
- **Hosting**: Vercel/Netlify (frontend) + Railway/Render (backend)
- **Docker**: From the start (docker-compose for backend + frontend)

---

## Architecture Overview

```
Frontend (React)
    │
    ▼ REST API
Backend (FastAPI)
    │
    ├── Service Orchestrator (parallel API calls)
    │
    ├── City Service Registry (abstraction layer)
    │   ├── ChicagoServices: Uber, Divvy, CTA, Scooters
    │   └── NYCServices: Uber, Citi Bike, MTA (future)
    │
    └── Shared Adapters: Uber, Google Maps, GBFS base
```

**Key Abstraction**: All transportation services implement a common interface. Adding NYC = new config + new adapters extending shared base classes.

---

## Phase 1: Core Value Validation

**Goal**: Prove the concept with Uber + Divvy only.

### Backend Tasks

1. **Project Setup**
   - Initialize FastAPI with Poetry
   - Create folder structure
   - Environment variables for API keys
   - Health check endpoint

2. **Service Abstractions** (`/backend/app/services/base.py`)
   - Define `TransportationService` protocol
   - Define `TransportEstimate` model
   - Define `MicromobilityService` protocol

3. **Uber Integration** (`/backend/app/services/rideshare/uber.py`)[CURRENT]
   - Implement `GET /estimates/price` call
   - Parse response into `TransportEstimate`
   - Deep link generator for Uber app

4. **Divvy Integration** (`/backend/app/services/micromobility/`)
   - `gbfs_base.py`: Base GBFS adapter
   - `divvy.py`: Divvy-specific implementation
   - Fetch station locations + availability
   - Calculate cost: unlock fee + (duration × per-minute rate)
   - Use Google Distance Matrix for ride duration estimate

5. **Orchestrator** (`/backend/app/core/orchestrator.py`)
   - Parallel async calls to Uber + Divvy
   - Aggregate results
   - Rank by cost (cheapest first)

6. **API Endpoint** (`/backend/app/api/v1/compare.py`)
   - `POST /api/v1/compare`
   - Request: `{origin: {lat, lng}, destination: {lat, lng}}`
   - Response: `{results: [...], errors: [...]}`

### Frontend Tasks

7. **Project Setup**
   - Initialize React + Vite + TypeScript
   - Install: TanStack Query, Zustand, Tailwind CSS
   - Basic app structure

8. **Location Input** (`/frontend/src/components/LocationInput/`)
   - Google Places Autocomplete integration
   - Store origin/destination in Zustand
   - Geocode to lat/lng

9. **Compare Hook** (`/frontend/src/hooks/useCompare.ts`)
   - TanStack Query hook for `/api/v1/compare`
   - Handle loading, error, success states

10. **Results Display** (`/frontend/src/components/ResultsList/`)
    - `TransportCard.tsx`: Service name, price, time, book button
    - "Cheapest" badge on lowest-price option
    - Deep link buttons

11. **Basic Polish**
    - Responsive layout
    - Loading spinner
    - Error messages

### Phase 1 Deliverable
User enters two Chicago addresses → sees Uber vs Divvy side-by-side → taps "Book with Uber" → opens Uber app with trip pre-filled.

---

## Phase 2: Full Chicago Experience

1. **CTA Transit** - Google Maps Directions API with `mode=transit`, $2.50 flat fare
2. **Scooters** - Research Lime/Spin APIs, implement if available
3. **Caching** - Redis for GBFS (5 min), Uber estimates (30 sec), geocoding (24 hr)
4. **Error Handling** - Circuit breaker, graceful degradation
5. **Rate Limiting** - Per-user limits, API quota tracking
6. **UI Enhancements** - "Fastest" badge, walking distance display, loading skeletons
7. **Convenience Ranking** - Sort by walking distance + wait time

---

## Phase 3: NYC Expansion

1. **Citi Bike** - Extends `GBFSAdapter` with NYC endpoint
2. **MTA Transit** - Google Maps + $2.90 fare
3. **City Selector UI** - Dropdown, auto-detect from geolocation
4. **Lyft Research** - Evaluate API access, implement if available
5. **Deployment** - CI/CD, monitoring, analytics

---

## Folder Structure

```
road-scanner/
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/v1/
│   │   │   ├── compare.py
│   │   │   └── schemas.py
│   │   ├── core/
│   │   │   ├── orchestrator.py
│   │   │   └── ranking.py
│   │   ├── services/
│   │   │   ├── base.py
│   │   │   ├── rideshare/uber.py
│   │   │   ├── micromobility/
│   │   │   │   ├── gbfs_base.py
│   │   │   │   └── divvy.py
│   │   │   └── transit/google_transit.py
│   │   ├── cities/
│   │   │   ├── registry.py
│   │   │   └── chicago.py
│   │   └── models/
│   │       ├── coordinates.py
│   │       └── estimate.py
│   └── tests/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── api/client.ts
│       ├── hooks/useCompare.ts
│       ├── stores/uiStore.ts
│       ├── components/
│       │   ├── LocationInput/
│       │   └── ResultsList/
│       └── types/
│
└── docker-compose.yml
```

---

## Critical Files to Create First

1. `/backend/app/services/base.py` - Service interface definitions
2. `/backend/app/core/orchestrator.py` - Parallel API coordination
3. `/backend/app/services/rideshare/uber.py` - Uber price estimates
4. `/backend/app/services/micromobility/gbfs_base.py` - Bike share base adapter
5. `/frontend/src/hooks/useCompare.ts` - API integration hook

---

## API Keys Required

- **Uber**: OAuth 2.0 access token (Bearer token)
  - **Important**: Uber no longer offers server tokens - we use OAuth access tokens
  - Token type: `Bearer` (not `Token`)
  - Test environment: `https://test-api.uber.com/v1.2`
  - Production environment: `https://api.uber.com/v1.2` (use test for development)
  - Access tokens expire after 30 days and may require refresh flow
- **Google Maps**: Places API + Directions API + Distance Matrix
- **Divvy**: Public GBFS endpoints (no key needed)
- **CTA**: Free API key from transitchicago.com

---

## Success Criteria

**Phase 1 Complete When**:
- [ ] User can compare Uber vs Divvy for any Chicago trip
- [ ] Results show price + estimated time
- [ ] Deep links open native apps correctly
- [ ] Response time < 3 seconds
