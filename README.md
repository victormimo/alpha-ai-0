# alpha-ai-0

This repo can be run locally inside a [Docker](https://www.docker.com/products/docker-desktop/) container. For now, it's a simple chat interface that uses [Streamlit](https://streamlit.io), our deployed API on Azure, and Optimism Goerli.

## Running Locally

To run locally, you'll need to have Docker installed. Then, run the following commands:

Create a new Streamlit directory that Docker will use to build the Streamlit image.

```bash
mkdir .streamlit && cd .streamlit && touch secrets.toml
```

Inside of the newly created `secrets.toml` file, add your own OpenAI API key. You can get one [here](https://platform.openai.com/account/api-keys) inside of Poet's org on OpenAI.

```
openai_key = "YOUR_KEY_HERE"
```

Then, run `docker-compose up`
