# Python Lenddo API Client

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Manual Installation](#manual-installation)
- [General Usage](#general-usage)
  - [Example: Requesting one of your application's Lenddo Score](#example-requesting-one-of-your-applications-lenddo-score)
  - [Exceptions and Error Handling](#exceptions-and-error-handling)
- [Submitting Applications to Lenddo: Using the API Client as a White Label Solution](#submitting-applications-to-lenddo-using-the-api-client-as-a-white-label-solution)
  - [The PartnerToken API call](#the-partnertoken-api-call)
  - [The CommitPartnerJob API call](#the-commitpartnerjob-api-call)
- [Requesting Results from Lenddo](#requesting-results-from-lenddo)
    - [Scores](#scores)
    - [Verification Results](#verification-results)

## Introduction
The `lenddo_api_client` python module provides the class `LenddoAPIClient`, 
a generic interface to all the Lenddo HTTP APIs. The client makes authenticated HTTP requests
using the HMAC-SHA1 signing method.

## Installation
To install our client use `pip`:
```
$ pip install lenddo
```

Version `1.1.0` supports both python `2.7.x` and python `3.x`.
If any bug is encountered kindly report the issue [here](https://github.com/Lenddo/python-lenddo/issues/new).

## Manual Installation
The python Lenddo API client library has no third-party dependencies. The only installation
step is to copy and drop the directory `lenddo_api_client/` into a directory in your `PYTHONPATH`. The client has
been tested with python versions `2.7.x` and `3.6.x`.

## General Usage
In order to make API calls, first instantiate a `LenddoAPIClient` initialized
with your API id, your API secret, the base URL of the API resource you intend to use. You
may then make HTTP requests using the client's `get`, `post`, `put`, `delete` and `options`
methods, which are named after the respective HTTP methods. Arguments to
these methods take the form `(resource-type, resource-id, parameter-dictionary)`:
- `resource-type` describes the resource being requested (for example `ApplicationScore`,
`PartnerToken`)
- `resource-id` identifies the specific instance of the requested resource
- `parameter-dictionary` contains additional parameters supported by the call.
In the case of a GET request, these are converted to the request query string. In a POST
or PUT request, they are JSON-encoded and submitted as the request body.

> Optionally, you can use [proxies](#request-a-lenddo-score-behind-a-http-proxy) when connecting to external services.

### Example: Requesting one of your application's Lenddo Score
In this example we make a GET request to the `ApplicationScore` API to obtain the score for a
application with id `example-application`. `ApplicationScore` is hosted at `scoreservice.lenddo.com`.

#### Request a Lenddo score with the LenddoAPIClient
```python
from lenddo_api_client import LenddoAPIClient

client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ApplicationScore', 'example-application')
```

This results in a signed HTTP GET request to `https://scoreservice.lenddo.com/ApplicationScore/example-application`.

#### Request a Lenddo score behind a HTTP proxy
Say your HTTP proxy is running at the http://192.168.1.100 address in your internal network: 
```python
from lenddo_api_client import LenddoAPIClient

HTTP_PROXIES = {
    'http': 'http://192.168.1.100',
    'https': 'http://192.168.1.100',
}

client = LenddoAPIClient(
            'your-api-client-id', 'your-api-client-secret', 
            'https://scoreservice.lenddo.com', proxies=HTTP_PROXIES
         )
response = client.get('ApplicationScore', 'example-application')         
```
The `HTTP_PROXIES` dictionary is based on python's ['proxies' dict](https://docs.python.org/2/library/urllib2.html#proxyhandler-objects).

### Exceptions and Error Handling
Exceptions raised by the client are standard exceptions documented in standard library docs.
The sdk client provides a wrapper module for these exceptions in `lenddo_api_client.errors`.

| exception | description | `2.x` | `3.x` |
| --------- | ----------- | ----- | ----- |
| `HTTPError` | Raised when an API call returns a non-success status. | [link][py2-http-error] | [link][py3-http-error] |
| `URLError` | Raised on network error. | [link][py2-url-error] | [link][py3-url-error] |

The following is the same request as in the previous example, this time with error handling included:

```python
import json

from lenddo_api_client import LenddoAPIClient
from lenddo_api_client.errors import HTTPError, URLError


client = LenddoAPIClient(
    'your-api-client-id', 
    'your-api-client-secret',
    'https://scoreservice.lenddo.com'
)
try:
    response = client.get('ApplicationScore', 'example-application')
except HTTPError as e:
    print('API call failed with status %d' % e.code)

    # Error responses from the Lenddo APIs still return JSON bodies describing error details,
    # only now we have to decode the JSON ourselves.
    print(json.loads(e.read()))
except URLError as e:
    print('API call failed with reason %s' % e.reason)
```

For the sake of brevity, we omit error handling in subsequent examples. In production code, calls should
be made taking into account at least the possibility of `HTTPError`.

## Submitting Applications to Lenddo: Using the API Client as a White Label Solution

You may submit data directly to Lenddo while keeping your own branding, thus utilizing Lenddo services
without having users leave your ecosystem. For each user application, this is accomplished in two
phases: first by making POST calls to the `PartnerToken` resource, which saves OAuth tokens associated
to your user's application, and finally by committing the job using the `CommitPartnerJob` resource.
Both resources are hosted at `networkservice.lenddo.com`.

Applications are identified by a `application_id` which must be supplied as parameter to both
calls. In addition, the `partner_script_id` parameter specifies how Lenddo informs
you of the results. You may only commit one job per `application_id`/`partner_script_id` pair.

### The PartnerToken API call
During the first phase of the job flow, make calls to `PartnerToken` to send social
network OAuth tokens to Lenddo. Each call to `PartnerToken` returns a `profile_id`
which you must save in order to send it along with all other `profile_ids` associated
to this application when you finally commit the job. To add multiple tokens for the same
application, make multiple `PartnerToken` calls, each time saving the returned
`profile_id`.

`PartnerToken` takes the following arguments, all required unless stated otherwise:

- **application_id** - a string that identifies the application to associate with an OAuth token
It must match the `application_id` you use in the `CommitPartnerJob` step.
- **provider** - the token provider. Valid values are:
    `Facebook`, ` LinkedIn`, ` Yahoo`, ` WindowsLive`, or ` Google`
- **token data** - a dictionary of OAuth token data with keys `key` and `extra_data`.
   > **Note**: All tokens must be **OAuth 2.0**.
    - **key** - the access token proper, a string
    - **extra_data** - optional dictionary of additional OAuth fields returned by the token provider.

#### Note
In order for Lenddo to generate the profile_id, it has to use the supplied OAuth token,
which may fail (for example, when the user has denied permission or the token has expired). When
this happens, `PartnerToken` will return with HTTP 400 and the body of the response will contain both the
error code and response body that Lenddo received when trying to use the token. The provider's HTTP response
is under `provider_status_code` and the provider's response body is under `provider_response`. The format of
the `provider_response` varies among OAuth providers; see the OAuth provider's documentation for details.


#### Example
```python
import json

from lenddo_api_client import LenddoAPIClient
from lenddo_api_client.errors import HTTPError


client = LenddoAPIClient(
    'your-api-client-id', 
    'your-api-client-secret',
    'https://networkservice.lenddo.com'
)
try:
    response = client.post('PartnerToken', None, {
        'application_id' : 'example-application',
        'provider' : 'Facebook',
        'token_data' : { 'key' : 'example-access-token' }})
except HTTPError as e:
    print('API call failed with HTTP status %d' % e.code)
    print(json.loads(e.read()))

profile_id = response['profile_id']
# ... and store this profile_id - application_id association
```

#### Errors
To inspect error details, catch `HTTPError`, call the exception object's 'read()' method, and decode the
JSON response.  In the table below, 'Error Name' refers to the string found in the response body's 'name' field.

|Error Name                         |HTTP Status Code    |Description |
|----------                         |----------------    |----------- |
|BAD_REQUEST                        |400                 |Request was malformed, or missing required data. |
|INVALID_TOKEN                      |400                 |Token data was missing required fields or fields had invalid values.|
|TOKEN_FAILURE                      |400                 |Failure upon attempt to use the token. `provider_status_code` contains the provider's HTTP status code. `provider_response` contains the provider's error response body. |
|INTERNAL_ERROR                     |500                 |An internal error occurred. If this persists please contact a Lenddo Representative.|

### The CommitPartnerJob API Call
Once there are no more tokens to associate to a given application, use the
`CommitPartnerJob` call to have Lenddo compute a score for your user. To
obtain the results of the job, see [Requesting Results from Lenddo] (#requesting-results-from-lenddo).

`CommitPartnerJob` takes the following required arguments:

- **partner script id** - Please reference the [developer section](https://partners.lenddo.com/developer_settings) 
    of the partner dashboard. This will define how you're notified of scoring results.
- **application id** - an application id that, coupled with the partner script id, identifies this job. For any given
    application, this is the same application_id used in the `PartnerToken` call.
    You can use this value to retrieve score results.
- **profile ids** - a list of `profile_ids` gathered from the results of the `PartnerToken` call.

In addition to these arguments, CommitPartnerJob accepts the following:
- **verification_data** - A dictionary representing a verification form
- **partner_data** - A dictionary pf form data.

#### Example
```python
# In the actual workflow, profile_ids would be the list of the ids obtained from PartnerToken
# responses associated to this application.
profile_ids = ['123FB']

# Assume the same client instance as used in the PartnerToken section.
# This client connects to networkservice.lenddo.com.
client.post('CommitPartnerJob', None, {
    'partner_script_id' : 'your-partner-script-id',
    'application_id' : 'example-application',
    'profile_ids' : profile_ids})
```

#### Errors
To inspect error details, catch `HTTPError`, call the exception object's `read()` method, and decode the
JSON response.  In the table below, 'Error Name' refers to the string found in the response body's 'name' field.

|Error Name                         |HTTP Status Code    |Description |
|----------                         |----------------    |----------- |
|BAD_REQUEST                        |400                 |Request was malformed, or missing required data. |
|INTERNAL_ERROR                     |500                 |An internal error occurred. If this persists please contact a Lenddo Representative. |
|PARTNER_CLIENT_ALREADY_PROCESSED   |400                 |The specified application_id has already been used. |


## Requesting Results from Lenddo

You may obtain score and verification results from Lenddo by making calls to the
`ApplicationVerification` and `ApplicationScore` APIs hosted at `scoreservice.lenddo.com`.

### Scores
To obtain score results, make a GET request to `ApplicationScore`:

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ApplicationScore', 'example-application', {'partner_script_id' : 'your-partner-script-id'})
score = response['score']
flags = response['flags']
```

### Verification Results
To obtain verification results, make a GET request to `ApplicationVerification`:

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ApplicationVerification', 'example-application', {'partner_script_id' : 'your-partner-script-id'})
results = response['verifications']
flags = response['flags']
name_results = results['name']
```
### Application Decision Results
To obtain application decision results, make a GET request to `ApplicationVerification`:

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('ApplicationDecision', 'example-application', {'partner_script_id' : 'your-partner-script-id'})
results = response['decision']
flags = response['flags']
```

### FICO Score Results
To obtain FICO score results, make a GET request to `FICOScore`:

```python
from lenddo_api_client import LenddoAPIClient
client = LenddoAPIClient('your-api-client-id', 'your-api-client-secret',
	'https://scoreservice.lenddo.com')
response = client.get('FICOScore', 'example-application', {'partner_script_id' : 'your-partner-script-id'})
results = response['score']
pd = response['pd']
```

### CommitPartnerJob partner_data format for FICO scoring
The partner_data format for a FICO score application has has three required fields:
- **application** dictionary, required
- **bureauData** dictionar
- **applicant** dictionary

#### applicationData.application
The application object has the following fields.

| Key | Type | Required | Description |
|--------------|------|---|--------------------------------------------------------------------------------------------------|
| applicationId | string | Yes | |
| date | string in ISO 8601 format | Yes | |
| productType | string | Yes | one of "Mortgage", "Personal Loans", "Overdraft", "Cards", "Auto Loans", "Payday Loan", "SME", or "Others" |
| channel | string | Yes | one of "Partner/Store", "Internet", "Branch", "Small business hub", "Pre-approved", "Top-up", "Mobile App" or "ATM" |
| product | object | Yes | see description below |


#### applicationData.application.product
The product object has the following fields.

| Key | Type | Required | Description |
|--------------|------|---|--------------------------------------------------------------------------------------------------|
| loanAmount | integer | Yes | |
| paymentMethod | string | Yes | one of "Auto debit" or "Payment through transaction account" |
| indicatorForPresenceOfGuarantor | boolean | Yes | |
| loanPurpose | string | Yes | one of "Loan for personal expenses", "Working capital loan", "Holiday", "Loan for making interest payment", "Education", "Renovation", "Refinancing", or "Others" |

#### applicationData.bureauData
The "bureauData" object has two fields, "enquiries" (array of objects) and "tradelines" (array of objects).

#### applicationData.bureauData.enquiries
Each enquiry object in the enquiries array has the following fields.

| Key | Type | Required | Description |
|--------------|------|---|--------------------------------------------------------------------------------------------------|
| amount | integer | Yes | the amount of the enquiry |
| applicationId | string | Yes | |
| enquiryDate | string in DDMMYYYY format | Yes | |
| entityType | string | Yes | |
| memberCd | string | Yes | |
| memberRef | string | Yes | |
| processedDate | string in DDMMYYYY format | Yes | the date when the enquiry was made |
| productCd | string | Yes | the product applied for |
| purpose | integer | Yes | purpose of the enquiry |
| controlNum | integer | No | a system-generated enquiry control number |

#### applicationData.bureauData.tradelines
Each tradeline object in the tradelines array has the following fields.

| Key | Type | Required | Description |
|--------------|------|---|--------------------------------------------------------------------------------------------------|
| accountNum | string | Yes |
| accountStatus | integer | Yes |
| accountType | integer | Yes | |
| accountTypeCd | integer | Yes |
| amtOverdue | number | No | the amount past due as of the date in the Date Reported field |
| applicationId | string | Yes | |
| cashLimit | number | No | |
| closeDate | string in DDMMYYYY format | Yes | the date the account was closed |
| collateralType | integer | Yes | 
| collateralValue | number | No | |
| controlNum | integer | No | a system-generated enquiry control number |
| creditLimit | number | No | for Credit Card (Account Type 10) and Fleet Card (Account Type 16, this field contains the highest amount of credit used in the history of the account |
| currBalance | number | No | the entire amount of credit or loan outstanding, including the current and overdue portion, if any, together with interest last applied, as of the date in the Date Reported field |
| delqHisMMYY | string | Yes | cycle delinquency (up to 48 months) |
| installmentAmt | number | No | |
| interestRate | number | No | |
| lastPayment | number | No | |
| lastPaymentDate | string in DDMMYYYY format | Yes | |
| memberCd | string | Yes | |
| memberRef | string | Yes | |
| openDate | string in DDMMYYYY format | Yes | date of first disbursement of the account |
| ownershipInd | integer | Yes | 1 = Individual, 2 = Authorised User (refers to supplementary credit card holder), 3 = Guarantor, 4 = Joint |
| payHistEndDate | string in DDMMYYYY | Yes | the date of the end of the payment history |
| payHistStartDate | string in DDMMYYYY format | Yes | date of the beginning of the payment history |
| processedDate | string in DDMMYYYY format | Yes | |
| productCd | string | Yes | |
| repaymentTenure | integer | Yes | term of loan | 
| reportedDate | integer | No | Yes |
| sanctionAmt | number | No | for all other accounts, this field contains the amount of loan sanctioned |
| settlementAmt | number | No | settlement amount |
| suitFiledCurrStatus | string | Yes  | suit filed status of the current month |
| suitFiledStatusMMYY | string | Yes | suit filed status history (up to 48 months)) |
| termFrequency | string | Yes | payment frequency |
| writeoffPrincipalAmt | number | No | |
| writeoffSettledStatus | string | Yes | |
| writeoffTotalAmt | number | No | write-off amount - total |

#### applicant
The applicant object has the following fields.

| Key | Type | Required | Description |
|--------------|------|---|--------------------------------------------------------------------------------------------------|
| dob | string in ISO 8601 format | Yes | |
| mobileTelephoneProvided | boolean | No | |
| gender | string | No | one of "MALE" or "FEMALE" |
| maritalStatus | string | No | one of "Married", "Living together", "Single", "Widowed", "Divorced/Separated", or "Other"  
| residenceRegion | string | No | |
| emailProvided | boolean | No | |
| employmentStatus | string | No | one of "Salaried", "Own Business/ Self-Employed", "Retired/Pensioner", "Part-time Employed / Freelance / Contractual Employee / Laborer", "Housewife/Other", or "Student" |
| yearsInCurrentJob | integer | No | |
| homeTelephoneProvided | boolean | No | |
| educationLevel | string | No | one of "Undergraduate", "Graduate", "Post Graduate", or "Diploma and Specialized Courses"  |
| yearsOfService | integer | No | |
| residentialStatus | string | No | one of "Self Owned", "Company Provided", "With Parents", "Rented", "Paying Guest", "Leased", or "Other" 
| workTelephoneProvided | boolean | No | |
| dependents | integer | No | |
| numOfMonthsInCurrentAddress | integer | No | |
| monthlyIncome | integer | No | |
| existingCustomer | object | No | object with fields "timeWithTheBank" (integer) and "noOfAccountsWithTheBank" (integer)

### Errors
To inspect error details, catch `HTTPError`, call the exception object's `read()` method, and decode the
JSON response.  In the table below, 'Error Name' refers to the string found in the response body's 'name' field.

|Error Name        |HTTP Status Code    |Description |
|----------        |----------------    |----------- |
|BAD_REQUEST       |400                 |Request was malformed, or missing required data. |
|INTERNAL_ERROR    |500                 |An internal error occurred. If this persists please contact a Lenddo Representative. |
|NOT_FOUND         |404                 |The requested application_id was not found. |

[py2-http-error]: https://docs.python.org/2/library/urllib2.html#urllib2.HTTPError
[py2-url-error]: https://docs.python.org/2/library/urllib2.html#urllib2.URLError
[py3-http-error]: https://docs.python.org/3/library/urllib.error.html?highlight=httperror#urllib.error.HTTPError
[py3-url-error]: https://docs.python.org/3/library/urllib.error.html?highlight=httperror#urllib.error.URLError
