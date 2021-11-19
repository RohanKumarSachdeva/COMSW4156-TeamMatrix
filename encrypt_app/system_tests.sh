#!/bin/sh -e
#
# Description: Build script for system-level tests exercising every API entry point

API_SERVER="0.0.0.0:5001"

# /generate endpoint
RESPONSE=$(curl -s -X GET "${API_SERVER}/generate")
resp_message=$(echo $RESPONSE | jq -r '.message')
echo "Password ${resp_message} generated successfully using /generate endpoint"
echo "/generate endpoint test passed"
sleep 1

# /create endpoint
APP_NAME="testapp"
DUMMY_PASSWORD="passcode123"
RESPONSE=$(curl -s -X POST "${API_SERVER}/create?application=${APP_NAME}&password=${DUMMY_PASSWORD}")

resp_message=$(echo $RESPONSE | jq -r '.message')

if [ "${resp_message}" == "Password created successfully!" ]; then
    echo "/create endpoint test passed"
else
    echo "/create endpoint test failed"
    exit 1
fi

sleep 1

RESPONSE=$(curl -s -X GET "${API_SERVER}/retrieve?application=${APP_NAME}")
X=$(echo $RESPONSE | jq -r '.message')
resp_message=$(echo $RESPONSE | jq -r '.message')

if [[ $resp_message == *"${DUMMY_PASSWORD}"* ]]; then
    echo "/retrieve endpoint test passed"
else
    echo "/retrieve endpoint test failed"
    exit 1
fi


NEW_PASSWORD="password987"
RESPONSE=$(curl -s -X POST "${API_SERVER}/update?application=${APP_NAME}&password=${NEW_PASSWORD}")
resp_message=$(echo $RESPONSE | jq -r '.message')
if [ "${resp_message}" == "Password updated successfully!" ]; then
    echo "/update endpoint test passed"
else
    echo "/update endpoint test failed"
    exit 1
fi

sleep 1

RESPONSE=$(curl -s -X DELETE "${API_SERVER}/delete?application=${APP_NAME}")
resp_message=$(echo $RESPONSE | jq -r '.message')
if [ "${resp_message}" == "Deleted passwords for ${APP_NAME} application(s)." ]; then
    echo "/delete endpoint test passed"
else
    echo "/delete endpoint test failed"
    exit 1
fi
