curl -XPOST 'host.docker.internal:9200/emails/_bulk' -H "Content-Type: application/json" --data-binary @emails.json
curl -XPOST 'host.docker.internal:9200/questions/_bulk' -H "Content-Type: application/json" --data-binary @questions.json
curl -XPOST 'host.docker.internal:9200/newsletter/_bulk' -H "Content-Type: application/json" --data-binary @newsletter.json
