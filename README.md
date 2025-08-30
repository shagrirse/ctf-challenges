# Introduction

Thank you so much for contributing to the challenge creation process for our CTF events. If you do need any clarification or are running into some troubles with creating/documenting your challenges, or if you have special deployment notes you'd like to discuss, please reach out to me `@shagrirse`.

If you have any suggestions for improving the current challenge creation workflow, do let me know!!!

# Creation Guide
Here are some best practices to follow when creating your challenges to make it a breeze to deploy:

0. Try as much as possible to follow the existing file structure for each challenge given in the examples in this repo
    - Examples can be found in `example-image-based-challenge` or `example-text-based-challenge` 
1. There will be a `challenge.yml` and `README.md` file in each challenge.
    - `challenge.yml` A configuration file meant to be used to programmatically deploy you challenge on to our servers. Fields that are not commented out are required. Fields in that file which are commented out can be used as well, but might be modified by the training team as they see fit.
    - `README.md` A pretty basic markdown file that should contain the necessary things (all headers are in the template!)
2. Each challenge directory should also contain a `writeup` directory, which should be used to document the solution to your challenge, taking note to include any scripts/files you might want to include as part of your solution.
    - It would be ideal if your challenge has a script that automatically solves it, though it is optional.
3. The `src` directory should contain all the source code needed (if applicable).
    - It is mandatory for your challenge to be Dockerized.
4. There should be a `docker-compose.yml` and `Dockerfile` in the challenge's root directory as well, indicating the docker infrastructure and commands needed to deploy your challenge.
5. A `.dockerignore` file can also be used to ignore non-build essential files/directories if needed.
6. **Highly recommended to use port 80**, but if you need to use another port, specify it in challenge.yml and the challenge's README. The `exposed_port` option in `challenge.yml` is the port the challenge will be exposed on the internet.
    - If your challenge requires multiple ports (or containers), put `challenge_type` as `other`.

# Contributing
[only if you want to](https://www.conventionalcommits.org/en/v1.0.0/)
1. Fork the repo
2. Branch from main
3. Challenge Creation
4. Open PR
5. $$$ Profit