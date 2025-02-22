# Youtube_subscriber_service

This is our free open source youtube service project on github
This project consist 2 service:
1) Getting the subscription list of the user and store the data in MongoDB
2) Generate summary of the videos for individual subscriptions and send personalized email notification to the user.

## Local Setup

- Step 1: Check Python version
    ```python3.12 --version```

- Step 2: Create a virtual environment
    ```python3.12 -m venv youtube_subscription```

- Step 3: Activate the virtual environment
    - Linux/Mac: ```source youtube_subscription/bin/activate```

    - Windows (cmd): ```youtube_subscription\Scripts\activate```
- After activating the virtual environment, install the dependencies using the following command:
  - ```pip install -r requirements.txt```

## High Level Design/Architecture

![](./assets/High_level_system_design_flow.png)