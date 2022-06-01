# microservices  

## System architecture
![system architecture](https://github.com/lizhouyu/microservices/docs/system architecture.png)  
The server side code is in the "server_side" folder.  
The client side script is in the "client_side" folder.  
The data processing scipt is in the "data_process" folder.


## todo list
- [ ] build a "number of GPUs-number of clients-computational time cost" model
    - [x] pre-test: investigate the general trend ![pre-test](https://github.com/lizhouyu/microservices/microservice_data_process/experiment/gpu/pre-test/detection_time.png)
    - [x] small data test: average result for small amount of data ![small data](https://github.com/lizhouyu/microservices/microservice_data_process/experiment/gpu/avg_results/regression.png)
    - [ ] number of GPUs v.s. computational time cost
    - [ ] number of clients v.s. computational time cost