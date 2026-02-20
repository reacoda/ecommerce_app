1. The python request module allow one to send HTTP requests using Python. The HTTP request returns a response object with all the response data (content, encoding, status, e.t.c.).
When one visit a website such as google.com this is done as an HTTP GET request. When we submit a login form in our ecommerce application that is done through an HTTP POST request. 

How is it used to make HTTP requests:
- The first thing one will need to do is to include the module as follows:
  import requests
- Then if one would like to get data from a website they write the following:
  response = requests.get('https://api.github.com/users/reacoda/)
  print(response.json())

- To send data to a website, one does the following:
  data = {'username': 'tiisetso', 'password': 'password123'}
  response = requests.post('https://example.com/login', data=data)

  Suppose you would like to use the Python request module to integrate a payment API.
  After installing the requests module, you will need to set up authentication to store your APIs securely in environment variables and include them in the request headers as specified by the provider. To create charges, one will use requests.post(). For retrieving information, you will use requests.get(). 
  
  Handle the response: Check the HTTP status code - 200 OK for success, 400 Bad request, 401 Unauthorized, 402 Payment required. You will then parse the JSON response to confirm success, extract transaction IDs, or display error messages to the user. 

2.  JSON and XML data formats

    JavaScript Object Notation is primarily used to transmit data between a server and web application. it uses dictionaries - key-value.  is represented the following way:

    {
        "name": "Laptop",
        "price": 15000,
        "inStock": True,
        "tags": ["electronics", "computers"]
    }

    Whereas XML (Extensible Markup Language) is designed to store, structure, and transport data by allowing users to define their own tags. It is represented in the following way:
    <product>
        <name>Laptop</name>
        <price>15000</price>
        <inStock>True</inStock>
        <tags>
            <tag>electronics</tag>
            <tag>computers</tag>
        </tags>
    </product>

    - Both are used for storing data, sending data between systems (using APIs), and for configuration files.

    Advantages of JSON
    - Easier to read as they look like Python dictionaries
    - They use smaller file size (less data to send)
    - It can be processed faster
    - It works natively with JavaScript

    Disadvantages of JSON 
    - No comments allowed - one can't add notes in the data
    - It has limited data types (no dates, only strings/numbers/booleans)
    - No schema validation built-in
    - Less human-readable for complex nested data

    XML Advantages 
    - Self-documenting (the tags explain the data)
    - Supports attributes (extra info on tags)
    - Schema validation (can enforce rules)
    - It works better for document-style data

    Disadvantages of XML
    - It has a lot of extra characters: <tag></tag>
    - It is usually larger file sizes
    - Slower to process
    - More complex to work with

3. - What is REST APIs
    A RESTful API (Representational State Transfer Application Programming Interface) is an architectural style for designing networked applications that uses HTTP protocols to enable communication between clients and servers.
   - What is it used for 
    
   - Advantages of REST APIs
    1. Simplicity and Ease of Use: REST leverages existing HTTP infrastructure and methods, requiring no additional protocols or specialized tools. 
    2. Scalability: The stateless nature of REST means servers don't need to maintain session information between requests, allowing easy horizontal scaling by adding more servers. 


    References:
    1. GeeksforGeeks (2024) *Python requests module*. Available at: https://www.geeksforgeeks.org/python-requests-module/ (Accessed: 8 February 2026).

    2. IBM (2023) *What is a REST API?*. Available at: https://www.ibm.com/topics/rest-apis (Accessed: 8 February 2026).

    3. Mozilla Developer Network (2024) *HTTP request methods*. Available at: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods (Accessed: 8 February 2026).

    4. Red Hat (2024) *What is a REST API?*. Available at: https://www.redhat.com/en/topics/api/what-is-a-rest-api (Accessed: 8 February 2026).
