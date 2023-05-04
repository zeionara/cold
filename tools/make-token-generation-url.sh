#!/bin/bash

client_id=${1:-$COLD_APP_ID}

echo "https://oauth.vk.com/authorize?client_id=$client_id&redirect_uri=https://vk.com/away.php?to=https://oauth.vk.com/blank.html&scope=offline,wall&response_type=token&v=5.131"
