# What is this?

This code is a TwitterBot for publishing a location within the contiguous United States that currently has a temperature of 72 degrees. It is ready to be deployed in the user's cloud computing choice using Docker.

# How it works?
1. The code downloads a current weather map. Then, it searches the weather map for locations where a temperature of 72 degrees may be likely using premade partitions.
2. The most likely locations (density of acceptable regions per partition) are sorted. Then, OpenWeather API calls are made to ping each location for weather.
3. When a location has been found, it will be published to Twitter and the code will end. Otherwise, it will publish that no location was found.

# How to use?

1. In the runme.py file, replace the OpenWeather API and Twitter API placeholders with your own keys.
2. Run the file as is, or create a Docker container with it all!
3. If needed to be deployed, use AWS ECS to automatically run the Docker container
