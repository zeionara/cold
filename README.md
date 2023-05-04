# Cold

**Co**mmunity **l**abelling **d**river - a tool for inferring labels for data elements using provided corpus of annotations. In particular, the tools attempts to solve the *cold*-start problem of the recommender systems.

<p align="center">
    <img src="assets/images/logo.png"/>
</p>

## Installation

To install the project dependencies, create a conda environment using the provided config file:

```sh
conda env create -f environment.yml
```

The following env variables are required for working with `vk api`:

- `COLD_APP_ID` - api app id, see at the [vk api web page](https://vk.com/apps?act=manage);
- `COLD_VK_API_KEY` - api access token, use [this script](tools/make-token-generation-url.sh) to obtain it;
- `COLD_USER_ID` - user id, from whose profile automated queries will be sent, see property `user_id` filled after running the [token generation script](tools/make-token-generation-url.sh).

## Launch

To run the project in a manual mode, execute the following command:

```sh
python -m cold probe assets/default/train.cld assets/default/spec.yml
```

## Test

To run tests, use the following command:

```sh
python -m unittest discover test
```
