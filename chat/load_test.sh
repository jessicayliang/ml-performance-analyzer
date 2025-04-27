#!/bin/bash

# Number of requests you want to send in parallel
N=10

# Function to send request
send_request() {
  local req_num=$1
  local user_id="user_${req_num}"

  local payload=$(jq -n --arg uid "$user_id" '{
    prompt: "Write me a short paragraph about Economics.",
    max_tokens: 50,
    user_id: $uid
  }')

  curl -s -X POST "http://localhost:8000/generate" \
    -H "Content-Type: application/json" \
    -d "$payload" > /dev/null
}

# Main loop
for i in $(seq 1 $N); do
  send_request "$i" &
done

# Wait for all background jobs to finish
wait

echo "Sent $N concurrent requests to localhost:8000/generate!"
