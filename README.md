
# Human vs LLM

While there exist many benchmarks to evaluate the perfomance of LLMs, most of these benchmarks neglect the capabilities of LLMs in cultural domains.

So we toke 10 LLM to the test and avaluated their creativity and cultural bias.

Clone the repo and see it for you self !


## Set-up (linux)

1. Install git lfs if not installed 
    ```sh
    sudo apt-get install git-lfs
    git lfs install
    git lfs version
    ```
    Install uv if not installed (https://docs.astral.sh/uv/getting-started/installation/) 

2. Clone the project
3. Sync the uv evironment
    ```sh
    uv sync
    # or
    uv sync --link-mode=copy # If copy issue
    .venv\Scripts\activate # activate venv
    ```
4. (OPTIONAL) Download the English (wiki.en.align.vec) and French (wiki.fr.align.vec) alligned word vectors from : https://fasttext.cc/docs/en/aligned-vectors.html and place in the folder models/
5. (OPTIONAL) Run models/convert_models.py to convert the .vec into .kv files (can take up to 30 minutes)
    ```sh
    python models/convert_models.py
    ```
6. Run the app
    ```sh
    streamlit run app/app.py
    ```

## Useful commands
Test tracked files and list lfs files
``` sh
git lfs track
git lfs ls-files
```

Pull lfs files
```sh
git lfs pull
```