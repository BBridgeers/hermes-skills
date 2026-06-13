# Instagram GraphQL Response Shape

## User Media Query
- Hash: `69cba40317214236af40e7efa697781d`
- Endpoint: `https://www.instagram.com/graphql/query`
- Variables: `{"id": "<user_id>", "first": 50, "after": "<cursor>"}`

## Response Structure
```json
{
  "data": {
    "user": {
      "edge_owner_to_timeline_media": {
        "count": 940,
        "page_info": {
          "has_next_page": true,
          "end_cursor": "QVF..."
        },
        "edges": [
          {
            "node": {
              "__typename": "GraphSidecar",   // carousel (GraphImage=image, GraphVideo=video)
              "id": "3847670568532023096",
              "shortcode": "DWmDDWtjDOe",
              "taken_at_timestamp": 1769443200,
              "edge_media_to_caption": {
                "edges": [{"node": {"text": "caption here..."}}]
              },
              "edge_media_preview_like": {"count": 1234},
              "edge_media_to_comment": {"count": 56},
              "edge_sidecar_to_children": {    // carousel only
                "edges": [
                  {
                    "node": {
                      "id": "...",
                      "__typename": "GraphImage",
                      "display_url": "https://...",
                      "display_resources": [
                        {"src": "https://...small.jpg", "config_width": 240, "config_height": 300},
                        {"src": "https://...large.jpg", "config_width": 1080, "config_height": 1350}
                      ]
                    }
                  }
                ]
              }
            }
          }
        ]
      }
    }
  }
}
```

## Key Points
- `display_resources` is an array of quality variants — last entry is highest resolution
- Carousel children can be mixed type (images + videos in same carousel)
- `__typename`: `GraphSidecar` = carousel, `GraphVideo` = video, `GraphImage` = single image
- The public endpoint (`/api/v1/users/web_profile_info/?username=`) hits 429 aggressively — prefer the GraphQL private endpoint with auth cookies
