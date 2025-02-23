

### Step 1: Set Up AWS SSO
1. Enable AWS SSO:
    - Go to the AWS Management Console.
    - Navigate to the AWS SSO service.
    - Click on "Enable AWS SSO" if it is not already enabled.
3. Configure AWS SSO:

    - Set up your identity source (e.g., AWS SSO, Active Directory, etc.).
    - Create user groups and assign users to these groups.
    - Assign permissions to these groups by creating permission sets.
4. Assign Users to AWS Accounts:

    - Assign the user groups to the AWS accounts you want to manage.
    - Assign the appropriate permission sets to these groups.

### Step 2: Configure AWS CLI for SSO
1. Install AWS CLI:

    - If you haven't already, install the AWS CLI on your local machine.

```
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

2. Configure AWS CLI for SSO:

    - Run the following command to configure the AWS CLI for SSO:

  ```aws configure sso```
    
   - Follow the prompts to enter your SSO start URL, region, and other details.

### Step 3: Use AWS SSO in Your Script

1. Login Using AWS SSO:

    - Before running your script, log in using AWS SSO:
    ```aws sso login --profile youtube-transcript```