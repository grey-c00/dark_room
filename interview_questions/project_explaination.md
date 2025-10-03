# Experience so far:
I started working on the projects and over the time, my role evolved.

Current my role includes - 
1. discussing upcoming projects and their feasibility in our system
2. Architecture discussion
3. Implementation, code reviews, runbook creation and getting reviewed
4. Onboarding new people to the product
5. Sort of owning a part of the entire system, health of the systems, alert monitoring, cost monitoring and all

# Auto Tagging
goal is to speak for 40 minutes

## what is the project?

Here, I am going to use some terms such as training. Which is like, people are being trained via various methods to do well in their jobs such as sales, which is called performance in field.

So basically, there is a system where we show co-relation between the training provided and the way people are performing in the field.

So, while training, each training module is assigned some tags such as this training modules is for communication, this training module is for product knowledge. So, at the end , we are going to tell that based on the training provided in the communication, how people are performing in the field.

So, you can decided to modify your training modules.


So the project was that, lets say you are trying to understand the corelation. So, what is you need is the training data and tags on them such as communication, product knowledge.

So, training data has been since a long time in our system but this corelation feature was new. Now, customers would want to use this feature and for this they need to add tags to their training data.

So, there are two ways to do this -
1. either they go to each training module and add tags manually, but this is going to be a tedious task as there are thousands of training modules
2. or, we can provide a system which can automatically tag these training modules.


So, we decided to go with the second option, which is to provide a system which can automatically tag these training modules. At that point of time, LLMs were being rolled out and it was a great opportunity to integrate this product with LLMs.

So, we decided to provide a system that will suggest the tags based and add them on the training data.


## why the project?
This project was important because, this was a new feature and customers were going to use this feature. So, if we can provide a system which can automatically tag these training modules, then it will be a great value addition to the product.

## Potential impact?
Within a month of releasing this feature, we were able to sell this feature to 15+ customer which brought in 2.5M dollars of revenue.

## Architecture
we decided to go with a serverless architecture because this feature is not that is being used frequently. So, we decided to go with a serverless architecture which is cost effective and scalable.

we decided to use a event driven architecture. 
Why? because there are few async flows that needs to be taken care. One such flow was to make LLMs calls and get the result back. There could be multiple calls as well, which may take some time and there could be failures as well. So, given all these situation, we had two options, 
1. either we can have dedicated machines running on K8s cluster and fulfil the request
2. or, we can use a event driven architecture which is scalable and cost effective.

Hence, we decided to go with event driven architecture.


So, this was the architecture, 
1. Request will be made to lambda
2. Lambda will identify all of the training modules that needs to be tagged
3. Lambda will make call to LLMs service via gRPC call
4. LLM services will return results
5. Those results will be served back to customers
6. If customer wants, they can make modifications to the tags
7. Once they are happy with the tags, they can give the go ahead
8. Lambda will be invoked again and those tags will be added to the training modules via gRPC calls


## failure handling

There can be failure at multiple stages. Such as
- while collecting training modules 
  - we solved it by designing a very efficient API to retrieve and serve this data
- while making LLM calls 
  - we solved it by implementing retry mechanism with exponential backoff 
  - and by keeping track of each request and its status
  - and we implemented alerting as well to monitor the failures
- while serving the results back to customers
  - we solved it by write a logic to notify the customer, once, all of the results are ready
  - customer could see the data and make modifications
- making it idempotent to make sure that server is not overloaded
  - we started to maintain the state of each request with idempotent key
- what if LLM service is down?
  - we resolved it at multiple layers - 
    - if call to LLM service has failed, such as 500 or anything then we will retry with exponential backoff 
    - if it still fails then we will mark this request as failed and notify the customer
    - if LLMs never send the response back?
      - First of all, there is contract between our service and LLM service, so they will somehow have to ensure that response is being sent back. If not, they need to work and honor the contract.
      - But still, we implemented a mechansim to do pings are certain intervals and if there is no response for a long time, then we will mark this request as failed and notify the customer
      - How do decided the timeout?
        - Their was a mechanisum based on amount of data that needs to be processed and based on that we decided the timeout. Estimated rate was number of training modules / 60 seconds.
        - So, if no response is received then within this time frame, request will be marked as failed.
        - If we are receiving responses (may be slow) then we again consider this much of timeout.
- What if customer made some incorrect modification
  - we need to identify the incorrect modification and provide right suggestion to the customer to fix it
- What if final gRPC call of applying tags was failing - 
  - We used the same retry mechanism with exponential backoff
  - We made it idempotent as well - though by contract this API call was always idempotent
  - If it still fails, we will write this request in dead letter queue

## why do you think that it was a good project


## tradeoffs
1. lambda size - lambda had a size limit of 250MB, so we had to make sure that our lambda function was within this limit. Some of the packages that were having bigger size, we had to identify was to either remove them or use some other package or use layers
2. lambda run time - lambda had a run time limit of 15 minutes, so we had to make sure that our lambda function was within this limit. We had to make sure that each lambda function was doing only one thing and not doing too much work. We had to break down the work into smaller chunks and use multiple lambda functions to do the work.
3. multiple retries, need to make all APIs idempoent
4. Almost all communications are async, need to maintain the state of each request and make sure that there is no loose end in the entire system
5. Customer had certain controls, so it was hard to detect the manual modifications and provide right suggestions
6. Need to add validations around LLMs response
7. Need to do testing to find out how accurate those results were


## why dedicated instances were not used?
1. cost - dedicated instances are costly, as we have to pay for the instances even if they are not being used. In our case, this feature was not being used frequently, so it was not cost effective to use dedicated instances.

## challanges

how the last row was identified


challenges faces such as - ec2 to lambda, more than one type of processing, gRPC call, wait for LLM model to respond and creating file and validations around user modifications

# System Stabilization

# Repartition


# Migration Framework

# Moving Odata to snowflake


# dp-reporting-service



# Odata API optimization
whenever a API calls hits our server, based on certain configuration and tier of the customer, we expose data for them so that they can fetch this data.

While, working around those APIs, I identified that intial response time of this API was way too high.

While, if we look at the high level, this was just checking db configuratin to know that what all is enabled for 
this user. So, I was curious and started to take a look at my own pase.

I identfied that in application layer, while checking if user has access to it or not, they were making small small but a lots of call to db. So, I decied to go with caching implementation and implemented it using redis.

If any update happens in db, cache will be invalidated and newere data will be served.

We deployed this as a local cache for each server.

