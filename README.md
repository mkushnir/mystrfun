Fun With Strings
----------------

The Fun With Strings service provides an entertaining web API about English words.  You may ask the service to tell some word (in a random manner).  Or ask for a Wikipaedia article about your personal word of the day.  Finally, given a pair of first and last person names, get a joke about this person.


Authenticated^WAny users will be able to see some internal stats of the service.


All API return the _200_ HTTP response on sucess and one of _4xx/5xx_ on errors.  Results are represented as json objects in the response body.

In a general case, an error is returned with the following json object in the body:

Fields:

- _message_: a string explaining an error.

Example:

    GET /random

    500 Internal Error

    {
        "message": "Application error."
    }


A positive result is returned in a json object:

Fields:

- _result_: a string, or any other object as specified by the endpoint.


# Generic Errors

## Application Error

    500 Internal Server Error

    {
        "message": "Application error."
    }



# End Points

## GET /random

Return a random word.  Example:

    GET /random

    200 OK

    {
        "result": "hello"
    }


## GET /wikipedia/\<phrase\>

Given the phrase, return a text of its article in the English Wikipedia (XML tree in a single string).  Example:

    GET /wikipedia/randomize

    {
        "result": "<root>'''Randomization''' is the process of
                   making something [[random]]; ...</root>"
    }

Errors (example):

    GET /wikipedia/qwepoiwerpoi

    404 Not Found

    {
        "message": "No such wiki: qwepoiwerpoi"
    }


## GET /joke/\<first-name\>/\<last-name\>

Return a Chuck Norris joke for the given name pair.  If either the _last-name_ or both names are missing, they are replaced with the _Norris_ and _Chuck_ respectively.  Example:

    GET /joke/bill/gates

    {
      "result": "Hellen Keller's favorite color is bill gates."
    }


## GET /stats/\<int:n\>

Return the top _n_ words submitted to the _/wikipedia_ endpoint as an array of strings.  Example:

    GET /stats/2

    {
      "result": [
        "randomness", 
        "randomize"
      ]
    }


## POST /stats/reset

Clear the Wikipedia stats:

    POST /stats/reset

    {
        "result": "ok"
    }

