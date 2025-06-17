#!/usr/bin/env bash

###############################################################################
# Service control script.                                                     #
# Installs, configures, and uninstalls OpenSearch and its dashboards.         #
###############################################################################

function install() {
  docker run -d --name opensearch \
    -p 9200:9200 -p 9600:9600 \
    -e "discovery.type=single-node" \
    -e "DISABLE_SECURITY_PLUGIN=true" \
    opensearchproject/opensearch:2.11.0

  docker run -d --name opensearch-dashboards \
    -p 5601:5601 \
    --link opensearch:opensearch \
    -e "OPENSEARCH_HOSTS=http://opensearch:9200" \
    -e "DISABLE_SECURITY_DASHBOARDS_PLUGIN=true" \
    opensearchproject/opensearch-dashboards:2.11.0
}

function configure() {
  curl -XPUT \
    "http://localhost:9200/_search/pipeline/nlp-search-pipeline" \
    -H 'Content-Type: application/json' \
    -d'
  {
    "description": "Post processor for hybrid search",
    "phase_results_processors": [
      {
        "normalization-processor": {
          "normalization": {
            "technique": "min_max"
          },
          "combination": {
            "technique": "arithmetic_mean",
            "parameters": {
              "weights": [
                0.3,
                0.7
              ]
            }
          }
        }
      }
    ]
  }
  '
}

function uninstall() {
  docker container stop opensearch
  docker container stop opensearch-dashboards
  docker container prune
}

if [[ -z "${1}" ]]; then
  echo "Please specify a command."
  exit 1
fi

case "${1}" in
  up)
    install
    ;;

  cfg)
    configure
    ;;

  down)
    uninstall
    ;;

  *)
    echo "Unknown command: ${1}."
    exit 1
    ;;
esac
exit 0
