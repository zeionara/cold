#!/bin/bash

path=${1:-assets/default/train.cld}

python -m cold probe "$path" assets/default/spec.yml -u
