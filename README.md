## a smiple face recognition app
![Alt text](image.png)
## EVENT
```json
{
  "type": "error" || "data",
  "image": "data:image/jpeg;base64,...",
  "extra": {
    "faces": [
      {
        "name": "name" || "unknown",
        "crop": "data:image/jpeg;base64,..." || null,
      },
    ]
  }
}
```
