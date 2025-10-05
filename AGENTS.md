## Supabase Data
The data available in supabase is in the 'dw' schema and contains metadata from youtube i.e channel and video metadata. Also contains youtube transcripts, transcript summaries, and video topics. 
- Only use data in the dw schema
- Do not use youtube-transcript-api

## Tech Stack
Use the bellow tech stack, you must ask before adding other services or frameworks
- Langchain for Agent development
- Supabase for relational database
- pgvector in supabase for vector database
- python programming language
- flask for web apps

## Evals
- when running evals dump the results into a .evals folder for each run, name each run with a timestamp to avoid naming collision
- .gitignore .evals folder and its children

