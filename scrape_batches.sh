#!/bin/bash

cd scraping_test/scraping_test/spiders 
num_batches=10
for ((i=1; i<=num_batches; i++))
do
    batch_file="../../../domains_batched/domains_batch_$i.csv"
    output_file="../../../output/output_batch_$i.csv"

    echo "Starting batch $i..."
    time scrapy crawl multi_domain_spider -a domains_file="$batch_file" -o "$output_file"

    echo "Batch $i finished!"
done