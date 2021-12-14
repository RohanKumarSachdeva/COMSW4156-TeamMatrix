# COMSW4156-TeamMatrix

**To Build**: `pip install -r requirements.txt`

**To Run:** `python3 app.py`

**To Test:** 

- Generate Endpoint: 
    `curl -X GET "0.0.0.0:5001/generate"`

- Create Endpoint: 
    `curl -X POST "0.0.0.0:5001/create?application=app1&password=qwerty@098"`

- Strength Endpoint: 
    `curl -X POST "0.0.0.0:5001/strength?password=qwerty123"`

- Retrieve Endpoint: 
    ```
    curl -X GET "0.0.0.0:5001/retrieve?application=all"
    curl -X GET "0.0.0.0:5001/retrieve?application=app1"
    ```

- Update Endpoint:
    `curl -X POST "0.0.0.0:5001/update?application=app1&password=qty@1234"`

- Delete Endpoint: 
    `curl -X DELETE "0.0.0.0:5001/delete?application=google"`
    
    
 ## API Documentation:
 - Generate Endpoint: Enables user to Generate a password for an application.

- Create Endpoint: Enables user to create a password for a spcified application.

- Password Strength Endpoint: Checks the strength of password taken as input from the user, providig output on a scale of 0-4 alog with guessed time of craking password.

- Retrieve Endpoint: Enables user to retrieve password for all or specific applications.
  
- Update Endpoint: Enables user to update password for a spcified application.

- Delete Endpoint: Enables user to delete password for particular or all applications.

[**API Spec**](https://github.com/RohanKumarSachdeva/COMSW4156-TeamMatrix/blob/main/documentation/api_spec_password_manager.png)
 
[**Sonar Cloud Report Dashboard**](https://sonarcloud.io/summary/overall?id=RohanKumarSachdeva_COMSW4156-TeamMatrix)


## Client UI Application
The client accesses our Password Manageemnt Application on URL [http://127.0.0.1:5000/](http://127.0.0.1:5000/). 
Since client paths are accessible only when client is authorized, client is first presented with a Welcome page to login with [Google OAuth2.0](https://developers.google.com/assistant/identity/google-sign-in-oauth). 
Upon login, client gets an option to - 
- Generate a password using our application. Client can specify the inputs to be used (special characters, Uppercase charaters, numbers)
- Store a new application and password in our database. While providing new inputs, client can also check the strength of their provided password.
- Retrieve an application and its respective password.
- Delete a particular entry for an application and password.
- Update password for an app.

