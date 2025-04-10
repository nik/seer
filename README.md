# seer
This app takes a project in the form of a zip file, combines all of the relevant code (ignoring `node_modules` etc) and 
then uses [Tarsier](https://github.com/reworkd/tarsier) combined with a user query to automate app tasks. 

For instance, if I am a product manager and want to understand my current product's onboarding screens without manually
running through all of them, I can ask seer -- "what is the onboarding process" which will return a bunch of relevant screenshots
using a combination of GPT and OCR. 
