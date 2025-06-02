# Progress Tracker

## Todos

- Restructure adapter data to match crawl data or do pipeline transform?
- Add crawler for open game resource
- Add crawler for spriters-resource
- Add crawler for itch.io
- Add crawler for booru
- Data aggregation

## Notes

- ML filtering
- ML processing
- ML deduplication
- Add crawler for X

## Done

- How to aggregate data across multiple route handlers?
  - Use request.user_data to push and pop the data. Downside is data needs to be serializable.
- Where and how to save this data?
  - Data will be saved in data/ folder. Format: uuid.json and uuid.(zip|png|jpeg|webp|etc)
- What data format to use?
  - Use tags, title, text, asset_url, asset_page, timestamp, author, group
