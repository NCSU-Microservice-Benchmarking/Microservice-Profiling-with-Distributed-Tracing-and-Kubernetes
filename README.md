# microservices  

## System architecture
![system architecture](docs/system_architecture.png)  
The server side code is in the "server_side" folder.  
The client side script is in the "client_side" folder.  
The data processing scipt is in the "data_process" folder.


## todo list
- [ ] build a "number of GPUs-number of clients-computational time cost" model
    - [x] pre-test: investigate the general trend  
    ![pre-test](data_process/experiment/gpu/pre-test/detection_time.png)
    - [x] small data test: average result for small amount of data  
    ![small data](data_process/experiment/gpu/avg_results/regression.png)
    - [ ] number of GPUs v.s. computational time cost
    - [ ] number of clients v.s. computational time cost