#!/bin/bash

ENDPOINT="http://localhost:8000/generate"
PROMPT="Explain in simple terms what leveraged buyouts are."
USERS=("user_0" "user_1" "user_2" "user_3" "user_4" "user_5" "user_6" "user_7" "user_8" "user_9")

CONCURRENT_REQUESTS=10

while true; do
  for ((i=1; i<=CONCURRENT_REQUESTS; i++)); do
    RANDOM_USER=${USERS[$RANDOM % ${#USERS[@]}]}

    curl -X POST "$ENDPOINT" \
      -H "Content-Type: application/json" \
      -d "{\"prompt\": \"$PROMPT\", \"max_tokens\": 100, \"user_id\": \"$RANDOM_USER\"}" &

    echo -e "Sent request #$i for $RANDOM_USER"
  done

  # Wait for all background curl processes to finish
  wait
done
