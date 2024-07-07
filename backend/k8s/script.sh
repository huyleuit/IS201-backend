#!/bin/bash
export PROJECT_NAME=is210
export REGISTRY_URL=registry-harbor.ngodat0103.me
export namespace=is210
if [ "$1" == "start" ]; then
  kubectl config use-context gke_is210-418312_asia-southeast1_autopilot-cluster-1
  # Use find to recursively find all .yml files
  find . -name "*.yml" | while read file
  do
    # Use envsubst to substitute environment variables
    envsubst < "$file" | kubectl apply -f -
  done
  kubectl config set-context --current --namespace=is210
fi


if [ "$1" == "delete" ]; then
 # Use find to recursively find all .yml files
  find . -name "*.yml" | while read file
  do
    if [ "$file" == "./1-namespace.yml" ]; then
      continue
    fi
    envsubst < "$file" | kubectl delete -f -
  done
fi
