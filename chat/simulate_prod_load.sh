#!/bin/bash

ENDPOINT="http://localhost:8000/generate"
PROMPT="Explain in simple terms what leveraged buyouts are."
USERS=("user_0" "user_1" "user_2" "user_3" "user_4" "user_5" "user_6" "user_7" "user_8" "user_9")

while true; do
  # Randomly select a user
  RANDOM_USER=${USERS[$RANDOM % ${#USERS[@]}]}

  # Send the request
  curl -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$PROMPT\", \"max_tokens\": 100, \"user_id\": \"$RANDOM_USER\"}"

  echo -e "\nSent request for $RANDOM_USER"

  # Optional: short sleep to avoid hammering the server too fast
  sleep 3
done
