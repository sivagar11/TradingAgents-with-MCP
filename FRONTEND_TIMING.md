# TradingAgents Frontend - Performance Timing Features

## Overview

The TradingAgents API now includes performance timing tracking to measure how long each agent takes to complete its analysis.

## Backend Changes

### New Backend Version (`api/main_v2.py`)

A new version of the API (`main_v2.py`) has been created with enhanced timing tracking:

**Features:**
- Tracks individual agent execution time
- Measures total analysis duration
- Provides timing summaries in WebSocket messages
- Stores full results with timing data

**Key Endpoints:**
- `GET /` - Health check
- `GET /results/{session_id}` - Retrieve full analysis results with timing data
- `WebSocket /ws/analyze` - Real-time streaming with timing information

### WebSocket Message Format

The WebSocket sends timing information in these formats:

```json
{
  "type": "status",
  "agent": "Market Analyst",
  "status": "completed",
  "duration": "5.32s"
}
```

```json
{
  "type": "final_decision",
  "decision": "BUY",
  "total_duration": "45.67s",
  "agent_timings": {
    "Market Analyst": "5.32s",
    "Social Analyst": "3.21s",
    "News Analyst": "4.15s",
    "Fundamentals Analyst": "6.78s",
    "Research Manager": "8.45s",
    "Trader": "3.92s",
    "Portfolio Manager": "5.84s"
  }
}
```

## Running with Timing

### Start the Timing-Enabled Backend

```bash
# Option 1: Use the v2 startup script
./start-backend-v2.sh

# Option 2: Manual start
source venv/bin/activate
python -m uvicorn api.main_v2:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Updates Needed

To display timing in the frontend, update `src/app/page.tsx`:

1. **Add state for timing:**
```typescript
const [agentTimings, setAgentTimings] = useState<{ [key: string]: string }>({});
const [totalDuration, setTotalDuration] = useState<string | null>(null);
```

2. **Handle timing messages in WebSocket handler:**
```typescript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'status' && message.duration) {
    setAgentTimings(prev => ({
      ...prev,
      [message.agent]: message.duration
    }));
  }
  
  if (message.type === 'final_decision') {
    setTotalDuration(message.total_duration);
    if (message.agent_timings) {
      setAgentTimings(message.agent_timings);
    }
  }
};
```

3. **Display timing using the TimingPanel component:**
```typescript
import TimingPanel from '@/components/TimingPanel';

// In your render:
{Object.keys(agentTimings).length > 0 && (
  <TimingPanel timings={agentTimings} totalDuration={totalDuration} />
)}
```

## Component: TimingPanel

A React component (`src/components/TimingPanel.tsx`) has been created to display timing information beautifully:

```typescript
<TimingPanel 
  timings={{
    "Market Analyst": "5.32s",
    "Social Analyst": "3.21s",
    ...
  }}
  totalDuration="45.67s"
/>
```

## Full Results Endpoint

After analysis completes, you can retrieve the full results with timing data:

```bash
GET /results/{session_id}
```

**Response:**
```json
{
  "ticker": "NVDA",
  "analysis_date": "2024-11-01",
  "final_decision": "BUY",
  "full_report": { ... complete agent state ... },
  "agent_timings": {
    "Market Analyst": 5.32,
    "Social Analyst": 3.21,
    ...
  },
  "total_duration": 45.67
}
```

## Example Usage

### Complete Flow

1. **Start both servers:**
```bash
# Terminal 1 - Backend with timing
./start-backend-v2.sh

# Terminal 2 - Frontend
./start-frontend.sh
```

2. **Run Analysis:**
   - Open http://localhost:3000
   - Enter ticker and date
   - Click "Start Analysis"
   - Watch timing information appear as agents complete

3. **View Results:**
   - Timing appears next to each agent as it completes
   - Total duration shown at the end
   - Timing summary panel displays all agents

## Performance Insights

Typical timing ranges per agent:
- **Analysts (Market, Social, News, Fundamentals)**: 3-8 seconds each
- **Researchers (Bull, Bear)**: 5-10 seconds each
- **Research Manager**: 8-15 seconds
- **Trader**: 3-7 seconds
- **Risk Analysts**: 4-8 seconds each
- **Portfolio Manager**: 5-10 seconds

**Total typical duration**: 40-90 seconds for complete analysis

## Optimization Tips

To improve performance:
1. Use faster LLMs for `shallow_thinker` (e.g., `gpt-4o-mini`)
2. Reduce `research_depth` (debate rounds)
3. Select fewer analysts
4. Use local models with Ollama for faster response

## Troubleshooting

### Timing Not Showing
- Ensure you're using `api/main_v2.py` (not `api/main.py`)
- Check WebSocket connection is successful
- Verify frontend is handling timing messages

### Inaccurate Timing
- Agent timing tracks from report generation, not LLM calls
- Network latency may affect WebSocket message delivery
- Multiple concurrent requests may skew results

## Next Steps

Future enhancements:
- Real-time progress bars
- Historical timing comparisons
- Performance analytics dashboard
- Timing-based recommendations

