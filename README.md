# P.A.N.I.C FOR SECRET NETWORK NODE RUNNERS

### Notes: 
This is tested by me on Ubuntu 20.04 LTS with Reddis and Telegram Bot enabled

## Install Instruction For Secret Node Runners
```
sudo apt-get update
sudo apt-get upgrade
```
```
sudo apt-get install build-essential
```
```
sudo apt-get install python3.6
```

```
sudo apt-get install python3-pip
```

```
pip3 install pipenv
```

## Validate installations

```
python3 --version

pip3 --version

pipenv --version

```
## Advance Features
### Tellegram Bot
 Follow the instructions here to create a tg bot
 >https://github.com/mohammedpatla/panic_cosmos/blob/master/doc/INSTALL_TELEGRAM.md

### Install Reddis for DB
 Follor the instructions here to install redis DB on your server
 >https://github.com/mohammedpatla/panic_cosmos/blob/master/doc/INSTALL_REDIS.md

## Setting up P.A.N.I.C.
 Clone the Repo from

 ```
 git clone https://github.com/mohammedpatla/panic_cosmos.git
 ```

 To set up your config files
 
 Navigate to :
 ```
 cd ~/panic_cosmos/config
 ```

 ### Edit the config files for each
1.  ```
    nano example_user_config_main.ini
    ```

    Make sure you added Reddis Password if you set one and change it to `true`,

    Add Telegram API token and Chat ID (that you got from the setup) on both sections and changed them to `true`

    Then rename it to user_config_main.ini using
        ``` mv example_user_config_main.ini user_config_main.ini ```
2.  ```
    nano example_user_config_nodes.ini
    ```
    You have to enable all your nodes you want to monitor

    Confirm you added your RPC Address `<your IP>:26657` 

    Do not cahnge the Bootstarap RPC address as that will confirm if your node is up and running (IF you have another validators RPC address you trust, you can add that address)

    Then rename it to user_config_nodes.ini using
        ``` mv example_user_config_nodes.ini user_config_nodes.ini ```
3.  ```
    nano example_user_config_repos.ini
    ```
    If you want you can Add Repositorys to monitor or just set them to false

    Then rename it to user_config_repos.ini using
        ``` mv example_user_config_repos.ini user_config_repos.ini ```

 ### Build
 ```
 cd ~/panic_cosmos
 ```
 ```
 pipenv sync
 ```
 ### Run
 ```
 pipenv run python run_alerter.py
 ```
If you want to run this as a Linux Service you can find it in the original detailed docs (This is untested with my version)
[Running P.A.N.I.C as a service on Linux](https://github.com/mohammedpatla/panic_cosmos/blob/master/doc/INSTALL_AND_RUN.md#running-panic-as-a-linux-service)


 ### Finishing up
If Everything was set right then you should get this output:
    ```
    Enabled alerting channels (general): ConsoleChannel, LogChannel, TelegramChannel
    Enabled alerting channels (periodic alive reminder): ConsoleChannel, LogChannel, TelegramChannel
    Trying to connect to <your-IP>/status
    Success.
    Trying to connect to http://bootstrap.mainnet.enigma.co:26657/status
    Success.
    Node monitor (<Moniker>) started.
    Network monitor (secret-1) started with 1 validator(s) and 1 full node(s).
    Telegram commands started.
    Periodic alive reminder started.
    ```

### Advanced Configurations
[Advanced](https://github.com/mohammedpatla/panic_cosmos/blob/master/doc/INSTALL_AND_RUN.md#advanced-configuration)

## Original Documentation
### [Click Here](https://github.com/mohammedpatla/panic_cosmos/blob/master/doc/DESIGN_AND_FEATURES.md) Design and Features
### [Click here](https://github.com/mohammedpatla/panic_cosmos/blob/master/doc/INSTALL_AND_RUN.md) Original Installation Instructions

## Credits
- Original Creater : Simply VC @ All rights Reserved

- Modified By : Mohammed Patla
