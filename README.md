# alpha-ai-0: back to basics

This repo can be run locally inside a [Docker](https://www.docker.com/products/docker-desktop/) container. For now, it's a simple chat interface that uses [Streamlit](https://streamlit.io)

## Running Locally

To run locally, you'll need to have Docker installed. Then, run the following commands:

Create a new Streamlit directory that Docker will use to build the Streamlit image.

```bash
mkdir .streamlit && cd .streamlit && touch secrets.toml
```

```
openai_key = "YOUR_KEY_HERE"
```

Then, run `docker-compose up`
