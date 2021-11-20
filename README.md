# COMSW4156-TeamMatrix

**To Build**: `pip install -r requirements.txt`

**To Run:** `python3 app.py`

**To Test:** 

- Generate Endpoint: 
    `curl -X GET "0.0.0.0:5001/generate"`

- Create Endpoint: 
    `curl -X POST "0.0.0.0:5001/create?application=app1&password=qwerty@098"`

- Retrieve Endpoint: 
    ```
    curl -X GET "0.0.0.0:5001/retrieve?application=all"
    curl -X GET "0.0.0.0:5001/retrieve?application=app1"
    ```

- Update Endpoint:
    `curl -X POST "0.0.0.0:5001/update?application=app1&password=qty@1234"`

- Delete Endpoint: 
    `curl -X DELETE "0.0.0.0:5001/delete?application=google"`
    
**To run system-tests:**

`./system_tests.sh`
    
    
 ## API Documentation:
 - Generate Endpoint: Enables user to Generate a password for an application.

- Create Endpoint: Enables user to create a password for a spcified application.

- Retrieve Endpoint: Enables user to retrieve password for all or specific applications.
  
- Update Endpoint: Enables user to update password for a spcified application.

- Delete Endpoint: Enables user to delete password for particular or all applications.

 The API Spec can be found [here](https://github.com/RohanKumarSachdeva/COMSW4156-TeamMatrix/blob/main/documentation/api_spec_password_manager.png)

