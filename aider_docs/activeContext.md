# Active Context

## Current Focus
Critical reliability bug: Phonemization (eSpeak) fails after sustained usage

## Recent Changes
- Added resource tracking to phonemizer
- Implemented singleton pattern for EspeakBackend
- Added periodic cleanup every 50 requests

## Next Steps
1. Monitor resource usage through logging
2. Identify specific resource leaks
3. Develop targeted fix based on diagnostics
4. Verify Railway memory limits aren't being exceeded
