# seer
This app takes a project in the form of a zip file, combines all of the relevant code (ignoring vendor stuff, `node_modules` etc) and 
then uses [Tarsier](https://github.com/reworkd/tarsier) with Groq to parse and work through a user's input to automate website tasks. 

For instance, if I am a product manager and want to understand my current product's onboarding screens without manually
running through all of them, I can ask seer -- "what is the onboarding process" which will return a bunch of relevant screenshots
using a combination of GPT and OCR. The great part is that accuracy is guaranteed here since there is live processing happening based 
on the ultimate source of truth -- the codebase. Things like documentation in Notion, or Figma screenshots get outdated almost instantly.

The code isn't the prettiest as the goal of this was a private side project rather than OSS.
